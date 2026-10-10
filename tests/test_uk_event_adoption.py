"""Offline validation and mutation guards for canonical event adoption."""

import sys
import types
from pathlib import Path

import pytest

from pipeline import adopt_uk_event as helper_module


@pytest.fixture
def helper():
    return helper_module


@pytest.fixture
def adoption(helper, monkeypatch, tmp_path):
    pin_path = tmp_path / "data/uk/certified_bundle.json"
    pin_path.parent.mkdir(parents=True)
    pin_path.write_bytes(
        (helper.modal_runner.ROOT / "data/uk/certified_bundle.json").read_bytes()
    )
    monkeypatch.setattr(helper, "ROOT", tmp_path)
    monkeypatch.setattr(helper, "current_input_digest", lambda event, bundle: "a" * 64)
    output = "results/uk/events/autumn_budget_2024"
    download = ".venv-replay-checks/download"
    paths = [output + "/measure_2026.json", output + "/RUN_MANIFEST.json"]
    rows = []
    for relative in paths:
        old, new = ("old " + relative).encode(), ("new " + relative).encode()
        destination = tmp_path / relative
        source = tmp_path / download / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(old)
        source.write_bytes(new)
        rows.append(
            {
                "path": relative,
                "old_sha256": helper.modal_runner.digest_bytes(old),
                "new_sha256": helper.modal_runner.digest_bytes(new),
                "changed": True,
            }
        )
    report = {
        "event": "autumn_budget_2024",
        "remote_output": output,
        "download_root": download,
        "full_event_complete": True,
        "input_manifest_sha256": "a" * 64,
        "files": rows,
        "changed_existing_numerical_artifacts": [rows[0]],
    }
    return tmp_path, report


def test_adoption_requires_stopped_run_and_reviewed_numeric_changes(helper, adoption):
    root, report = adoption
    before = (root / report["files"][0]["path"]).read_bytes()
    with pytest.raises(ValueError, match="local event run stopped"):
        helper.adopt(
            report, backup_root=".venv-replay-checks/backup", local_run_stopped=False
        )
    with pytest.raises(ValueError, match="numerical bytes differ"):
        helper.adopt(
            report, backup_root=".venv-replay-checks/backup", local_run_stopped=True
        )
    assert (root / report["files"][0]["path"]).read_bytes() == before
    assert not (root / ".venv-replay-checks/backup").exists()


