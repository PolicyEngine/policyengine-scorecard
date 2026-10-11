"""Certified replay variants: exact validation, support and namespaces.

Engine-free and dataset-free: installed distributions are synthesised as
dist-info directories, simulations are stubbed, and the dataset is a few
bytes with a known digest.
"""

import base64
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compute_uk_event as compute
from pipeline import stage_uk_event as stage
from pipeline import uk_replay_variants as rv

LEGACY = "pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z"
CURRENT = "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0"


def record(variant_id=CURRENT):
    return copy.deepcopy(rv.get_variant(variant_id))


def reseal(r):
    """Recompute a mutated record's own identity fields, so only the
    consistency rule under test can refuse it."""
    r["identity_sha256"] = rv.identity_sha256(r["identity"])
    r["variant_id"] = rv.variant_slug(r["identity"])
    if r["layout"] == "replay_namespace":
        r["result_root"] = f"{rv.REPLAY_RESULT_ROOT}/{r['variant_id']}"
    return r


def test_committed_variants_validate_and_default_is_legacy():
    document = rv.load_document()
    assert document["default_variant"] == LEGACY
    assert {v["variant_id"] for v in document["variants"]} == {LEGACY, CURRENT}
    for variant in document["variants"]:
        rv.validate_record(variant)
    assert rv.is_legacy(rv.get_variant())
    assert not rv.is_legacy(rv.get_variant(CURRENT))
    with pytest.raises(rv.VariantError, match="no certified replay variant"):
        rv.get_variant("pe9.9.9_uk9.9.9_unknown")


def test_identity_bytes_equal_rfc8785_for_committed_identities():
    rfc8785 = pytest.importorskip("rfc8785")
    for variant in rv.load_document()["variants"]:
        assert rv.canonical_identity_bytes(variant["identity"]) == rfc8785.dumps(
            variant["identity"]
        )


INCONSISTENT = [
    (
        "model version",
        lambda r: r["identity"]["release_bundle"].update(model_version="2.126.8"),
    ),
    (
        "wrapper version",
        lambda r: r["identity"]["release_bundle"].update(policyengine_version="6.2.7"),
    ),
    (
        "model package",
        lambda r: r["identity"]["release_bundle"].update(
            model_package="policyengine-us"
        ),
    ),
    (
        "artifact digest",
        lambda r: r["identity"]["release_bundle"].update(
            certified_data_artifact_sha256="0" * 64
        ),
    ),
    (
        "dataset uri",
        lambda r: r["identity"]["release_bundle"].update(
            default_dataset_uri="hf://x/y.h5@1"
        ),
    ),
    ("dataset bytes", lambda r: r["identity"]["dataset"].update(sha256="1" * 64)),
    ("dataset size", lambda r: r["identity"]["dataset"].update(size_bytes=0)),
    (
        "certified model",
        lambda r: r["certification"].update(certified_for_model_version="2.125.0"),
    ),
    (
        "certified build",
        lambda r: r["certification"].update(
            data_build_id="policyengine-uk-data-1.57.0"
        ),
    ),
    (
        "basis",
        lambda r: r["certification"].update(
            compatibility_basis="exact_build_model_version"
        ),
    ),
    ("materialization", lambda r: r["identity"].update(materialization="download")),
    ("python", lambda r: r["identity"].update(python="3")),
    ("status", lambda r: r.update(status="promoted")),
    ("executor", lambda r: r.update(executor=["kubernetes"])),
    ("data years gap", lambda r: r.update(data_years=[2024, 2026])),
    ("data years empty", lambda r: r.update(data_years=[])),
    ("requirements bytes", lambda r: r["requirements"].update(sha256="2" * 64)),
    (
        "requirements file",
        lambda r: r["requirements"].update(path="docs/uk_replay/nope.txt"),
    ),
    (
        "installed hash",
        lambda r: r["identity"]["packages"]["policyengine-uk"].update(
            record_sha256="short"
        ),
    ),
    (
        "extra package",
        lambda r: r["identity"]["packages"].update(
            {"policyengine-us": {"version": "1", "record_sha256": "3" * 64}}
        ),
    ),
    ("result root", lambda r: r.update(result_root="results/uk/events")),
]


@pytest.mark.parametrize("label,mutate", INCONSISTENT, ids=[x[0] for x in INCONSISTENT])
def test_each_inconsistent_record_is_refused(label, mutate):
    r = record()
    mutate(r)
    if label != "result root":
        reseal(r)
    with pytest.raises(rv.VariantError):
        rv.validate_record(r)


