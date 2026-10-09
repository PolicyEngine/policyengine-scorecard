"""Run the unchanged UK replay CLI in one offline Modal container.

Inspect inputs without a provider call::

    python3 -m pipeline.modal_uk_event --event autumn_budget_2024 --plan

Provider execution needs a separate Python 3.12 control environment::

    UV_CACHE_DIR=.venv-uv-cache uv venv --python 3.12.14 .venv-replay-checks/modal-control
    UV_CACHE_DIR=.venv-uv-cache uv pip install \
        --python .venv-replay-checks/modal-control/bin/python 'modal==1.3.2'

After reviewing that plan, verify the remote environment without simulation::

    .venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_event \
        --event autumn_budget_2024 \
        --preflight-only --output-dir .venv-replay-checks/modal/ab24/preflight \
        --download-root .venv-replay-checks/modal-downloads/preflight --execute

A focused simulation uses --measures and --years. A full event uses its
canonical remote output directory by default, but downloads always land below
an ignored local prefix. This wrapper never writes local canonical results.
Build-time installation can use the package index; the function's runtime
network is blocked, and no credential or provider Secret is sent to it.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
REMOTE_ROOT = "/replay"
REMOTE_PYTHON = "/opt/replay-venv/bin/python"
PYTHON_VERSION = "3.12.14"
MODAL_VERSION = "1.3.2"
UV_VERSION = "0.11.7"
HF_COMMIT = "a75a9a831d6b07aaffbd09713f2a1124f5c0f08f"
HF_REPO_CACHE = "datasets--policyengine--populace-uk-private"
HF_CACHE_RELATIVE = ".cache/huggingface/hub"
MAX_RETURN_BYTES = 8 * 1024 * 1024
EVENTS = (
    "autumn_budget_2024",
    "autumn_statement_2023",
    "spring_budget_2024",
    "spring_statement_2025",
    "spring_budget_2023",
)
ENGINE_PINS = {
    "policyengine": "5.0.2",
    "policyengine-core": "3.27.1",
    "policyengine-uk": "2.89.2",
}
REPOSITORY_FILES = (
    "pipeline/modal_uk_event.py",
    "pipeline/compute_uk_event.py",
    "pipeline/compute_uk_ab2025.py",
    "pipeline/compute_uk_obr_costings.py",
    "pipeline/build_uk_event_registry.py",
    "pipeline/uk_engine_registry.py",
    "data/uk/certified_bundle.json",
    "docs/uk_replay/requirements.txt",
    "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json",
    "sources/uk_replay/source.json",
    "sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz",
)
RESOURCE_LIMITS = {
    "cpu": 2,
    "memory_mib": 32768,
    "timeout_seconds": 3600,
    "max_containers": 1,
    "max_inputs": 1,
    "workers": 1,
    "block_network": True,
}
OFFLINE_ENV = {
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "HF_DATASETS_OFFLINE": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
    "HDF5_USE_FILE_LOCKING": "FALSE",
    "OMP_NUM_THREADS": "2",
    "OPENBLAS_NUM_THREADS": "2",
    "MKL_NUM_THREADS": "2",
    "NUMEXPR_NUM_THREADS": "2",
}


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in value
        or str(path) != value
    ):
        raise ValueError("paths must be normalized relative POSIX paths")
    return value


def repository_files(event: str) -> tuple[str, ...]:
    if event not in EVENTS:
        raise ValueError(f"unsupported fiscal event: {event}")
    return (*REPOSITORY_FILES, f"data/uk/events/{event}_measures.json")


def requirements_pins(text: str) -> dict[str, str]:
    pins = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9_.+!-]+)", line)
        if not match:
            raise ValueError("remote requirements must contain exact package pins only")
        name, version = match.groups()
        name = re.sub(r"[-_.]+", "-", name).lower()
        if name in pins:
            raise ValueError(f"duplicate requirement: {name}")
        pins[name] = version
    if any(pins.get(name) != version for name, version in ENGINE_PINS.items()):
        raise ValueError("requirements do not match the certified engine pins")
    return pins


def certified_pin(root: Path) -> dict:
    cert = json.loads((root / "data/uk/certified_bundle.json").read_bytes())
    audit = json.loads((root / "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json").read_bytes())
    if (
        cert.get("repo_id") != "policyengine/populace-uk-private"
        or cert.get("artifact") != "populace_uk_2023.h5"
        or not re.fullmatch(r"[0-9a-f]{64}", cert.get("sha256", ""))
        or cert.get("size_bytes", 0) <= 0
        or audit["certified_identity"].get("resolved_hf_commit") != HF_COMMIT
        or any(
            audit["certified_identity"].get(key) != cert.get(key)
            for key in ("repo_id", "artifact", "revision", "sha256", "size_bytes")
        )
        or not any(
            row.get("name") == "policyengine-uk" and row.get("specifier") == "==2.89.2"
            for row in cert.get("compatible_model_packages", [])
        )
    ):
        raise ValueError("certified pin differs from the audited offline bundle")
    return cert


def input_manifest(
    event: str, *, root: Path = ROOT, hf_cache: Path | None = None
) -> tuple[dict, dict[str, Path]]:
    """List exact mounts; never traverse a repository or a Hugging Face cache."""
    cert = certified_pin(root)
    requirements_pins((root / "docs/uk_replay/requirements.txt").read_text())
    hf_cache = hf_cache or Path.home() / ".cache/huggingface/hub"
    repo_cache = hf_cache / HF_REPO_CACHE
    ref = repo_cache / "refs" / cert["revision"]
    artifact = repo_cache / "snapshots" / HF_COMMIT / cert["artifact"]
    if ref.read_text().strip() != HF_COMMIT:
        raise ValueError("cached revision does not resolve to the audited HF commit")
    if artifact.stat().st_size != cert["size_bytes"]:
        raise ValueError("cached artifact size differs from the certified bundle")
    mounts = {relative: root / relative for relative in repository_files(event)}
    ref_relative = f"{HF_CACHE_RELATIVE}/{HF_REPO_CACHE}/refs/{cert['revision']}"
    artifact_relative = (
        f"{HF_CACHE_RELATIVE}/{HF_REPO_CACHE}/snapshots/{HF_COMMIT}/{cert['artifact']}"
    )
    # Mount the blob's content directly at the snapshot path; no symlink or
    # unrelated blob, release metadata, refs/main or token file is transmitted.
    mounts[ref_relative] = ref
    mounts[artifact_relative] = artifact.resolve(strict=True)
    rows = []
    for relative, source in sorted(mounts.items()):
        is_artifact = relative == artifact_relative
        if relative in repository_files(event) and not source.resolve().is_relative_to(
            root.resolve()
        ):
            raise ValueError(
                "allowlisted repository input resolves outside the workspace"
            )
        rows.append(
            {
                "path": relative,
                "size_bytes": source.stat().st_size,
                "sha256": cert["sha256"] if is_artifact else sha256_file(source),
                "kind": "certified_artifact" if is_artifact else "input",
            }
        )
    return {
        "schema_version": 1,
        "event": event,
        "certified_bundle": cert,
        "hf_commit": HF_COMMIT,
        "files": rows,
        "artifact_digest_validation": "remote hash before engine import, plus existing managed-loader pre/post simulation checks",
        "resource_limits": RESOURCE_LIMITS,
    }, mounts


def request_spec(
    event: str,
    *,
    years: list[int],
    measures: list[str],
    output_dir: str,
    preflight_only: bool,
) -> dict:
    if event not in EVENTS:
        raise ValueError("unsupported fiscal event")
    output_dir = relative_path(output_dir)
    output = PurePosixPath(output_dir)
    canonical = PurePosixPath("results/uk/events") / event
    ignored = PurePosixPath(".venv-replay-checks/modal")
    if not (output.is_relative_to(canonical) or output.is_relative_to(ignored)):
        raise ValueError(
            "remote output must be event results or the ignored Modal directory"
        )
    if len(years) != len(set(years)) or any(
        year < 2023 or year > 2030 for year in years
    ):
        raise ValueError("years must be unique within 2023–2030")
    if len(measures) != len(set(measures)) or any(
        not re.fullmatch(r"[a-z0-9]+(?:_+[a-z0-9]+)*", key) for key in measures
    ):
        raise ValueError("measures must be unique lowercase slugs")
    return {
        "schema_version": 1,
        "event": event,
        "years": years,
        "measures": measures,
        "output_dir": output_dir,
        "preflight_only": preflight_only,
        "workers": 1,
    }


def validate_selection(request: dict, *, root: Path = ROOT) -> None:
    registry = json.loads(
        (root / f"data/uk/events/{request['event']}_measures.json").read_bytes()
    )
    if registry.get("event_slug", registry.get("event")) != request["event"]:
        raise ValueError("uploaded registry belongs to another fiscal event")
    if set(request["years"]) - set(registry["calendar_years"]):
        raise ValueError("requested years are outside the event's scoring grid")
    known = {measure["measure_key"] for measure in registry["measures"]}
    if set(request["measures"]) - known:
        raise ValueError("requested measure keys are absent from the event registry")


def verify_inputs(manifest: dict, *, root: Path = ROOT) -> None:
    """Check uploaded bytes before importing a country package."""
    cert = certified_pin(root)
    expected = set(repository_files(manifest["event"]))
    expected.add(f"{HF_CACHE_RELATIVE}/{HF_REPO_CACHE}/refs/{cert['revision']}")
    artifact_relative = (
        f"{HF_CACHE_RELATIVE}/{HF_REPO_CACHE}/snapshots/{HF_COMMIT}/{cert['artifact']}"
    )
    expected.add(artifact_relative)
    rows = manifest.get("files", [])
    if (
        manifest.get("schema_version") != 1
        or manifest.get("certified_bundle") != cert
        or manifest.get("hf_commit") != HF_COMMIT
        or manifest.get("resource_limits") != RESOURCE_LIMITS
        or len(rows) != len(expected)
        or {row["path"] for row in rows} != expected
    ):
        raise ValueError("remote input manifest differs from the exact allowlist")
    for row in rows:
        relative_path(row["path"])
        source = root / row["path"]
        if not source.resolve().is_relative_to(root.resolve()):
            raise ValueError("uploaded input escapes the remote root")
        if row["path"] == artifact_relative and (
            row["sha256"] != cert["sha256"] or row["size_bytes"] != cert["size_bytes"]
        ):
            raise ValueError("artifact manifest does not carry the certified digest")
        if (
            source.stat().st_size != row["size_bytes"]
            or sha256_file(source) != row["sha256"]
        ):
            raise ValueError(f"uploaded input differs from its digest: {row['path']}")
    ref = root / HF_CACHE_RELATIVE / HF_REPO_CACHE / "refs" / cert["revision"]
    if ref.read_text().strip() != HF_COMMIT:
        raise ValueError("remote HF revision ref differs from the audited commit")


def verify_runtime(*, root: Path = ROOT) -> dict:
    pins = requirements_pins((root / "docs/uk_replay/requirements.txt").read_text())
    installed = {name: importlib.metadata.version(name) for name in pins}
    if installed != pins or platform.python_version() != PYTHON_VERSION:
        raise ValueError(
            "remote Python or installed requirements differ from the pinned environment"
        )
    audit = json.loads((root / "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json").read_bytes())
    distribution = importlib.metadata.distribution("policyengine")
    packaged_manifest = Path(
        distribution.locate_file("policyengine/data/bundle/manifest.json")
    )
    packaged_sha = sha256_file(packaged_manifest)
    if packaged_sha != audit["packaged_bundle_manifest_sha256"]:
        raise ValueError(
            "installed packaged bundle manifest differs from the offline audit"
        )
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "installed_packages": installed,
        "packaged_bundle_manifest_sha256": packaged_sha,
        "block_network": True,
        "workers": 1,
    }


def run_worker(payload: dict) -> int:
    started = time.perf_counter()
    request = payload["request"]
    if (
        request
        != request_spec(
            request["event"],
            years=request["years"],
            measures=request["measures"],
            output_dir=request["output_dir"],
            preflight_only=request["preflight_only"],
        )
        or payload["inputs"]["event"] != request["event"]
    ):
        raise ValueError("worker request identity is inconsistent")
    for key, value in OFFLINE_ENV.items():
        os.environ[key] = value
    os.environ["HF_HOME"] = str(ROOT / ".cache/huggingface")
    os.environ["HF_HUB_CACHE"] = str(ROOT / HF_CACHE_RELATIVE)
    print("[modal] verifying allowlisted inputs before engine import", flush=True)
    verify_inputs(payload["inputs"])
    validate_selection(request)
    runtime = verify_runtime()
    print("[modal] input hashes and full pinned environment verified", flush=True)
    from pipeline import compute_uk_event as compute

    registry_path, _ = compute.event_paths(request["event"])
    registry = json.loads(registry_path.read_bytes())
    compute.validate_event_identity(registry, request["event"])
    compute.registry_builder.validate_registry(registry)
    compute.validate_years(request["years"], registry)
    output = ROOT / request["output_dir"]
    if output.exists() and any(output.iterdir()):
        raise ValueError("remote output directory already contains files")
    output.mkdir(parents=True, exist_ok=True)
    if request["preflight_only"]:
        print("[modal] starting existing offline managed-bundle preflight", flush=True)
        pre = compute.preflight()
        result = {
            "event": request["event"],
            "computed": False,
            "certified_dataset_sha256": pre["sha256"],
            "data_bundle": compute.fiscal.data_bundle_id(pre["release_bundle"]),
            "release_bundle": pre["release_bundle"],
            "registry_sha256": sha256_file(registry_path),
            "input_manifest_sha256": digest_bytes(canonical_bytes(payload["inputs"])),
            "engine_version": compute.fiscal.package_version("policyengine-uk"),
            **compute.runtime_versions(),
        }
        compute.fiscal.atomic_write_bytes(
            output / "PREFLIGHT.json", canonical_bytes(result)
        )
        print("[modal] existing offline managed-bundle preflight complete", flush=True)
    else:
        argv = [
            "--event",
            request["event"],
            "--output-dir",
            str(output),
            "--workers",
            "1",
        ]
        if request["years"]:
            argv.extend(["--years", *map(str, request["years"])])
        if request["measures"]:
            argv.extend(["--measures", *request["measures"]])
        if compute.main(argv):
            raise RuntimeError("generic replay CLI returned a failure")
    files = {}
    total = 0
    for path in sorted(output.iterdir()):
        if not path.is_file() or not re.fullmatch(r"[A-Za-z0-9_]+\.json", path.name):
            raise ValueError("replay produced an unexpected output file")
        total += path.stat().st_size
        if total > MAX_RETURN_BYTES:
            raise ValueError("replay output exceeds the small-artifact return limit")
        files[str(path.relative_to(ROOT))] = sha256_file(path)
    receipt = {
        "schema_version": 1,
        "runner": "Modal offline Linux; unchanged generic replay CLI",
        "request": request,
        "request_sha256": digest_bytes(canonical_bytes(request)),
        "input_manifest_sha256": digest_bytes(canonical_bytes(payload["inputs"])),
        "files": files,
        "runtime": runtime,
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output / "MODAL_RECEIPT.json").write_bytes(canonical_bytes(receipt))
    return 0


def modal_function(mounts: dict[str, Path]):
    """Construct lazy SDK objects; only main's explicit --execute starts them."""
    if sys.version_info[:2] != (3, 12):
        raise ValueError(
            "Modal provider execution requires a Python 3.12 control interpreter "
            "to match serialized function code; use .venv-replay-checks/modal-control/bin/python"
        )
    import modal

    if importlib.metadata.version("modal") != MODAL_VERSION:
        raise ValueError(f"Modal control SDK must be =={MODAL_VERSION}")
    image = (
        modal.Image.debian_slim(python_version="3.12")
        .pip_install(f"uv=={UV_VERSION}")
        .add_local_file(
            mounts["docs/uk_replay/requirements.txt"],
            "/opt/replay-requirements.txt",
            copy=True,
        )
        .run_commands(
            f"uv python install {PYTHON_VERSION}",
            f"uv venv --python {PYTHON_VERSION} /opt/replay-venv",
            f"uv pip install --python {REMOTE_PYTHON} --requirements /opt/replay-requirements.txt",
        )
        .env(
            {
                **OFFLINE_ENV,
                "PYTHONPATH": REMOTE_ROOT,
                "HF_HOME": f"{REMOTE_ROOT}/.cache/huggingface",
                "HF_HUB_CACHE": f"{REMOTE_ROOT}/{HF_CACHE_RELATIVE}",
            }
        )
    )
    for relative, path in sorted(mounts.items()):
        image = image.add_local_file(path, f"{REMOTE_ROOT}/{relative}", copy=False)
    app = modal.App("scorecard-uk-event-replay", include_source=False)

    @app.function(
        image=image,
        serialized=True,
        include_source=False,
        cpu=(2, 2),
        memory=(32768, 32768),
        timeout=3600,
        max_containers=1,
        retries=0,
        block_network=True,
        restrict_modal_access=True,
    )
    @modal.concurrent(max_inputs=1)
    def replay(payload: dict) -> dict:
        import hashlib
        import json
        import subprocess
        from pathlib import Path

        # Inherit stdout/stderr so Modal streams phase progress as it happens.
        subprocess.run(
            [
                "/opt/replay-venv/bin/python",
                "-m",
                "pipeline.modal_uk_event",
                "--worker-request",
                json.dumps(payload, separators=(",", ":")),
            ],
            cwd="/replay",
            check=True,
        )
        root = Path("/replay")
        output = root / payload["request"]["output_dir"]
        receipt_path = output / "MODAL_RECEIPT.json"
        receipt = json.loads(receipt_path.read_bytes())
        names = [*receipt["files"], str(receipt_path.relative_to(root))]
        files = {}
        total = 0
        for relative in names:
            path = root / relative
            if not path.resolve().is_relative_to(output.resolve()):
                raise ValueError("return path escapes the output directory")
            data = path.read_bytes()
            total += len(data)
            if total > 8 * 1024 * 1024:
                raise ValueError("result exceeds small-artifact return limit")
            files[relative] = {
                "bytes": data,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        return {"files": files}

    return modal, app, replay


def download_prefix(download_root: str, *, root: Path = ROOT) -> Path:
    download_root = relative_path(download_root)
    prefix = root / download_root
    checks = (root / ".venv-replay-checks").resolve()
    if not PurePosixPath(download_root).is_relative_to(".venv-replay-checks"):
        raise ValueError("local downloads must remain under ignored replay checks")
    if not checks.is_relative_to(root.resolve()) or not prefix.resolve().is_relative_to(
        checks
    ):
        raise ValueError("local download directory escapes the workspace checks")
    return prefix


def save_download(
    response: dict, payload: dict, download_root: str, *, root: Path = ROOT
) -> list[str]:
    prefix = download_prefix(download_root, root=root)
    request = payload["request"]
    output = PurePosixPath(request["output_dir"])
    files = response.get("files", {})
    total = 0
    for relative, row in files.items():
        path = PurePosixPath(relative_path(relative))
        if path.parent != output or not re.fullmatch(r"[A-Za-z0-9_]+\.json", path.name):
            raise ValueError("returned file is outside the requested output directory")
        data = row["bytes"]
        total += len(data)
        if total > MAX_RETURN_BYTES or digest_bytes(data) != row["sha256"]:
            raise ValueError("returned file fails its size or SHA-256 receipt")
    receipt_relative = str(output / "MODAL_RECEIPT.json")
    receipt = json.loads(files[receipt_relative]["bytes"])
    if (
        receipt["request"] != request
        or receipt["request_sha256"] != digest_bytes(canonical_bytes(request))
        or receipt["input_manifest_sha256"]
        != digest_bytes(canonical_bytes(payload["inputs"]))
        or receipt["files"]
        != {
            relative: row["sha256"]
            for relative, row in files.items()
            if relative != receipt_relative
        }
    ):
        raise ValueError(
            "returned receipt does not bind the request, inputs and output files"
        )
    paths = [prefix / relative for relative in files]
    for path in paths:
        if not path.resolve().is_relative_to(prefix.resolve()):
            raise ValueError("download destination escapes its ignored prefix")
        if path.exists():
            raise ValueError("download would overwrite an existing local file")
    for relative, row in files.items():
        destination = prefix / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, delete=False
        ) as handle:
            handle.write(row["bytes"])
            temporary = Path(handle.name)
        temporary.replace(destination)
    return [str(path.relative_to(root)) for path in paths]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=EVENTS, default="autumn_budget_2024")
    parser.add_argument("--years", nargs="*", type=int, default=[])
    parser.add_argument("--measures", nargs="*", default=[])
    parser.add_argument("--output-dir")
    parser.add_argument(
        "--download-root", default=".venv-replay-checks/modal-downloads"
    )
    parser.add_argument("--hf-cache", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--plan", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--worker-request", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker_request:
        return run_worker(json.loads(args.worker_request))
    output = args.output_dir or (
        f".venv-replay-checks/modal/{args.event}/preflight"
        if args.preflight_only
        else f"results/uk/events/{args.event}"
    )
    request = request_spec(
        args.event,
        years=args.years,
        measures=args.measures,
        output_dir=output,
        preflight_only=args.preflight_only,
    )
    validate_selection(request)
    inputs, mounts = input_manifest(args.event, hf_cache=args.hf_cache)
    payload = {"request": request, "inputs": inputs}
    prefix = download_prefix(args.download_root)
    if not args.execute:
        print(
            canonical_bytes(
                {**payload, "download_root": args.download_root, "cloud_call": False}
            ).decode(),
            end="",
        )
        return 0
    target = prefix / request["output_dir"]
    if not target.resolve().is_relative_to(prefix.resolve()):
        raise ValueError("download destination escapes its ignored prefix")
    if target.exists() and any(target.iterdir()):
        raise ValueError("choose an empty download prefix before a remote run")
    modal, app, replay = modal_function(mounts)
    with modal.enable_output(), app.run():
        response = replay.remote(payload)
    paths = save_download(response, payload, args.download_root)
    print(
        f"verified and downloaded {len(paths)} small replay files under {args.download_root}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
