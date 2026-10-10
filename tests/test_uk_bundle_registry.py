"""Selection and registration invariants without national simulations."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from pipeline.uk_bundle import (
    DEFAULT_BUNDLE,
    ROOT,
    bundle_document,
    bundle_identity,
    bundle_pin_path,
    bundle_window,
    event_output_dir,
    load_bundle,
    registry_path,
    validate_bundle_identity,
    validate_bundle_path,
    validate_registry_bundle,
)
from pipeline.register_uk_certified_bundle import write_registration, _extension_end
from pipeline.export_uk_bundle_requirements import export_requirements


def development_index(tmp_path, monkeypatch):
    pin = load_bundle()
    pin.update(
        bundle_key="development",
        data_year=2024,
        supported_calendar_years=[2024, 2030],
        development_bundle=True,
    )
    pin_path = tmp_path / "development.json"
    index = tmp_path / "index.json"
    write_registration(pin, pin_path, index, root=tmp_path)
    document = json.loads(index.read_text())
    document["bundles"]["development"] = str(pin_path)
    index.write_text(json.dumps(document))
    monkeypatch.setenv("UK_BUNDLE_INDEX", str(index))
    return pin, pin_path


def test_default_pin_bytes_and_paths_stay_historical():
    pin = ROOT / "data/uk/certified_bundle.json"
    assert bundle_pin_path() == pin
    assert bundle_document() == json.loads(pin.read_text())
    assert (
        registry_path("spring_budget_2023")
        == ROOT / "data/uk/events/spring_budget_2023_measures.json"
    )
    assert (
        event_output_dir("spring_budget_2023")
        == ROOT / "results/uk/events/spring_budget_2023"
    )
    assert bundle_window() == (2023, 2030)
    assert load_bundle()["managed_loader_version"] == "5.0.2"


def test_new_bundle_identity_requires_pin_window_and_versions(tmp_path, monkeypatch):
    development_index(tmp_path, monkeypatch)
    identity = bundle_identity("development", root=tmp_path)
    validate_bundle_identity(identity, "development", root=tmp_path)
    for field in identity:
        missing = {name: value for name, value in identity.items() if name != field}
        with pytest.raises(ValueError, match="missing bundle identity"):
            validate_bundle_identity(missing, "development", root=tmp_path)
    assert identity["supported_calendar_years"] == [2024, 2030]


@given(
    st.sampled_from(
        [
            "engine_versions",
            "bundle_key",
            "bundle_pin_sha256",
            "supported_calendar_years",
        ]
    )
)
def test_foreign_default_identity_rejected(field):
    identity = bundle_identity()
    identity[field] = "foreign"
    with pytest.raises(ValueError, match="bundle identity mismatch"):
        validate_bundle_identity(identity)


def test_foreign_pin_registry_and_window_rejected(tmp_path, monkeypatch):
    pin, _ = development_index(tmp_path, monkeypatch)
    identity = bundle_identity("development", root=tmp_path)
    registry = {**identity, "bundle": pin, "calendar_years": [2024, 2030]}
    validate_registry_bundle(registry, "development", root=tmp_path)
    registry["calendar_years"].append(2023)
    with pytest.raises(ValueError, match="outside bundle window"):
        validate_registry_bundle(registry, "development", root=tmp_path)
    registry["calendar_years"] = [2024]
    registry["bundle"]["sha256"] = "different"
    with pytest.raises(ValueError, match="pin differs"):
        validate_registry_bundle(registry, "development", root=tmp_path)


def test_window_change_keeps_source_accounting_once(tmp_path, monkeypatch):
    development_index(tmp_path, monkeypatch)
    from pipeline import build_uk_event_registry as builder

    rows = [
        {
            "source_row_id": f"row-{year}",
            "title": "Business rates: example",
            "fy": f"{year}-{str(year + 1)[-2:]}",
            "tax_head": "Business rates",
            "head_kind": "tax",
            "metric": "revenue_change",
            "value_gbp": year,
            "value_gbp_decimal": str(year),
            "fiscal_event": "Audit Event",
        }
        for year in (2022, 2023, 2024, 2030, 2031)
    ]
    monkeypatch.setattr(builder, "source_rows", lambda event: rows)
    base = builder.build_registry("audit_event", [], [], None)
    new = builder.build_registry("audit_event", [], [], None, "development")
    for name in (
        "rows_in",
        "rows_classified",
        "net_gbp_in_decimal",
        "net_gbp_classified_decimal",
        "absolute_gbp_in_decimal",
        "absolute_gbp_classified_decimal",
        "by_fy",
    ):
        assert base["accounting"][name] == new["accounting"][name]
    assert base["calendar_years"] == [2023, 2024, 2030]
    assert new["calendar_years"] == [2024, 2030]
    staged = [row for measure in new["measures"] for row in measure["source_rows"]]
    assert {
        row["source_row_id"]
        for row in staged
        if row.get("computation_status") == "outside_bundle_window"
    } == {"row-2022", "row-2023", "row-2031"}
    assert len(staged) == len({row["source_row_id"] for row in staged}) == 5


def test_bundle_path_isolation_allows_explicit_dev_receipts():
    for kind, parent in (
        ("registry", "data/uk/events"),
        ("results", "results/uk/events"),
    ):
        with pytest.raises(ValueError, match="another bundle"):
            validate_bundle_path(
                ROOT / parent / "bundles/other/event.json", DEFAULT_BUNDLE, kind=kind
            )
        with pytest.raises(ValueError, match="another bundle"):
            validate_bundle_path(ROOT / parent / "event.json", "other", kind=kind)
        validate_bundle_path(
            ROOT / ".venv-replay-checks/event.json", "other", kind=kind
        )


def test_registration_is_deterministic_and_never_overwrites(tmp_path):
    pin = {"bundle_key": "development", "development_bundle": True, "sha256": "abc"}
    path, index = tmp_path / "pin.json", tmp_path / "index.json"
    write_registration(pin, path, index, root=tmp_path)
    before = path.read_bytes(), index.read_bytes()
    write_registration(pin, path, index, root=tmp_path)
    assert before == (path.read_bytes(), index.read_bytes())
    with pytest.raises(ValueError, match="replace"):
        write_registration({**pin, "sha256": "changed"}, path, index, root=tmp_path)
    with pytest.raises(ValueError, match="production index"):
        write_registration(
            pin, path, tmp_path / "data/uk/certified_bundles/index.json", root=tmp_path
        )


def test_extension_end_is_read_from_code(tmp_path):
    path = tmp_path / "engine.py"
    path.write_text(
        "def extend_single_year_dataset(dataset, tax_benefit_system_parameters, end_year: int = 2032):\n pass\n"
    )
    assert _extension_end(path) == 2032
    path.write_text("def changed_function(): pass\n")
    with pytest.raises(ValueError, match="verify"):
        _extension_end(path)


def test_requirements_export_uses_exact_tag_lock_and_no_cache(tmp_path, monkeypatch):
    from pipeline import export_uk_bundle_requirements as module
    import subprocess

    files = {
        "pyproject.toml": b'[project]\nname="policyengine"\nversion="6.2.5"\n',
        "uv.lock": b"version = 1\n",
        "README.md": b"Release",
    }
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        if command[0] == "git" and command[3] == "show":
            return subprocess.CompletedProcess(
                command, 0, stdout=files[command[-1].split(":")[-1]]
            )
        if command[0] == "git":
            return subprocess.CompletedProcess(command, 0, stdout="a" * 40 + "\n")
        assert (
            "--frozen" in command and "--offline" in command and "--no-cache" in command
        )
        assert (Path(kwargs["cwd"]) / "uv.lock").read_bytes() == files["uv.lock"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="# uv header\npolicyengine-uk==2.102.3\npolicyengine-core==3.32.10\n",
        )

    monkeypatch.setattr(module.subprocess, "run", run)
    freeze, receipt = export_requirements(tmp_path, "6.2.5", "development")
    assert "policyengine==6.2.5\n" in freeze
    assert receipt["uv_lock_sha256"] == hashlib.sha256(files["uv.lock"]).hexdigest()
    assert receipt["freeze_sha256"] == hashlib.sha256(freeze.encode()).hexdigest()


def test_builder_cli_forwards_selected_engine_pin(tmp_path, monkeypatch):
    from pipeline import build_uk_event_registry as builder
    from types import SimpleNamespace
    import importlib.metadata
    import sys

    development_index(tmp_path, monkeypatch)
    system = object()
    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk",
        SimpleNamespace(CountryTaxBenefitSystem=lambda: system),
    )
    expected = bundle_identity("development")["engine_versions"]
    monkeypatch.setattr(importlib.metadata, "version", lambda name: expected[name])
    calls = []
    monkeypatch.setattr(
        builder, "engine_dumps", lambda **kwargs: calls.append(kwargs) or ({}, {})
    )
    monkeypatch.setattr(builder, "engine_resolver", lambda value: None)
    monkeypatch.setattr(
        builder,
        "build_registry",
        lambda *args: {"measures": [], "accounting": {"rows_in": 0, "by_class": {}}},
    )
    output = tmp_path / "registry.json"
    monkeypatch.setattr(builder, "registry_path", lambda *args: output)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_uk_event_registry",
            "--event",
            "audit_event",
            "--bundle",
            "development",
        ],
    )
    builder.main()
    assert calls == [{"pin": expected["policyengine-uk"], "system": system}]


def test_cgt_blended_engine_uses_january_reversal_only_for_new_bundle(
    tmp_path, monkeypatch
):
    development_index(tmp_path, monkeypatch)
    from pipeline import build_uk_event_registry as builder

    row = {
        "source_row_id": "row-2024",
        "title": "Capital Gains Tax: Increase the main rates and reliefs",
        "fy": "2024-25",
        "tax_head": "Capital gains tax",
        "head_kind": "tax",
        "metric": "revenue_change",
        "value_gbp": 1,
        "value_gbp_decimal": "1",
    }
    monkeypatch.setattr(builder, "source_rows", lambda event: [row])

    def resolve(path, date):
        return 0.18

    resolve.parameter_metadata = lambda path: {"fiscal_year_blend": True}
    paths = [f"gov.hmrc.cgt.{rate}_rate" for rate in ("basic", "higher", "additional")]
    new = builder.build_registry(
        "autumn_budget_2024", paths, ["capital_gains_tax"], resolve, "development"
    )["measures"][0]
    base = builder.build_registry(
        "autumn_budget_2024", paths, ["capital_gains_tax"], resolve
    )["measures"][0]
    assert {
        date for schedule in new["pe_baseline_modifier"].values() for date in schedule
    } == {"2024-01-01"}
    assert {
        date for schedule in base["pe_baseline_modifier"].values() for date in schedule
    } == {"2024-10-30"}
    assert (
        new["construction_adjustments"][0]["id"]
        == "cgt_fiscal_year_blend_annual_reversal"
    )
    assert "parameter_processing_evidence" not in base


def test_later_bundle_diagnostics_keep_old_diagnosis_as_reference_only(
    tmp_path, monkeypatch
):
    from pipeline.diagnose_uk_event_models import current_bundle_observation

    original = {
        "id": "cgt_main_rate_commencement",
        "class": "pe_gap",
        "interpretation": "Legacy onset was April 2025.",
        "observation": {"current_rate": 0.18},
        "engine_version": "2.102.3",
    }
    historical = deepcopy(original)
    assert current_bundle_observation(historical, bundle_identity()) == original
    development_index(tmp_path, monkeypatch)
    identity = bundle_identity("development", root=tmp_path)
    current = current_bundle_observation(deepcopy(original), identity)
    assert current["class"] == "bundle_observation"
    assert "Legacy onset was April 2025." not in current["interpretation"]
    assert current["legacy_reference"]["interpretation"] == original["interpretation"]
    assert current["legacy_reference"]["bundle_key"] == DEFAULT_BUNDLE
    assert current["observation"] == original["observation"]
    validate_bundle_identity(current, "development", root=tmp_path)


@pytest.mark.parametrize(
    "conflict",
    [
        None,
        "digest",
        "size",
        "policyengine-uk",
        "policyengine-core",
        "certification",
        "certified_uri",
        "default_uri",
        "artifact_build",
        "certification_build",
        "repo_type",
        "unverified",
        "empty_basis",
    ],
)
def test_registration_checks_packaged_artifact_and_package_pins(
    tmp_path, monkeypatch, conflict
):
    from pipeline import register_uk_certified_bundle as module
    from types import SimpleNamespace

    packages = {
        "policyengine": "6.2.5",
        "policyengine-uk": "2.102.3",
        "policyengine-core": "3.32.10",
    }
    digest = hashlib.sha256(b"certified bytes").hexdigest()
    dataset = {
        "path": "test.h5",
        "sha256": digest,
        "size_bytes": len(b"certified bytes"),
        "revision": "1.56.16",
    }
    build = "policyengine-uk-data-1.56.16"
    uri = "hf://owner/data/test.h5@1.56.16"
    country = {
        "certification": {
            "certified_for_model_version": "2.102.3",
            "compatibility_basis": "legacy_compatible_model_package",
            "data_build_id": build,
        },
        "model_package": {"version": "2.102.3"},
        "policyengine_version": "6.2.5",
        "default_dataset": "test",
        "default_dataset_uri": uri,
        "datasets": {"test": dataset},
        "certified_data_artifact": {
            "dataset": "test",
            "sha256": digest,
            "build_id": build,
            "uri": uri,
        },
        "data_package": {
            "repo_type": "model",
            "repo_id": "owner/data",
            "release_manifest_revision": "b" * 40,
            "release_manifest_path": "release_manifest.json",
        },
        "build_id": build,
    }
    manifest = {
        "packages": {name: {"version": version} for name, version in packages.items()},
        "data_releases": {"uk": country},
    }
    if conflict == "digest":
        dataset["sha256"] = "f" * 64
        country["certified_data_artifact"]["sha256"] = "f" * 64
    if conflict == "size":
        dataset["size_bytes"] += 1
    if conflict == "certification":
        country["certification"]["certified_for_model_version"] = "2.89.2"
    if conflict == "certified_uri":
        country["certified_data_artifact"]["uri"] = "hf://owner/other/test.h5@1.56.16"
    if conflict == "default_uri":
        country["default_dataset_uri"] = "hf://owner/data/test.h5@main"
    if conflict == "artifact_build":
        country["certified_data_artifact"]["build_id"] = "other"
    if conflict == "certification_build":
        country["certification"]["data_build_id"] = "other"
    if conflict == "repo_type":
        country["data_package"]["repo_type"] = "space"
    if conflict == "unverified":
        country["certification"]["compatibility_basis"] = "unverified_local"
    if conflict == "empty_basis":
        country["certification"]["compatibility_basis"] = ""
    manifest_path = tmp_path / "policyengine/data/bundle/manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest))
    repo = tmp_path / "cache/models--owner--data"
    (repo / "refs").mkdir(parents=True)
    (repo / "refs/1.56.16").write_text("a" * 40)
    artifact = repo / "snapshots" / ("a" * 40) / "test.h5"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"certified bytes")
    monkeypatch.setattr(
        module.importlib.metadata,
        "distribution",
        lambda _: SimpleNamespace(locate_file=lambda name: tmp_path / name),
    )
    monkeypatch.setattr(
        module.importlib.metadata,
        "version",
        lambda name: "wrong" if name == conflict else packages[name],
    )
    monkeypatch.setattr(module, "_stored_year", lambda path: 2024)
    monkeypatch.setattr(module, "_extension_end", lambda path: 2030)
    monkeypatch.setattr(
        module,
        "sha256_file",
        lambda path: digest if Path(path) == artifact else "b" * 64,
    )
    arguments = {
        "requirements_freeze": "freeze.txt",
        "offline_audit": "audit.json",
        "cache_root": tmp_path / "cache",
        "development": True,
    }
    if conflict is not None:
        with pytest.raises(ValueError):
            module.inspect_installed_bundle("test", **arguments)
    else:
        pin = module.inspect_installed_bundle("test", **arguments)
        assert pin["data_year"] == 2024
        assert pin["supported_calendar_years"] == [2024, 2030]
        assert pin["compatible_core_packages"] == [
            {"name": "policyengine-core", "specifier": "==3.32.10"}
        ]