def test_identity_tampering_is_refused_without_resealing():
    r = record()
    r["identity"]["packages"]["policyengine-uk"]["record_sha256"] = "4" * 64
    with pytest.raises(rv.VariantError, match="identity_sha256"):
        rv.validate_record(r)
    r = record()
    r["variant_id"] = "pe6.2.6_uk2.125.1_other-data"
    with pytest.raises(rv.VariantError, match="variant_id"):
        rv.validate_record(r)


def test_legacy_record_must_agree_with_certified_bundle(tmp_path):
    for relative in (
        "docs/uk_replay/requirements.txt",
        "data/uk/certified_bundle.json",
    ):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_bytes((rv.ROOT / relative).read_bytes())
    rv.validate_record(record(LEGACY), root=tmp_path)
    pinned = json.loads((tmp_path / "data/uk/certified_bundle.json").read_text())
    pinned["compatible_model_packages"][0]["specifier"] = "==2.90.0"
    (tmp_path / "data/uk/certified_bundle.json").write_text(json.dumps(pinned))
    with pytest.raises(rv.VariantError, match="does not declare this model"):
        rv.validate_record(record(LEGACY), root=tmp_path)


def installed_for(r):
    identity = r["identity"]
    return {
        "packages": {
            name: {
                "version": identity["packages"][name]["version"],
                "record_sha256": identity["packages"][name]["record_sha256"],
            }
            for name in rv.PACKAGES
        },
        "packaged_bundle_manifest_sha256": identity["packaged_bundle_manifest_sha256"],
        "python": identity["python"],
        "distributions": rv.requirements_pins(
            (rv.ROOT / r["requirements"]["path"]).read_text()
        ),
    }


def test_every_pinned_distribution_is_part_of_the_installed_check():
    r = record()
    exact = installed_for(r)
    for name in ("numpy", "pandas", "h5py"):
        changed = copy.deepcopy(exact)
        changed["distributions"][name] = "0.0.0"
        with pytest.raises(rv.VariantError, match=name):
            rv.verify_installed(r, installed=changed)
        missing = copy.deepcopy(exact)
        del missing["distributions"][name]
        with pytest.raises(rv.VariantError, match=name):
            rv.verify_installed(r, installed=missing)
    extra = copy.deepcopy(exact)
    extra["distributions"]["rfc8785"] = "0.1.4"
    rv.verify_installed(r, installed=extra)


def test_the_identity_binds_the_requirements_freeze():
    r = record()
    r["identity"]["requirements_sha256"] = "5" * 64
    reseal(r)
    with pytest.raises(rv.VariantError, match="another requirements file"):
        rv.validate_record(r)


def test_installed_environment_must_match_every_field():
    r = record()
    exact = installed_for(r)
    assert rv.verify_installed(r, installed=exact) == exact
    mutations = []
    for name in rv.PACKAGES:
        for field in ("version", "record_sha256"):
            mutations.append(("packages", name, field))
    mutations += [("packaged_bundle_manifest_sha256",), ("python",)]
    for path in mutations:
        changed = copy.deepcopy(exact)
        node = changed
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = "different"
        with pytest.raises(rv.VariantError, match="not the certified one"):
            rv.verify_installed(r, installed=changed)


def test_one_environment_never_validates_two_variants():
    current, legacy = record(CURRENT), record(LEGACY)
    assert rv.identity_mismatches(legacy, installed_for(current))
    assert rv.identity_mismatches(current, installed_for(legacy))


def write_distribution(site: Path, files: dict[str, bytes], installer: bytes):
    info = site / "demo-1.0.dist-info"
    info.mkdir(parents=True)
    rows = []
    for relative, payload in {
        **files,
        "demo-1.0.dist-info/INSTALLER": installer,
    }.items():
        path = site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=")
        rows.append(f"{relative},sha256={digest.decode()},{len(payload)}")
    rows += ["demo-1.0.dist-info/RECORD,,", "demo/__pycache__/x.cpython-312.pyc,,"]
    (info / "METADATA").write_text("Metadata-Version: 2.1\nName: demo\nVersion: 1.0\n")
    (info / "RECORD").write_text("\n".join(rows) + "\n")
    return importlib.metadata.PathDistribution(info)


