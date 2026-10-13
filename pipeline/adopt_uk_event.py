"""Verify a downloaded Modal event, then optionally adopt it after review.

This engine-free helper starts no simulation and makes no provider call. Execute
with .venv-replay/bin/python and PYTHONPATH=. so shared staging validators are
available. The default is read-only; --adopt requires a full canonical grid,
an explicit --local-run-stopped assertion, and preserves replaced bytes in an
ignored backup. RUN_MANIFEST is installed last.
"""

import argparse
import json
import math
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath

from pipeline import compute_uk_event as compute
from pipeline import modal_uk_event as modal_runner
from pipeline import stage_uk_event as stage

ROOT = modal_runner.ROOT


def read_json(path):
    def reject(value):
        raise ValueError(f"non-finite JSON literal: {value}")

    return json.loads(path.read_bytes(), parse_constant=reject)


def current_input_digest(event):
    inputs, _ = modal_runner.input_manifest(event, root=ROOT)
    return modal_runner.digest_bytes(modal_runner.canonical_bytes(inputs))


def validate(event, download_root, remote_output=None, allow_partial=False):
    prefix = modal_runner.download_prefix(download_root, root=ROOT)
    remote_output = remote_output or f"results/uk/events/{event}"
    modal_runner.relative_path(remote_output)
    directory = prefix / remote_output
    if not directory.resolve().is_relative_to(prefix.resolve()):
        raise ValueError("downloaded directory escapes its ignored prefix")
    receipt_path = directory / "MODAL_RECEIPT.json"
    receipt = read_json(receipt_path)
    request = receipt["request"]
    expected_request = modal_runner.request_spec(
        event,
        years=request["years"],
        measures=request["measures"],
        output_dir=remote_output,
        preflight_only=False,
    )
    if request != expected_request or receipt[
        "request_sha256"
    ] != modal_runner.digest_bytes(modal_runner.canonical_bytes(request)):
        raise ValueError("Modal request identity does not match this adoption")
    modal_runner.validate_selection(request, root=ROOT)
    if receipt["input_manifest_sha256"] != current_input_digest(event):
        raise ValueError(
            "Modal input commitment differs from current allowlisted inputs"
        )
    runtime = receipt["runtime"]
    pins = modal_runner.requirements_pins(
        (ROOT / "docs/uk_replay/requirements.txt").read_text()
    )
    audit = read_json(ROOT / "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json")
    if (
        runtime["python"] != modal_runner.PYTHON_VERSION
        or runtime["installed_packages"] != pins
        or runtime["packaged_bundle_manifest_sha256"]
        != audit["packaged_bundle_manifest_sha256"]
        or runtime.get("block_network") is not True
        or runtime.get("workers") != 1
        or not runtime["platform"].startswith("Linux")
    ):
        raise ValueError("remote runtime does not match the pinned offline environment")
    actual_paths = {
        str(path.relative_to(prefix)) for path in directory.iterdir() if path.is_file()
    }
    expected_paths = {*receipt["files"], f"{remote_output}/MODAL_RECEIPT.json"}
    if actual_paths != expected_paths or any(
        not path.is_file() for path in directory.iterdir()
    ):
        raise ValueError("download directory contains missing or unreceipted files")
    for relative, digest in receipt["files"].items():
        modal_runner.relative_path(relative)
        path = prefix / relative
        if path.parent != directory or not path.resolve().is_relative_to(
            directory.resolve()
        ):
            raise ValueError("Modal receipt names a file outside this output directory")
        if modal_runner.sha256_file(path) != digest:
            raise ValueError(f"download SHA differs from Modal receipt: {relative}")
        read_json(path)
    manifest = read_json(directory / "RUN_MANIFEST.json")
    if (
        not {
            "artifact_grid",
            "requested_grid",
            "full_event_grid",
            "full_event_complete",
        }
        <= manifest.keys()
    ):
        raise ValueError("compute manifest lacks explicit event-grid commitments")
    registry_path, _ = compute.event_paths(event)
    registry = read_json(registry_path)
    compute.registry_builder.validate_registry(registry)
    registry_sha = modal_runner.sha256_file(registry_path)
    cert = modal_runner.certified_pin(ROOT)
    versions = {
        "engine_version": pins["policyengine-uk"],
        "policyengine_version": pins["policyengine"],
        "policyengine_core_version": pins["policyengine-core"],
    }
    if (
        manifest["event"] != event
        or manifest["registry_sha256"] != registry_sha
        or manifest["certified_dataset_sha256"] != cert["sha256"]
        or manifest["data_bundle"] != cert["revision"]
        or any(manifest.get(key) != value for key, value in versions.items())
    ):
        raise ValueError(
            "compute manifest identity does not match the certified registry/runtime"
        )
    for relative, digest in manifest["artifacts"].items():
        if receipt["files"].get(relative) != digest:
            raise ValueError("compute and Modal artifact commitments disagree")
        artifact = read_json(prefix / relative)
        if any(artifact.get(key) != value for key, value in versions.items()):
            raise ValueError("numerical artifact uses another engine runtime")
        if not math.isfinite(artifact["measure_total_gbp"]):
            raise ValueError("non-finite numerical total")
        if (
            artifact.get("dataset_sha256_before") != cert["sha256"]
            or artifact.get("dataset_sha256_after") != cert["sha256"]
            or artifact.get("data_bundle") != cert["revision"]
        ):
            raise ValueError(
                "numerical artifact does not retain the certified file identity"
            )
    original_root = compute.ROOT
    try:
        # Reuse the actual stage/grid/orientation/accounting validators while
        # resolving untouched canonical receipt paths inside the download.
        compute.ROOT = prefix
        _, tally = stage.stage_event(
            registry, manifest, artifact_dir=directory, registry_sha256=registry_sha
        )
    finally:
        compute.ROOT = original_root
    if manifest["full_event_complete"] != tally["full_event_complete"]:
        raise ValueError("compute manifest completeness differs from the staged grid")
    if not allow_partial and not tally["full_event_complete"]:
        raise ValueError("a partial replay cannot be adopted as a completed event")
    for year in manifest["years"]:
        progress = read_json(directory / f"RUN_PROGRESS_{year}.json")
        expected_artifacts = {
            relative: digest
            for relative, digest in manifest["artifacts"].items()
            if read_json(prefix / relative)["year"] == year
        }
        expected_progress = {
            "schema_version": 1,
            "receipt_kind": "completed_event_artifacts",
            "event": event,
            "year": year,
            "registry_sha256": registry_sha,
            "certified_dataset_sha256": cert["sha256"],
            "data_bundle": cert["revision"],
            **versions,
            "artifacts": expected_artifacts,
        }
        if progress != expected_progress:
            raise ValueError(
                "per-year progress does not match final artifacts and runtime"
            )
    changes = []
    for relative in sorted(expected_paths):
        destination = ROOT / relative
        source = prefix / relative
        new_sha = modal_runner.sha256_file(source)
        old_sha = (
            modal_runner.sha256_file(destination) if destination.is_file() else None
        )
        changes.append(
            {
                "path": relative,
                "old_sha256": old_sha,
                "new_sha256": new_sha,
                "changed": old_sha is not None and old_sha != new_sha,
            }
        )
    numerical_changes = [
        row
        for row in changes
        if row["changed"] and row["path"] in manifest["artifacts"]
    ]
    for row in numerical_changes:
        old, new = read_json(ROOT / row["path"]), read_json(prefix / row["path"])
        row["changed_top_level_fields"] = sorted(
            key for key in old.keys() | new.keys() if old.get(key) != new.get(key)
        )
        row["head_effects_equal"] = old["head_effects"] == new["head_effects"]
        row["measure_total_equal"] = (
            old["measure_total_gbp"] == new["measure_total_gbp"]
        )
        row["old_head_effects"] = old["head_effects"]
        row["new_head_effects"] = new["head_effects"]
    if any(name.startswith("policyengine") for name in sys.modules):
        raise AssertionError("validation unexpectedly imported an engine")
    return {
        "event": event,
        "download_root": download_root,
        "remote_output": remote_output,
        "input_manifest_sha256": receipt["input_manifest_sha256"],
        "modal_receipt_sha256": modal_runner.sha256_file(receipt_path),
        "full_event_complete": manifest["full_event_complete"],
        "staging_tally": tally,
        "files": changes,
        "changed_existing_numerical_artifacts": numerical_changes,
    }