def test_canonical_drift_after_validation_blocks_all_writes(helper, adoption):
    root, report = adoption
    destination = root / report["files"][0]["path"]
    destination.write_bytes(b"changed since review")
    with pytest.raises(ValueError, match="canonical bytes changed"):
        helper.adopt(
            report,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert destination.read_bytes() == b"changed since review"
    assert not (root / ".venv-replay-checks/backup").exists()


def test_adoption_preserves_originals_and_installs_manifest_last(
    helper, adoption, monkeypatch
):
    root, report = adoption
    before = {row["path"]: (root / row["path"]).read_bytes() for row in report["files"]}
    actual_replace = Path.replace
    replaced = []

    def record_replace(source, destination):
        replaced.append(destination)
        return actual_replace(source, destination)

    monkeypatch.setattr(Path, "replace", record_replace)
    helper.adopt(
        report,
        backup_root=".venv-replay-checks/backup",
        local_run_stopped=True,
        allow_changed_existing=True,
    )
    assert replaced[-1].name == "RUN_MANIFEST.json"
    for relative, original in before.items():
        assert (root / ".venv-replay-checks/backup" / relative).read_bytes() == original
        assert (root / relative).read_bytes() == (
            root / report["download_root"] / relative
        ).read_bytes()


@pytest.fixture
def other_bundle_adoption(helper, adoption):
    root, report = adoption
    key = "development-isolation-fixture"
    pin = helper.uk_bundle.load_bundle(root=root)
    pin["bundle_key"] = key
    pin["development_bundle"] = True
    pin_relative = "data/uk/certified_bundles/development.json"
    (root / pin_relative).parent.mkdir(parents=True)
    (root / pin_relative).write_bytes(helper.modal_runner.canonical_bytes(pin))
    (root / "data/uk/certified_bundles/index.json").write_bytes(
        helper.modal_runner.canonical_bytes(
            {
                "schema_version": 1,
                "default_bundle": helper.uk_bundle.DEFAULT_BUNDLE,
                "bundles": {
                    helper.uk_bundle.DEFAULT_BUNDLE: "data/uk/certified_bundle.json",
                    key: pin_relative,
                },
            }
        )
    )
    original_paths = [row["path"] for row in report["files"]]
    old_output = report["remote_output"]
    output = f"results/uk/events/bundles/{key}/{report['event']}"
    for row in report["files"]:
        old_relative = row["path"]
        new_relative = old_relative.replace(old_output, output)
        for prefix in (root, root / report["download_root"]):
            path = prefix / new_relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((prefix / old_relative).read_bytes())
        row["path"] = new_relative
    report["remote_output"] = output
    report.update(helper.uk_bundle.bundle_identity(key, root=root))
    return root, key, report, original_paths


def test_adoption_isolated_bundle_preserves_default_bytes(
    helper, other_bundle_adoption
):
    root, key, report, default_paths = other_bundle_adoption
    before = {relative: (root / relative).read_bytes() for relative in default_paths}
    helper.adopt(
        report,
        bundle=key,
        backup_root=".venv-replay-checks/backup",
        local_run_stopped=True,
        allow_changed_existing=True,
    )
    assert all(
        (root / relative).read_bytes() == payload
        for relative, payload in before.items()
    )
    assert (root / report["files"][0]["path"]).read_bytes() == (
        root / report["download_root"] / report["files"][0]["path"]
    ).read_bytes()


def test_adoption_rejects_report_from_another_bundle_before_writes(
    helper, other_bundle_adoption
):
    root, _, report, _ = other_bundle_adoption
    with pytest.raises(ValueError, match="bundle identity mismatch"):
        helper.adopt(
            report,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert not (root / ".venv-replay-checks/backup").exists()


def test_adoption_rejects_default_destination_for_other_bundle(
    helper, other_bundle_adoption
):
    root, key, report, _ = other_bundle_adoption
    report["remote_output"] = f"results/uk/events/{report['event']}"
    with pytest.raises(ValueError, match="complete canonical"):
        helper.adopt(
            report,
            bundle=key,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert not (root / ".venv-replay-checks/backup").exists()


def test_download_drift_blocks_all_writes_before_backup(helper, adoption):
    root, report = adoption
    originals = {
        row["path"]: (root / row["path"]).read_bytes() for row in report["files"]
    }
    (root / report["download_root"] / report["files"][-1]["path"]).write_bytes(
        b"changed download"
    )
    with pytest.raises(ValueError, match="download bytes changed"):
        helper.adopt(
            report,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert not (root / ".venv-replay-checks/backup").exists()
    assert all(
        (root / relative).read_bytes() == payload
        for relative, payload in originals.items()
    )


def test_input_drift_after_validation_blocks_adoption(helper, adoption, monkeypatch):
    root, report = adoption
    monkeypatch.setattr(helper, "current_input_digest", lambda event, bundle: "b" * 64)
    with pytest.raises(ValueError, match="inputs changed after validation"):
        helper.adopt(
            report,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert not (root / ".venv-replay-checks/backup").exists()


@pytest.mark.parametrize("change", ["partial", "another_event"])
def test_only_complete_canonical_event_outputs_can_be_adopted(helper, adoption, change):
    root, report = adoption
    if change == "partial":
        report["full_event_complete"] = False
    else:
        report["remote_output"] = "results/uk/events/spring_budget_2024"
    with pytest.raises(ValueError, match="complete canonical"):
        helper.adopt(
            report,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert not (root / ".venv-replay-checks/backup").exists()


@pytest.mark.parametrize(
    "relative",
    [
        "../escape.json",
        "data/uk/certified_bundle.json",
        "results/uk/events/spring_budget_2024/measure.json",
        "results/uk/events/autumn_budget_2024/nested/measure.json",
    ],
)
def test_adoption_rejects_paths_outside_its_event_namespace(helper, adoption, relative):
    root, report = adoption
    report["files"][0]["path"] = relative
    with pytest.raises(ValueError):
        helper.adopt(
            report,
            backup_root=".venv-replay-checks/backup",
            local_run_stopped=True,
            allow_changed_existing=True,
        )
    assert not (root / ".venv-replay-checks/backup").exists()


@pytest.fixture
def downloaded_event(helper, monkeypatch, tmp_path):
    """Real transport and stage validators over a tiny certified fixture."""
    runner = helper.modal_runner
    event = "autumn_budget_2024"
    output = f"results/uk/events/{event}"
    download = ".venv-replay-checks/download"
    directory = tmp_path / download / output
    directory.mkdir(parents=True)
    monkeypatch.setattr(helper, "ROOT", tmp_path)
    monkeypatch.setattr(helper.compute, "ROOT", tmp_path)
    artifact_bytes = b"certified fixture"
    cert = {
        "repo_id": "policyengine/populace-uk-private",
        "artifact": "populace_uk_2023.h5",
        "revision": "fixture-certified-revision",
        "sha256": runner.digest_bytes(artifact_bytes),
        "size_bytes": len(artifact_bytes),
        "compatible_model_packages": [
            {"name": "policyengine-uk", "specifier": "==2.89.2"}
        ],
    }
    audit = {
        "certified_identity": {**cert, "resolved_hf_commit": runner.HF_COMMIT},
        "packaged_bundle_manifest_sha256": "c" * 64,
    }
    for relative in runner.repository_files(event):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"{}")
    (tmp_path / "data/uk/certified_bundles/index.json").write_bytes(
        runner.canonical_bytes(
            {
                "schema_version": 1,
                "default_bundle": runner.DEFAULT_BUNDLE,
                "bundles": {runner.DEFAULT_BUNDLE: "data/uk/certified_bundle.json"},
            }
        )
    )
    (tmp_path / "data/uk/certified_bundle.json").write_bytes(
        runner.canonical_bytes(cert)
    )
    (tmp_path / "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json").write_bytes(
        runner.canonical_bytes(audit)
    )
    (tmp_path / "docs/uk_replay/requirements.txt").write_text(
        "\n".join(f"{name}=={version}" for name, version in runner.ENGINE_PINS.items())
    )
    hf_cache = tmp_path / runner.HF_CACHE_RELATIVE
    cache = hf_cache / runner.HF_REPO_CACHE
    ref = cache / "refs" / cert["revision"]
    h5 = cache / "snapshots" / runner.HF_COMMIT / cert["artifact"]
    ref.parent.mkdir(parents=True)
    h5.parent.mkdir(parents=True)
    ref.write_text(runner.HF_COMMIT)
    h5.write_bytes(artifact_bytes)
    actual_inputs = runner.input_manifest
    monkeypatch.setattr(
        runner,
        "input_manifest",
        lambda event, root, **kwargs: actual_inputs(
            event, root=root, hf_cache=hf_cache, **kwargs
        ),
    )
    source = {
        "source_row_id": "tax",
        "fy": "2026-27",
        "metric": "revenue_change",
        "tax_head": "Income tax",
        "value_gbp": 10.0,
        "value_gbp_decimal": "10.0",
        "classification": "partial",
    }
    measure = {
        "measure_key": f"{event}__tax",
        "title": "A tax change",
        "classification": "partial",
        "computability": "partial",
        "construction": "forward_delta_on_certified_world",
        "pe_reform_delta": {"gov.tax.rate": {"2026": 0.3}},
        "heads": [
            {"obr_head": "Income tax", "pe_variables": ["income_tax"], "channel": "tax"}
        ],
        "source_rows": [source],
        "commences_fy": "2026-27",
        "missing_legs": ["A scope limitation"],
    }
    registry = {
        "event_slug": event,
        "bundle": cert,
        "calendar_years": [2026],
        "measures": [measure],
        "accounting": helper.compute.registry_builder.accounting([source], [measure]),
    }
    registry_path = tmp_path / f"data/uk/events/{event}_measures.json"
    registry_path.write_bytes(runner.canonical_bytes(registry))
    monkeypatch.setattr(
        helper.compute.registry_builder, "source_rows", lambda event: [source]
    )
    versions = {
        "engine_version": "2.89.2",
        "policyengine_version": "5.0.2",
        "policyengine_core_version": "3.27.1",
    }
    artifact = {
        **versions,
        "event": event,
        "measure_key": measure["measure_key"],
        "year": 2026,
        "construction": "forward_delta_on_certified_world",
        "certified_dataset_sha256": cert["sha256"],
        "dataset_sha256_before": cert["sha256"],
        "dataset_sha256_after": cert["sha256"],
        "data_bundle": cert["revision"],
        "head_channels": {"income_tax": "tax"},
        "head_effects": {"income_tax": 10.0},
        "measure_total_gbp": 10.0,
        "literal_reform_minus_baseline": {"income_tax": 10.0},
        "totals": {
            "baseline": {"heads": {"income_tax": 0.0}},
            "reform": {"heads": {"income_tax": 10.0}},
        },
    }
    artifact_relative = f"{output}/{measure['measure_key']}_2026.json"
    pair = {"measure_key": measure["measure_key"], "year": 2026}
    manifest = {
        **versions,
        "event": event,
        "certified_dataset_sha256": cert["sha256"],
        "data_bundle": cert["revision"],
        "years": [2026],
        "measures": [measure["measure_key"]],
        "artifact_grid": [pair],
        "requested_grid": [pair],
        "full_event_grid": [pair],
        "full_event_complete": True,
    }
    request = runner.request_spec(
        event, years=[], measures=[], output_dir=output, preflight_only=False
    )
    receipt = {
        "request": request,
        "request_sha256": runner.digest_bytes(runner.canonical_bytes(request)),
        "runtime": {
            "python": runner.PYTHON_VERSION,
            "installed_packages": runner.ENGINE_PINS,
            "packaged_bundle_manifest_sha256": audit["packaged_bundle_manifest_sha256"],
            "block_network": True,
            "workers": 1,
            "platform": "Linux-fixture",
        },
    }

    def refresh():
        registry_path.write_bytes(runner.canonical_bytes(registry))
        registry_sha = runner.sha256_file(registry_path)
        artifact["registry_sha256"] = registry_sha
        manifest["registry_sha256"] = registry_sha
        (tmp_path / download / artifact_relative).write_bytes(
            runner.canonical_bytes(artifact)
        )
        manifest["artifacts"] = {
            artifact_relative: runner.sha256_file(
                tmp_path / download / artifact_relative
            )
        }
        progress = {
            "schema_version": 1,
            "receipt_kind": "completed_event_artifacts",
            "event": event,
            "year": 2026,
            "registry_sha256": registry_sha,
            "certified_dataset_sha256": cert["sha256"],
            "data_bundle": cert["revision"],
            **versions,
            "artifacts": manifest["artifacts"],
        }
        (directory / "RUN_MANIFEST.json").write_bytes(runner.canonical_bytes(manifest))
        (directory / "RUN_PROGRESS_2026.json").write_bytes(
            runner.canonical_bytes(progress)
        )
        (directory / "RUN_LOG.json").write_bytes(b"{}\n")
        receipt["input_manifest_sha256"] = helper.current_input_digest(event)
        receipt["files"] = {
            str(path.relative_to(tmp_path / download)): runner.sha256_file(path)
            for path in directory.iterdir()
            if path.name != "MODAL_RECEIPT.json"
        }
        (directory / "MODAL_RECEIPT.json").write_bytes(runner.canonical_bytes(receipt))

    refresh()
    return {
        "root": tmp_path,
        "event": event,
        "download": download,
        "directory": directory,
        "registry": registry,
        "manifest": manifest,
        "artifact": artifact,
        "receipt": receipt,
        "refresh": refresh,
    }


def test_read_only_validation_runs_real_inventory_grid_and_orientation_guards(
    helper, downloaded_event
):
    fixture = downloaded_event
    report = helper.validate(fixture["event"], fixture["download"])
    assert report["full_event_complete"]
    assert report["staging_tally"]["computed_measure_years"] == 1
    assert report["staging_tally"]["source_value_gbp_decimal"] == "10.0"
    assert not (fixture["root"] / "results").exists()


def test_validation_tolerates_an_engine_imported_before_it_runs(
    helper, downloaded_event, monkeypatch
):
    """A full suite in an engine-equipped venv imports policyengine first."""
    fixture = downloaded_event
    monkeypatch.setitem(
        sys.modules, "policyengine_preloaded_elsewhere", types.ModuleType("x")
    )
    report = helper.validate(fixture["event"], fixture["download"])
    assert report["full_event_complete"]


def test_validation_rejects_an_engine_imported_during_validation(
    helper, downloaded_event, monkeypatch
):
    fixture = downloaded_event
    read_json = helper.read_json

    def read_json_importing_engine(path):
        monkeypatch.setitem(
            sys.modules, "policyengine_imported_by_validation", types.ModuleType("x")
        )
        return read_json(path)

    monkeypatch.setattr(helper, "read_json", read_json_importing_engine)
    with pytest.raises(AssertionError, match="unexpectedly imported an engine"):
        helper.validate(fixture["event"], fixture["download"])


def test_validation_rejects_changed_current_allowlisted_input(helper, downloaded_event):
    fixture = downloaded_event
    (fixture["root"] / "pipeline/compute_uk_event.py").write_bytes(b"different inputs")
    with pytest.raises(ValueError, match="current allowlisted inputs"):
        helper.validate(fixture["event"], fixture["download"])


def test_validation_rejects_falsely_complete_grid_even_with_valid_hashes(
    helper, downloaded_event
):
    fixture = downloaded_event
    fixture["registry"]["calendar_years"].append(2027)
    second = {
        "measure_key": fixture["registry"]["measures"][0]["measure_key"],
        "year": 2027,
    }
    fixture["manifest"]["full_event_grid"].append(second)
    fixture["manifest"]["requested_grid"].append(second)
    fixture["refresh"]()
    with pytest.raises(ValueError, match="missing requested measure/year"):
        helper.validate(fixture["event"], fixture["download"])


def test_validation_rejects_missing_explicit_grid_commitments(helper, downloaded_event):
    fixture = downloaded_event
    fixture["manifest"].pop("artifact_grid")
    fixture["refresh"]()
    with pytest.raises(ValueError, match="explicit event-grid commitments"):
        helper.validate(fixture["event"], fixture["download"])


def test_validation_rejects_uncertified_post_simulation_digest(
    helper, downloaded_event
):
    fixture = downloaded_event
    fixture["artifact"]["dataset_sha256_after"] = "f" * 64
    fixture["refresh"]()
    with pytest.raises(ValueError, match="certified file identity"):
        helper.validate(fixture["event"], fixture["download"])


def test_validation_rejects_unreceipted_output_files(helper, downloaded_event):
    fixture = downloaded_event
    (fixture["directory"] / "uncommitted.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="missing or unreceipted files"):
        helper.validate(fixture["event"], fixture["download"])


@pytest.mark.parametrize("target", ["request", "manifest", "artifact"])
def test_validation_rejects_foreign_bundle_receipts(helper, downloaded_event, target):
    fixture = downloaded_event
    if target == "request":
        fixture["receipt"]["request"]["bundle_key"] = "foreign-bundle"
        fixture["receipt"]["request_sha256"] = helper.modal_runner.digest_bytes(
            helper.modal_runner.canonical_bytes(fixture["receipt"]["request"])
        )
    else:
        fixture[target]["bundle_key"] = "foreign-bundle"
    fixture["refresh"]()
    with pytest.raises(ValueError, match="identity"):
        helper.validate(fixture["event"], fixture["download"])
