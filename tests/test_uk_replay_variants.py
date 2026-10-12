"""Certified replay variants: exact validation, support and namespaces.

Engine-free and dataset-free: installed distributions are synthesised as
dist-info directories, simulations are stubbed, and the dataset is a few
bytes with a known digest.
"""

import base64
import copy
import hashlib
import importlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compute_uk_event as compute
from pipeline import stage_uk_event as stage
from pipeline import uk_replay_variants as rv

LEGACY = "pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z"
CURRENT = "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0"
DATASET_SHA256 = rv.get_variant(CURRENT)["identity"]["dataset"]["sha256"]


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
    with pytest.raises(rv.VariantError, match="no replay variant"):
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
        "dataset_sha256_before": DATASET_SHA256,
        "dataset_sha256_after": DATASET_SHA256,
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
        lambda *args: (_ for _ in ()).throw(
            AssertionError("legacy preflight for a variant")
        ),
    )
    monkeypatch.setattr(
        compute,
        "variant_preflight",
        lambda variant, dataset_source=None: {
            "sha256": variant["identity"]["dataset"]["sha256"],
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
    with pytest.raises(
        ValueError, match="does not support|supported grid|supported years differ"
    ):
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


# --- review of #160 ------------------------------------------------------------


def staged_variant_run(tmp_path, monkeypatch):
    """A one-measure variant run over CY2023–2024 (2023 unsupported)."""
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    registry_path = tmp_path / "registry.json"
    registry = {"calendar_years": [2023, 2024], "measures": [measure()]}
    registry_path.write_text(json.dumps(registry))
    monkeypatch.setattr(compute.registry_builder, "validate_registry", lambda d: None)
    monkeypatch.setattr(compute.worlds, "engine_resolver", lambda: lambda p, d: None)
    monkeypatch.setattr(
        compute,
        "variant_preflight",
        lambda variant, dataset_source=None: {
            "sha256": variant["identity"]["dataset"]["sha256"],
            "release_bundle": {
                "certified_data_build_id": "policyengine-uk-data-1.58.0"
            },
        },
    )
    monkeypatch.setattr(
        compute,
        "run_sim",
        lambda year, variables, reform, pre: (
            simulation(900, 1000) if reform else simulation(1000, 1030)
        ),
    )
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
    manifest = json.loads((output / "RUN_MANIFEST.json").read_bytes())
    digest = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    return registry, manifest, output, digest, args


@pytest.mark.parametrize(
    "label,forge",
    [
        # B1: a self-consistent manifest that claims 2023 is supported.
        (
            "no unsupported years",
            lambda m: m.update(unsupported_years=[], supported_years=[2023, 2024]),
        ),
        ("other data years", lambda m: m.update(data_years=[2023, 2030])),
        ("other identity", lambda m: m.update(variant_identity_sha256="f" * 64)),
        ("unknown variant", lambda m: m.update(variant_id="pe9_uk9_x")),
        ("other dataset", lambda m: m.update(certified_dataset_sha256="b" * 64)),
        ("other data bundle", lambda m: m.update(data_bundle="another-build")),
        # Deleting variant_id must not turn the identity check off.
        ("variant fields dropped", lambda m: m.pop("variant_id")),
    ],
)
def test_staging_checks_a_manifests_variant_claims_against_the_record(
    tmp_path, monkeypatch, label, forge
):
    registry, manifest, output, digest, _ = staged_variant_run(tmp_path, monkeypatch)
    stage.stage_event(registry, manifest, artifact_dir=output, registry_sha256=digest)
    forged = copy.deepcopy(manifest)
    forge(forged)
    with pytest.raises((ValueError, rv.VariantError)):
        stage.stage_event(registry, forged, artifact_dir=output, registry_sha256=digest)


def test_a_legacy_manifest_lists_no_variant_fields():
    registry = {"calendar_years": [2023], "measures": []}
    for fields in (
        {"unsupported_years": [{"year": 2023, "reason": "before_data_year"}]},
        {"variant_identity_sha256": "a" * 64},
    ):
        with pytest.raises(ValueError, match="legacy compute manifest"):
            stage.manifest_variant(fields, registry, variants_path=rv.VARIANTS_PATH)
    assert stage.manifest_variant({}, registry, variants_path=rv.VARIANTS_PATH) is None


def test_resume_refuses_a_receipt_for_an_unsupported_year(tmp_path, monkeypatch):
    # B2: a receipt (from an older revision, or edited) naming a 2023
    # artifact must not put that year into a variant's manifest.
    registry, manifest, output, digest, args = staged_variant_run(tmp_path, monkeypatch)
    forged = output / "test_event__tax_and_benefit_2023.json"
    forged.write_bytes(
        (output / "test_event__tax_and_benefit_2024.json")
        .read_bytes()
        .replace(b'"year": 2024', b'"year": 2023')
    )
    manifest["artifacts"][str(forged.relative_to(tmp_path))] = hashlib.sha256(
        forged.read_bytes()
    ).hexdigest()
    (output / "RUN_MANIFEST.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="outside the variant's supported years"):
        compute.main(args + ["--resume"])
    # A progress receipt for 2023 is never read, even one whose identity
    # fields match this run exactly (it would be accepted for 2024).
    (output / "RUN_MANIFEST.json").unlink()
    genuine = json.loads((output / "RUN_PROGRESS_2024.json").read_bytes())
    (output / "RUN_PROGRESS_2023.json").write_text(
        json.dumps(
            {
                **genuine,
                "year": 2023,
                "artifacts": {
                    str(forged.relative_to(tmp_path)): hashlib.sha256(
                        forged.read_bytes()
                    ).hexdigest()
                },
            }
        )
    )
    assert compute.main(args + ["--resume"]) == 0
    rerun = json.loads((output / "RUN_MANIFEST.json").read_bytes())
    assert all("_2023.json" not in path for path in rerun["artifacts"])


def test_staging_and_comparison_refuse_a_sealed_namespace(tmp_path, monkeypatch):
    # B3: the staged rows and comparison are part of what the receipt binds.
    from pipeline import compare_uk_event as compare

    registry, manifest, output, digest, _ = staged_variant_run(tmp_path, monkeypatch)
    (output.parent / rv.RECEIPT_NAME).write_text("{}")
    monkeypatch.setattr(rv, "ROOT", tmp_path)
    monkeypatch.setattr(
        stage.compute, "event_paths", lambda event: (tmp_path / "registry.json", output)
    )
    with pytest.raises(rv.VariantError, match="sealed"):
        stage.main(["--event", "test_event", "--artifact-dir", str(output)])
    assert not (output / "STAGED.jsonl").exists()
    with pytest.raises(rv.VariantError, match="sealed"):
        compare.write_summary(output.parent, artifact_root=tmp_path)


def test_population_note_names_the_variant_population():
    assert stage.population_note(None) == stage.LEGACY_POPULATION_NOTE
    assert "single certified 2023 population" in stage.LEGACY_POPULATION_NOTE
    note = stage.population_note(record())
    assert "enhanced_frs_2024_25.h5" in note and "1.58.0" in note
    assert "2023" not in note


def test_only_certified_variants_run_unless_qualifying(tmp_path):
    document = rv.load_document()
    candidate = copy.deepcopy(document)
    for r in candidate["variants"]:
        if r["variant_id"] == CURRENT:
            r["status"] = "candidate"
    path = tmp_path / "variants.json"
    path.write_text(json.dumps(candidate))
    with pytest.raises(rv.VariantError, match="not certified"):
        rv.get_variant(CURRENT, path=path)
    assert rv.get_variant(CURRENT, path=path, allow_uncertified=True)["status"] == (
        "candidate"
    )
    candidate["default_variant"] = CURRENT
    path.write_text(json.dumps(candidate))
    with pytest.raises(rv.VariantError, match="default_variant must be"):
        rv.load_document(path)


def test_the_cli_refuses_a_candidate_without_the_qualification_flag(
    tmp_path, monkeypatch
):
    document = rv.load_document()
    for r in document["variants"]:
        if r["variant_id"] == CURRENT:
            r["status"] = "candidate"
    path = tmp_path / "variants.json"
    path.write_text(json.dumps(document))
    args = ["--event", "autumn_budget_2024", "--variant", CURRENT, "--dry-run"]
    with pytest.raises(rv.VariantError, match="not certified"):
        compute.main(args + ["--variants-file", str(path)])


def test_the_legacy_variant_refuses_a_dataset_file():
    # M5: the legacy variant reads its Hugging Face cache; a file would be
    # silently ignored.
    with pytest.raises(ValueError, match="--dataset-file"):
        compute.main(
            ["--event", "autumn_budget_2024", "--dataset-file", "x.h5", "--dry-run"]
        )


def test_a_legacy_run_checks_its_installed_environment_first(monkeypatch):
    # M4: the legacy record's digests are checked before its preflight.
    calls = []
    monkeypatch.setattr(
        compute,
        "check_variant_environment",
        lambda variant: (
            calls.append(variant["variant_id"])
            or (_ for _ in ()).throw(rv.VariantError("not the certified environment"))
        ),
    )
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda *a: (_ for _ in ()).throw(AssertionError("preflight before check")),
    )
    monkeypatch.setattr(rv, "assert_not_sealed", lambda path: None)
    with pytest.raises(rv.VariantError, match="not the certified environment"):
        compute.main(["--event", "autumn_budget_2024"])
    assert calls == [LEGACY]


@pytest.mark.parametrize(
    "label,mutate",
    [
        ("dataset repo", lambda r: r["identity"]["dataset"].update(repo_id="a/b")),
        ("dataset revision", lambda r: r["identity"]["dataset"].update(revision="9")),
        ("dataset path", lambda r: r["identity"]["dataset"].update(path="other.h5")),
        (
            "dataset repo type",
            lambda r: r["identity"]["dataset"].update(repo_type="dataset"),
        ),
        ("layout", lambda r: r.update(layout="flat")),
        ("bool data year", lambda r: r.update(data_years=[True, 2])),
        ("certification", lambda r: r.update(certification="certified")),
        ("identity", lambda r: r.update(identity=[])),
    ],
)
def test_single_field_changes_are_refused(label, mutate):
    r = record()
    mutate(r)
    with pytest.raises(rv.VariantError):
        rv.validate_record(r)


def test_a_wrong_legacy_result_root_is_refused():
    r = record(LEGACY)
    r["result_root"] = f"{rv.REPLAY_RESULT_ROOT}/{LEGACY}"
    with pytest.raises(rv.VariantError, match="result_root"):
        rv.validate_record(r)


def test_a_requirements_pin_that_disagrees_is_refused(tmp_path):
    r = record()
    text = (rv.ROOT / r["requirements"]["path"]).read_text()
    changed = text.replace("policyengine-uk==2.125.1", "policyengine-uk==2.125.2")
    assert changed != text
    path = tmp_path / "docs" / "requirements.txt"
    path.parent.mkdir(parents=True)
    path.write_text(changed)
    r["requirements"] = {
        "path": "docs/requirements.txt",
        "sha256": hashlib.sha256(changed.encode()).hexdigest(),
    }
    r["identity"]["requirements_sha256"] = r["requirements"]["sha256"]
    reseal(r)
    with pytest.raises(rv.VariantError, match="requirements pin policyengine-uk"):
        rv.validate_record(r, root=tmp_path)


def demo_site(tmp_path, monkeypatch):
    files = {
        "demo/__init__.py": b"x = 1\n",
        "demo/parameters/rate.yaml": b"values: {2024-01-01: 0.2}\n",
    }
    site = tmp_path / "site"
    write_distribution(site, files, b"uv\n")
    monkeypatch.syspath_prepend(str(site))
    importlib.invalidate_caches()
    return site


def test_an_unlisted_file_in_a_package_directory_is_found(tmp_path, monkeypatch):
    # B4: core loads every file in a parameter directory, so a file no RECORD
    # lists can change results while every listed file still verifies.
    site = demo_site(tmp_path, monkeypatch)
    assert rv.unlisted_package_files(("demo",)) == {}
    (site / "demo" / "__pycache__").mkdir()
    (site / "demo" / "__pycache__" / "y.cpython-312.pyc").write_bytes(b"\0")
    assert rv.unlisted_package_files(("demo",)) == {}  # bytecode is never read
    (site / "demo" / "parameters" / "extra.yaml").write_text("values: {}\n")
    assert rv.unlisted_package_files(("demo",)) == {
        "demo": ["demo/parameters/extra.yaml"]
    }


def test_the_scan_sees_what_core_would_load(tmp_path, monkeypatch):
    # Review of dc040de: core's loaders recurse into __pycache__ and follow
    # symlinked directories, and only the package's own RECORD is hash-checked.
    site = demo_site(tmp_path, monkeypatch)
    cache = site / "demo" / "parameters" / "__pycache__"
    cache.mkdir()
    (cache / "ok.cpython-312.pyc").write_bytes(b"\0")
    (cache / "x.py").write_text("raise SystemExit\n")
    assert rv.unlisted_package_files(("demo",)) == {
        "demo": ["demo/parameters/__pycache__/x.py"]
    }
    (cache / "x.py").unlink()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "rate.yaml").write_text("values: {}\n")
    (site / "demo" / "parameters" / "linked").symlink_to(
        outside, target_is_directory=True
    )
    assert rv.unlisted_package_files(("demo",)) == {
        "demo": ["demo/parameters/linked (symlink)"]
    }
    (site / "demo" / "parameters" / "linked").unlink()
    # A symlink to a listed file is still a symlink, not that file.
    (site / "demo" / "alias.py").symlink_to(site / "demo" / "__init__.py")
    assert rv.unlisted_package_files(("demo",)) == {"demo": ["demo/alias.py (symlink)"]}
    (site / "demo" / "alias.py").unlink()
    # Another distribution listing a file inside this package does not count.
    extra = site / "demo" / "parameters" / "from_other.yaml"
    extra.write_text("values: {}\n")
    info = site / "other-1.0.dist-info"
    info.mkdir()
    (info / "METADATA").write_text("Metadata-Version: 2.1\nName: other\nVersion: 1.0\n")
    (info / "RECORD").write_text("demo/parameters/from_other.yaml,,\n")
    importlib.invalidate_caches()
    assert rv.unlisted_package_files(("demo",)) == {
        "demo": ["demo/parameters/from_other.yaml"]
    }


def test_startup_files_must_belong_to_a_pinned_distribution(tmp_path, monkeypatch):
    # site.py runs a .pth file's import lines before any check here.
    site = demo_site(tmp_path, monkeypatch)
    (site / "_virtualenv.pth").write_text("import _virtualenv\n")
    (site / "hook.pth").write_text("import os; os.environ['X'] = '1'\n")
    files = rv.startup_files(("demo",))
    assert [f["name"] for f in files] == ["_virtualenv.pth", "hook.pth"]
    assert rv.startup_file_problems(files, {"demo": "1.0"}) == [
        "startup file hook.pth belongs to no pinned distribution"
    ]
    # The shim's name with other content is not the shim.
    (site / "_virtualenv.pth").write_text("import evil\n")
    assert len(rv.startup_file_problems(rv.startup_files(("demo",)), {})) == 2
    # A .pth a pinned distribution lists is that distribution's own.
    owned = [{"name": "x.pth", "owner": "demo", "text": "import x", "symlink": False}]
    assert rv.startup_file_problems(owned, {"demo": "1.0"}) == []
    assert rv.startup_file_problems(owned, {}) != []
    r = record()
    installed = installed_for(r)
    installed["startup_files"] = files
    with pytest.raises(rv.VariantError, match="startup file hook.pth"):
        rv.verify_installed(r, installed=installed)


def test_unlisted_files_fail_the_installed_check():
    r = record()
    installed = installed_for(r)
    rv.verify_installed(r, installed=installed)
    installed["unlisted_files"] = {"policyengine-uk": ["policyengine_uk/x.yaml"]}
    with pytest.raises(rv.VariantError, match="files outside its RECORD"):
        rv.verify_installed(r, installed=installed)


def test_bytecode_isolation_precedes_engine_import(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    environ = {}
    for module in rv.ENGINE_MODULES.values():
        monkeypatch.delitem(sys.modules, module, raising=False)
    stale = tmp_path / "no-bytecode" / "policyengine_uk"
    stale.mkdir(parents=True)
    (stale / "x.pyc").write_bytes(b"\0")
    prefix = rv.isolate_bytecode(tmp_path, environ)
    assert sys.pycache_prefix == str(prefix) == environ["PYTHONPYCACHEPREFIX"]
    assert sys.dont_write_bytecode and environ["PYTHONDONTWRITEBYTECODE"] == "1"
    assert list(prefix.iterdir()) == []  # a stale cache is cleared
    monkeypatch.setitem(sys.modules, "policyengine_uk", object())
    with pytest.raises(rv.VariantError, match="imported before isolation"):
        rv.isolate_bytecode(tmp_path, environ)


def test_bytecode_isolation_refuses_a_symlinked_directory(tmp_path, monkeypatch):
    # The guard runs before anything resolves or removes the path: a
    # symlinked no-bytecode directory must not get its target deleted.
    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    for module in rv.ENGINE_MODULES.values():
        monkeypatch.delitem(sys.modules, module, raising=False)
    precious = tmp_path / "precious"
    precious.mkdir()
    (precious / "keep.txt").write_text("keep")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "no-bytecode").symlink_to(precious, target_is_directory=True)
    with pytest.raises(rv.VariantError, match="symlink"):
        rv.isolate_bytecode(runtime, {})
    assert (precious / "keep.txt").read_text() == "keep"


def test_an_engine_imported_from_another_tree_is_refused(tmp_path, monkeypatch):
    site = demo_site(tmp_path, monkeypatch)
    monkeypatch.setitem(rv.ENGINE_MODULES, "demo", "demo")
    module = type(sys)("demo")
    module.__file__ = str(site / "demo" / "__init__.py")
    monkeypatch.setitem(sys.modules, "demo", module)
    rv.verify_import_origins(("demo",))
    shadow = tmp_path / "shadow" / "demo" / "__init__.py"
    shadow.parent.mkdir(parents=True)
    shadow.write_text("x = 2\n")
    module.__file__ = str(shadow)
    with pytest.raises(rv.VariantError, match="not its verified distribution"):
        rv.verify_import_origins(("demo",))


def test_isolation_routes_every_http_request_to_a_closed_port():
    # M2: requests ignores HF_HUB_OFFLINE but reads these variables
    # (urllib.request.getproxies), so the release-manifest fetch fails and
    # the wrapper uses its packaged certification.
    import urllib.request

    environ = {"NO_PROXY": "*", "no_proxy": "huggingface.co", "PATH": "/bin"}
    removed = rv.isolate_certification_environment(environ)
    assert {"NO_PROXY", "no_proxy"} <= set(removed)
    original = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(environ)
        proxies = urllib.request.getproxies()
    finally:
        os.environ.clear()
        os.environ.update(original)
    assert proxies["https"] == proxies["http"] == "http://127.0.0.1:9"
    assert "no" not in proxies


def test_a_symlinked_data_directory_is_refused(tmp_path):
    payload = b"certified bytes"
    r = tiny_variant(payload)
    source = tmp_path / "source.h5"
    source.write_bytes(payload)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "data").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(rv.VariantError, match="symlink"):
        rv.materialize_dataset(r, runtime, source=source)
    assert list(elsewhere.iterdir()) == []