def test_record_digest_binds_wheel_files_not_the_installer(tmp_path):
    files = {"demo/__init__.py": b"x = 1\n", "demo/data/manifest.json": b"{}"}
    pip = write_distribution(tmp_path / "pip", files, b"pip\n")
    uv = write_distribution(tmp_path / "uv", files, b"uv\n")
    assert rv.distribution_record_sha256(pip) == rv.distribution_record_sha256(uv)
    other = write_distribution(
        tmp_path / "other", {**files, "demo/__init__.py": b"x = 2\n"}, b"uv\n"
    )
    assert rv.distribution_record_sha256(other) != rv.distribution_record_sha256(uv)
    (tmp_path / "uv" / "demo" / "__init__.py").write_bytes(b"x = 3\n")
    with pytest.raises(rv.VariantError, match="differs from its wheel RECORD"):
        rv.distribution_record_sha256(uv)


def test_certification_is_isolated_from_tokens():
    environ = {"HF_TOKEN": "secret", "HUGGING_FACE_TOKEN": "secret", "PATH": "/bin"}
    removed = rv.isolate_certification_environment(environ)
    assert sorted(removed) == ["HF_TOKEN", "HUGGING_FACE_TOKEN"]
    assert not set(rv.TOKEN_VARIABLES) & set(environ)
    assert environ["HF_HUB_OFFLINE"] == "1" and environ["PATH"] == "/bin"


def test_release_bundle_must_match_exactly():
    r = record()
    bundle = dict(r["identity"]["release_bundle"])
    rv.verify_release_bundle(r, bundle)
    for change in (
        {"compatibility_basis": "exact_build_model_version"},
        {"model_version": "2.126.8"},
        {"extra": "field"},
    ):
        with pytest.raises(rv.VariantError, match="runtime release bundle differs"):
            rv.verify_release_bundle(r, {**bundle, **change})
    missing = dict(bundle)
    missing.pop("data_build_fingerprint")
    with pytest.raises(rv.VariantError):
        rv.verify_release_bundle(r, missing)


def tiny_variant(payload: bytes):
    r = record()
    r["identity"]["dataset"].update(
        sha256=hashlib.sha256(payload).hexdigest(), size_bytes=len(payload)
    )
    return r


def test_materialisation_copies_only_verified_bytes(tmp_path):
    payload = b"certified bytes"
    r = tiny_variant(payload)
    source = tmp_path / "cache" / "enhanced_frs_2024_25.h5"
    source.parent.mkdir()
    source.write_bytes(payload)
    runtime = tmp_path / "runtime"
    placed = rv.materialize_dataset(r, runtime, source=source)
    assert placed == (runtime / "data" / "enhanced_frs_2024_25.h5").resolve()
    assert placed.read_bytes() == payload
    assert rv.materialize_dataset(r, runtime, source=tmp_path / "absent") == placed
    impostor = tmp_path / "impostor" / "enhanced_frs_2024_25.h5"
    impostor.parent.mkdir()
    impostor.write_bytes(b"other bytes same len")
    placed.unlink()
    with pytest.raises(rv.VariantError, match="no local file holds"):
        rv.materialize_dataset(r, runtime, source=impostor)
    impostor.write_bytes(b"certified bytez")
    with pytest.raises(rv.VariantError, match="no local file holds"):
        rv.materialize_dataset(r, runtime, source=impostor)
    placed.symlink_to(source)
    with pytest.raises(rv.VariantError, match="symlink"):
        rv.materialize_dataset(r, runtime, source=source)
    with pytest.raises(rv.VariantError, match="does not materialise"):
        rv.materialize_dataset(record(LEGACY), runtime, source=source)


def test_materialisation_finds_the_cache_copy_by_digest(tmp_path, monkeypatch):
    payload = b"certified bytes"
    r = tiny_variant(payload)
    hub = tmp_path / "hub"
    snapshots = hub / "models--policyengine--policyengine-uk-data-private" / "snapshots"
    (snapshots / "aaa").mkdir(parents=True)
    (snapshots / "aaa" / "enhanced_frs_2024_25.h5").write_bytes(b"older release")
    (snapshots / "bbb").mkdir()
    (snapshots / "bbb" / "enhanced_frs_2024_25.h5").write_bytes(payload)
    monkeypatch.setenv("HF_HUB_CACHE", str(hub))
    placed = rv.materialize_dataset(r, tmp_path / "runtime")
    assert placed.read_bytes() == payload