def adopt(report, *, backup_root, local_run_stopped, allow_changed_existing=False):
    event = report["event"]
    if not local_run_stopped:
        raise ValueError(
            "adoption requires explicit confirmation that the local event run stopped"
        )
    if (
        not report["full_event_complete"]
        or report["remote_output"] != f"results/uk/events/{event}"
    ):
        raise ValueError("only a complete canonical remote output can be adopted")
    if report["changed_existing_numerical_artifacts"] and not allow_changed_existing:
        raise ValueError(
            "existing numerical bytes differ; review the report before authorizing replacement"
        )
    if report["input_manifest_sha256"] != current_input_digest(event):
        raise ValueError("allowlisted inputs changed after validation")
    expected_directory = PurePosixPath(report["remote_output"])
    paths = [row["path"] for row in report["files"]]
    if (
        len(paths) != len(set(paths))
        or f"{expected_directory}/RUN_MANIFEST.json" not in paths
    ):
        raise ValueError("adoption report repeats files or lacks the compute manifest")
    for relative in paths:
        modal_runner.relative_path(relative)
        path = PurePosixPath(relative)
        if path.parent != expected_directory or not re.fullmatch(
            r"[A-Za-z0-9_]+\.json", path.name
        ):
            raise ValueError("adoption report names a file outside its event namespace")
    backup = modal_runner.download_prefix(backup_root, root=ROOT)
    if backup.exists() and any(backup.iterdir()):
        raise ValueError("backup prefix must be empty")
    prefix = modal_runner.download_prefix(report["download_root"], root=ROOT)
    if (
        backup.resolve() == prefix.resolve()
        or backup.resolve().is_relative_to(prefix.resolve())
        or prefix.resolve().is_relative_to(backup.resolve())
    ):
        raise ValueError("backup and download prefixes must be separate")
    ordered = sorted(
        report["files"],
        key=lambda row: (row["path"].endswith("/RUN_MANIFEST.json"), row["path"]),
    )
    # Recheck all source and destination commitments before the first write.
    for row in ordered:
        source, destination = prefix / row["path"], ROOT / row["path"]
        if not source.resolve().is_relative_to(
            (prefix / report["remote_output"]).resolve()
        ):
            raise ValueError("download source escapes this event's output directory")
        if not destination.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("canonical destination escapes workspace")
        if modal_runner.sha256_file(source) != row["new_sha256"]:
            raise ValueError("download bytes changed after validation")
        actual = (
            modal_runner.sha256_file(destination) if destination.is_file() else None
        )
        if actual != row["old_sha256"]:
            raise ValueError("canonical bytes changed after validation")
    backup.mkdir(parents=True, exist_ok=True)
    for row in ordered:
        source, destination = prefix / row["path"], ROOT / row["path"]
        if destination.is_file():
            original = backup / row["path"]
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(destination, original)
        if row["old_sha256"] == row["new_sha256"]:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, delete=False
        ) as handle:
            handle.write(source.read_bytes())
            temporary = Path(handle.name)
        temporary.replace(destination)
    (backup / "ADOPTION.json").write_bytes(modal_runner.canonical_bytes(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", default="autumn_budget_2024")
    parser.add_argument("--download-root", required=True)
    parser.add_argument("--remote-output")
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--adopt", action="store_true")
    parser.add_argument("--local-run-stopped", action="store_true")
    parser.add_argument("--allow-changed-existing", action="store_true")
    parser.add_argument(
        "--backup-root", default=".venv-replay-checks/modal-adoption-backup"
    )
    args = parser.parse_args()
    report = validate(
        args.event, args.download_root, args.remote_output, args.allow_partial
    )
    print(modal_runner.canonical_bytes(report).decode(), end="")
    if args.adopt:
        adopt(
            report,
            backup_root=args.backup_root,
            local_run_stopped=args.local_run_stopped,
            allow_changed_existing=args.allow_changed_existing,
        )


if __name__ == "__main__":
    main()