def test_a_dataset_that_does_not_state_its_years_fails_when_required(
    monkeypatch, tmp_path
):
    # M3: a variant's simulation fails closed when its dataset hides its years.
    from pipeline import compute_uk_obr_costings as fiscal

    data_file = tmp_path / "data.h5"
    data_file.write_bytes(b"x")

    class Sim:
        policyengine_bundle = {
            "certified_data_build_id": "build",
            "runtime_dataset_source": str(data_file),
        }
        tax_benefit_system = type("System", (), {"variables": {"income_tax": None}})()
        dataset = object()

        def calculate(self, name, period):
            import numpy as np

            return np.array([1.0])

    class Uk:
        @staticmethod
        def managed_microsimulation(**kwargs):
            return Sim()

    import types

    monkeypatch.setitem(sys.modules, "policyengine", types.SimpleNamespace(uk=Uk))
    monkeypatch.setattr(fiscal, "variable_metadata", lambda *a, **k: {})
    kwargs = dict(
        year=2024,
        variables=["income_tax"],
        reform=None,
        runtime_dataset_source=data_file,
        expected_dataset_sha256=hashlib.sha256(b"x").hexdigest(),
    )
    assert fiscal.run_managed_simulation(**kwargs)["aggregates_gbp"]  # legacy
    with pytest.raises(RuntimeError, match="does not state its years"):
        fiscal.run_managed_simulation(**kwargs, require_dataset_years=True)