@settings(max_examples=200, deadline=None)
@given(
    st.integers(2015, 2035),
    st.integers(0, 10),
    st.sets(st.integers(2010, 2040), min_size=1, max_size=12),
)
def test_supported_year_partition_is_exact(first, span, registry_years):
    r = {"data_years": list(range(first, first + span + 1))}
    supported, unsupported = rv.supported_years(r, registry_years)
    unsupported_years = [row["year"] for row in unsupported]
    assert sorted(supported + unsupported_years) == sorted(registry_years)
    assert not set(supported) & set(unsupported_years)
    assert supported == sorted(supported)
    assert all(first <= year <= first + span for year in supported)
    for row in unsupported:
        assert row["reason"] == (
            "before_data_year" if row["year"] < first else "after_extension_end"
        )


def test_sealed_namespace_refuses_writes(tmp_path):
    namespace = tmp_path / "results" / "uk" / "replays" / CURRENT
    (namespace / "spring_budget_2023").mkdir(parents=True)
    rv.assert_not_sealed(namespace / "spring_budget_2023", root=tmp_path)
    (namespace / rv.RECEIPT_NAME).write_text("{}")
    with pytest.raises(rv.VariantError, match="sealed"):
        rv.assert_not_sealed(namespace / "spring_budget_2023", root=tmp_path)
    with pytest.raises(rv.VariantError, match="sealed"):
        rv.assert_not_sealed(namespace / "spring_budget_2023" / "deeper", root=tmp_path)


def test_variant_years_refuse_an_explicit_unsupported_year():
    r = record()
    registry = {"calendar_years": [2023, 2024, 2025]}
    assert compute.validate_variant_years([], registry, r) == [2024, 2025]
    with pytest.raises(ValueError, match="outside .*data years"):
        compute.validate_variant_years([2023], registry, r)
    with pytest.raises(ValueError, match="supports none"):
        compute.validate_variant_years([], {"calendar_years": [2022, 2023]}, r)
    with pytest.raises(ValueError, match="documented support"):
        compute.validate_variant_years([2026], registry, r)


def measure():
    rows = []
    for fy, tax, benefit in (("2023-24", 90, -20), ("2024-25", 100, -30)):
        rows += [
            {
                "source_row_id": f"tax_{fy}",
                "fy": fy,
                "metric": "revenue_change",
                "tax_head": "Income tax",
                "value_gbp": tax,
            },
            {
                "source_row_id": f"benefit_{fy}",
                "fy": fy,
                "metric": "exchequer_impact",
                "tax_head": "Welfare inside cap",
                "value_gbp": benefit,
            },
        ]
    rows.append(
        {
            "source_row_id": "corporation_2023-24",
            "fy": "2023-24",
            "metric": "revenue_change",
            "tax_head": "Corporation tax",
            "value_gbp": 4,
            "classification": "out_of_household_scope",
        }
    )
    return {
        "measure_key": "test_event__tax_and_benefit",
        "title": "An announcement",
        "computability": "partial",
        "construction": "reversal_on_certified_world",
        "commences_fy": "2023-24",
        "pe_baseline_modifier": {"gov.tax.rate": 0.2},
        "head_variables": ["income_tax", "universal_credit"],
        "heads": [
            {
                "obr_head": "Income tax",
                "pe_variables": ["income_tax"],
                "channel": "tax",
            },
            {
                "obr_head": "Welfare inside cap",
                "pe_variables": ["universal_credit"],
                "channel": "spending",
            },
        ],
        "source_rows": rows,
    }


def simulation(tax, benefit):
    return {
        "aggregates_gbp": {
            "income_tax": float(tax),
            "universal_credit": float(benefit),
        },
        "variable_metadata": {
            "income_tax": {"entity": "person", "definition_period": "year"},
            "universal_credit": {"entity": "benunit", "definition_period": "year"},
        },
        "policyengine_bundle": {
            "model_version": "2.125.1",
            "certified_data_build_id": "policyengine-uk-data-1.58.0",
        },
        "dataset_sha256_before": "a" * 64,
        "dataset_sha256_after": "a" * 64,
        "performance": {"wall_seconds": 1},
    }


def test_variant_run_skips_unsupported_years_and_stages_them_visibly(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    registry_path = tmp_path / "registry.json"
    registry_document = {"calendar_years": [2023, 2024], "measures": [measure()]}
    registry_path.write_text(json.dumps(registry_document))
    monkeypatch.setattr(compute.registry_builder, "validate_registry", lambda d: None)
    monkeypatch.setattr(compute.worlds, "engine_resolver", lambda: lambda p, d: None)
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda: (_ for _ in ()).throw(AssertionError("legacy preflight for a variant")),
    )
    monkeypatch.setattr(
        compute,
        "variant_preflight",
        lambda variant, dataset_source=None: {
            "sha256": "a" * 64,
            "release_bundle": {
                "certified_data_build_id": "policyengine-uk-data-1.58.0"
            },
        },
    )
    years = []

    def fake_run(year, variables, reform, pre):
        years.append(year)
        return simulation(900, 1000) if reform else simulation(1000, 1030)

    monkeypatch.setattr(compute, "run_sim", fake_run)
    output = tmp_path / "results" / "uk" / "replays" / CURRENT / "test_event"
    args = [
        "--event",
        "test_event",
        "--variant",
        CURRENT,
        "--registry",
        str(registry_path),
        "--output-dir",
        str(output),
    ]
    assert compute.main(args) == 0
    assert set(years) == {2024}
    manifest = json.loads((output / "RUN_MANIFEST.json").read_bytes())
    assert manifest["variant_id"] == CURRENT
    assert manifest["variant_identity_sha256"] == record()["identity_sha256"]
    assert manifest["supported_years"] == [2024]
    assert manifest["unsupported_years"] == [
        {"year": 2023, "reason": "before_data_year"}
    ]
    assert manifest["full_event_complete"] is False
    assert manifest["full_supported_grid_complete"] is True
    artifact = json.loads(
        (output / "test_event__tax_and_benefit_2024.json").read_bytes()
    )
    assert artifact["variant_id"] == CURRENT
    rows, tally = stage.stage_event(
        registry_document,
        manifest,
        artifact_dir=output,
        registry_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
    )
    by_id = {row["source_row_id"]: row for row in rows}
    assert by_id["tax_2024-25"]["pe_value"] == 100
    assert by_id["tax_2023-24"]["status"] == "unsupported_on_variant"
    assert by_id["tax_2023-24"]["pe_value"] is None
    assert "2024–2030" in by_id["tax_2023-24"]["reason"]
    assert by_id["corporation_2023-24"]["computability"] == "out_of_household_scope"
    assert by_id["corporation_2023-24"]["status"] == "not_computed"
    assert tally["unsupported_source_rows"] == 2
    assert tally["unsupported_years"] == [2023]
    assert tally["full_supported_grid_complete"] is True
    assert tally["source_rows"] == tally["staged_rows"] == len(rows) == 5
    # Resume within the same variant reuses receipted artifacts.
    years.clear()
    assert compute.main(args + ["--resume"]) == 0
    assert years == []
    # A forged unsupported-year artifact is refused by staging.
    forged = copy.deepcopy(manifest)
    forged["unsupported_years"] = [{"year": 2024, "reason": "before_data_year"}]
    with pytest.raises(ValueError, match="does not support|supported grid"):
        stage.stage_event(
            registry_document,
            forged,
            artifact_dir=output,
            registry_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        )
    other = copy.deepcopy(manifest)
    other["variant_identity_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="variant identity"):
        stage.stage_event(
            registry_document,
            other,
            artifact_dir=output,
            registry_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        )
    (output.parent / rv.RECEIPT_NAME).write_text("{}")
    with pytest.raises(rv.VariantError, match="sealed"):
        compute.main(args + ["--resume"])


def test_dataset_year_guard_refuses_years_without_inputs(monkeypatch, tmp_path):
    from pipeline import compute_uk_obr_costings as fiscal

    data_file = tmp_path / "data.h5"
    data_file.write_bytes(b"x")
    digest = hashlib.sha256(b"x").hexdigest()

    class Sim:
        policyengine_bundle = {
            "certified_data_build_id": "build",
            "runtime_dataset_source": str(data_file),
        }
        tax_benefit_system = type("System", (), {"variables": {"income_tax": None}})()
        dataset = type("Dataset", (), {"years": [2024, 2025]})()

        def calculate(self, name, period):
            import numpy as np

            return np.array([1.0])

    class Uk:
        @staticmethod
        def managed_microsimulation(**kwargs):
            return Sim()

    import sys
    import types

    monkeypatch.setitem(sys.modules, "policyengine", types.SimpleNamespace(uk=Uk))
    monkeypatch.setattr(fiscal, "variable_metadata", lambda *a, **k: {})
    ok = fiscal.run_managed_simulation(
        year=2024,
        variables=["income_tax"],
        reform=None,
        runtime_dataset_source=data_file,
        expected_dataset_sha256=digest,
    )
    assert ok["aggregates_gbp"] == {"income_tax": 1.0}
    with pytest.raises(RuntimeError, match="outside the simulation dataset's years"):
        fiscal.run_managed_simulation(
            year=2023,
            variables=["income_tax"],
            reform=None,
            runtime_dataset_source=data_file,
            expected_dataset_sha256=digest,
        )