def test_the_installed_engine_is_a_committed_variant_when_present():
    """In a pinned venv (.venv-candidate, .venv-replay, and the CI
    replay-engine job once the receiver change adds it), the real installed
    environment reproduces a committed record's digests, with no unlisted
    files. Without an engine installed this test skips."""
    try:
        version = importlib.metadata.version("policyengine-uk")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("no engine installed")
    matches = [
        r
        for r in rv.load_document()["variants"]
        if r["identity"]["packages"]["policyengine-uk"]["version"] == version
    ]
    if not matches:
        pytest.skip(f"policyengine-uk {version} is no committed variant")
    installed = rv.installed_identity()
    assert installed["unlisted_files"] == {}
    rv.verify_installed(matches[0], installed=installed)


def test_the_legacy_preflight_is_isolated_and_checks_its_release_bundle(monkeypatch):
    # Review of dc040de, M4: the legacy run uses the packaged certification
    # and must match its record's release bundle exactly, like any variant.
    calls = []
    legacy = record(LEGACY)
    bundle = dict(legacy["identity"]["release_bundle"])
    monkeypatch.setattr(compute.fiscal, "configure_offline", lambda: None)
    monkeypatch.setattr(compute.worlds, "configure_offline", lambda: None)
    monkeypatch.setattr(
        rv, "isolate_certification_environment", lambda: calls.append("certification")
    )
    monkeypatch.setattr(rv, "isolate_bytecode", lambda root: calls.append("bytecode"))
    monkeypatch.setattr(
        compute.worlds,
        "preflight",
        lambda: {
            "sha256": legacy["identity"]["dataset"]["sha256"],
            "revision": bundle["certified_data_build_id"],
        },
    )
    managed = {
        "sha256": legacy["identity"]["dataset"]["sha256"],
        "release_bundle": bundle,
    }
    monkeypatch.setattr(
        compute.fiscal,
        "preflight_certified_dataset",
        lambda: calls.append("engine") or dict(managed),
    )
    monkeypatch.setattr(compute, "import_engine", lambda: calls.append("origins"))
    pre = compute.preflight(legacy)
    assert calls == ["certification", "bytecode", "engine", "origins"]
    assert pre["check_import_origins"] is True
    managed["release_bundle"] = {**bundle, "compatibility_basis": "other"}
    with pytest.raises(rv.VariantError, match="runtime release bundle differs"):
        compute.preflight(legacy)
    # Without a record (the Modal preflight-only path) it is the original check.
    calls.clear()
    managed["release_bundle"] = bundle
    assert "check_import_origins" not in compute.preflight()
    assert calls == ["engine"]


def test_guards_check_the_environment_and_compile_from_source(monkeypatch):
    calls = []
    monkeypatch.setattr(
        compute, "check_variant_environment", lambda variant: calls.append("installed")
    )
    monkeypatch.setattr(rv, "isolate_bytecode", lambda root: calls.append("bytecode"))
    monkeypatch.setattr(
        compute.worlds,
        "engine_resolver",
        lambda: calls.append("engine") or (lambda path, date: None),
    )
    monkeypatch.setattr(compute.worlds, "reversal_delta_mismatches", lambda *a, **k: [])
    monkeypatch.setattr(compute, "import_engine", lambda: calls.append("origins"))
    assert compute.main(["--event", "autumn_budget_2024", "--guards"]) == 0
    assert calls == ["installed", "bytecode", "engine", "origins"]


def test_a_shadowed_distribution_copy_does_not_count(tmp_path, monkeypatch):
    # Found on Modal: the container's own client packages sit behind the
    # pinned environment on sys.path; Python imports the first copy.
    for index, version in enumerate(("2.0", "1.0")):
        info = tmp_path / f"site{index}" / f"shadowed-{version}.dist-info"
        info.mkdir(parents=True)
        (info / "METADATA").write_text(
            f"Metadata-Version: 2.1\nName: shadowed\nVersion: {version}\n"
        )
    monkeypatch.syspath_prepend(str(tmp_path / "site1"))
    monkeypatch.syspath_prepend(str(tmp_path / "site0"))  # first on the path
    importlib.invalidate_caches()
    assert importlib.metadata.version("shadowed") == "2.0"
    assert rv.installed_distributions()["shadowed"] == "2.0"
