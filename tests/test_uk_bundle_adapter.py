"""Bundle adapter gates using mocked managed loaders; no population simulation."""

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from pipeline import compute_uk_event as compute
from pipeline import compute_uk_obr_costings as fiscal
from pipeline import uk_bundle as bundles


@pytest.fixture
def adapter(monkeypatch, tmp_path):
    key = "development-adapter-test"
    cached = tmp_path / "cached.h5"
    cached.write_bytes(b"small certified test population")
    digest = hashlib.sha256(cached.read_bytes()).hexdigest()
    versions = {
        "policyengine": "6.2.5",
        "policyengine-uk": "2.102.3",
        "policyengine-core": "3.32.10",
    }
    pin = {
        "bundle_key": key,
        "repo_id": "policyengine/policyengine-uk-data-private",
        "repo_type": "model",
        "artifact": "enhanced_frs_2024_25.h5",
        "revision": "1.56.16",
        "release_tag": "1.56.16",
        "resolved_hf_commit": "a" * 40,
        "release_manifest_revision": "b" * 40,
        "sha256": digest,
        "size_bytes": cached.stat().st_size,
        "data_year": 2024,
        "supported_calendar_years": [2024, 2030],
        "data_build_id": "policyengine-uk-data-1.56.16",
        "managed_loader_version": "6.2.5",
        "requirements_freeze": "unused.txt",
        "offline_audit": "unused.json",
        "development_bundle": True,
        "compatible_model_packages": [
            {"name": "policyengine-uk", "specifier": "==2.102.3"}
        ],
        "compatible_core_packages": [
            {"name": "policyengine-core", "specifier": "==3.32.10"}
        ],
    }
    pin_path = tmp_path / "pin.json"
    pin_path.write_text(json.dumps(pin))
    index = tmp_path / "index.json"
    index.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "default_bundle": bundles.DEFAULT_BUNDLE,
                "bundles": {
                    key: str(pin_path),
                    bundles.DEFAULT_BUNDLE: str(
                        bundles.ROOT / "data/uk/certified_bundle.json"
                    ),
                },
            }
        )
    )
    monkeypatch.setenv("UK_BUNDLE_INDEX", str(index))
    for name in (
        "HF_HUB_OFFLINE",
        "TRANSFORMERS_OFFLINE",
        "HF_DATASETS_OFFLINE",
        "HF_HUB_DISABLE_TELEMETRY",
        "POLICYENGINE_UK_DATA_REPO",
    ):
        monkeypatch.setenv(name, "initial-test-value")
    monkeypatch.setattr(fiscal, "ROOT", tmp_path)
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(fiscal, "LOCAL_DATA_MIRROR_ROOT", tmp_path / "mirror")
    monkeypatch.setattr(fiscal, "version", lambda name: versions[name])
    monkeypatch.setattr(fiscal, "package_version", lambda name: versions[name])
    compute.runtime_versions.cache_clear()
    monkeypatch.setattr(
        fiscal, "block_runtime_network", lambda: network_blocks.append(True)
    )
    network_blocks, downloads, materializations, simulations, calculations = (
        [],
        [],
        [],
        [],
        [],
    )
    release = {
        "model_version": "2.102.3",
        "default_dataset_uri": f"hf://{pin['repo_id']}/{pin['artifact']}@{pin['revision']}",
        "certified_data_artifact_sha256": digest,
        "certified_data_build_id": pin["data_build_id"],
        "compatibility_basis": "legacy_compatible_model_package",
        "policyengine_version": "6.2.5",
    }
    data_year = ["2024"]
    dataset_years = list(range(2024, 2031))
    mutation = [False]

    def download(**kwargs):
        downloads.append(kwargs)
        return str(cached)

    def materialize(country):
        materializations.append((country, Path.cwd()))
        return SimpleNamespace(path=Path.cwd() / "data" / pin["artifact"])

    def managed(**kwargs):
        simulations.append(kwargs)
        variable = SimpleNamespace(
            label="Income tax",
            entity=SimpleNamespace(key="person"),
            definition_period="year",
            unit="currency-GBP",
        )

        def calculate(name, year):
            calculations.append((name, year))
            if mutation[0]:
                cached.write_bytes(b"mutated during aggregate reads")
            return SimpleNamespace(sum=lambda: 100.0 + 5.0 * bool(kwargs))

        return SimpleNamespace(
            policyengine_bundle={
                **release,
                "runtime_dataset_source": str(Path.cwd() / "data" / pin["artifact"]),
            },
            dataset=SimpleNamespace(years=dataset_years),
            tax_benefit_system=SimpleNamespace(variables={"income_tax": variable}),
            calculate=calculate,
        )

    pe = SimpleNamespace(
        uk=SimpleNamespace(
            uk_latest=SimpleNamespace(release_bundle=release),
            managed_microsimulation=managed,
        )
    )
    monkeypatch.setitem(sys.modules, "policyengine", pe)
    monkeypatch.setitem(
        sys.modules, "huggingface_hub", SimpleNamespace(hf_hub_download=download)
    )
    monkeypatch.setitem(
        sys.modules,
        "pandas",
        SimpleNamespace(
            read_hdf=lambda path, table: SimpleNamespace(tolist=lambda: data_year)
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "policyengine.provenance.dataset_materialization",
        SimpleNamespace(materialize_dataset=materialize),
    )

    class Memory:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def as_dict(self):
            return {}

    monkeypatch.setattr(fiscal, "PeakRSSSampler", Memory)
    monkeypatch.setattr(fiscal, "current_rss_bytes", lambda: (0, "test"))
    value = SimpleNamespace(
        key=key,
        pin=pin,
        pin_path=pin_path,
        cached=cached,
        versions=versions,
        release=release,
        network_blocks=network_blocks,
        downloads=downloads,
        materializations=materializations,
        simulations=simulations,
        calculations=calculations,
        data_year=data_year,
        dataset_years=dataset_years,
        mutation=mutation,
        pe=pe,
        root=tmp_path,
    )
    yield value
    compute.runtime_versions.cache_clear()


def run(adapter, pre, **overrides):
    args = dict(
        year=2026,
        variables=["income_tax"],
        reform=None,
        runtime_dataset_source=Path(pre["runtime_dataset_source"]),
        expected_dataset_sha256=pre["sha256"],
        bundle_key=adapter.key,
    )
    return fiscal.run_managed_simulation(**{**args, **overrides})


def test_preflight_is_cached_model_repository_and_exact_materialized_file(adapter):
    original = Path.cwd()
    pre = fiscal.preflight_certified_dataset(adapter.key)
    assert adapter.downloads == [
        {
            "repo_id": adapter.pin["repo_id"],
            "repo_type": "model",
            "filename": adapter.pin["artifact"],
            "revision": adapter.pin["resolved_hf_commit"],
            "local_files_only": True,
        }
    ]
    assert pre["runtime_network_blocked"] is True and pre["local_files_only"] is True
    assert adapter.network_blocks
    assert Path(pre["runtime_dataset_source"]).resolve() == adapter.cached.resolve()
    assert (
        fiscal.sha256_file(Path(pre["runtime_dataset_source"]))
        == pre["sha256"]
        == adapter.pin["sha256"]
    )
    assert adapter.materializations[0][0] == "uk"
    assert Path.cwd() == original
    assert adapter.simulations == []


@pytest.mark.parametrize(
    "package", ["policyengine", "policyengine-uk", "policyengine-core"]
)
def test_preflight_refuses_each_engine_package_drift_before_artifact_lookup(
    adapter, package
):
    adapter.versions[package] = "0.0.1"
    with pytest.raises(RuntimeError, match="(installed|version differs)"):
        fiscal.preflight_certified_dataset(adapter.key)
    assert adapter.downloads == [] and adapter.simulations == []


@pytest.mark.parametrize(
    "field",
    [
        "default_dataset_uri",
        "certified_data_artifact_sha256",
        "certified_data_build_id",
        "compatibility_basis",
    ],
)
def test_preflight_refuses_wrong_release_certification_before_lookup(adapter, field):
    adapter.release[field] = (
        "unverified_test" if field == "compatibility_basis" else "different"
    )
    with pytest.raises(RuntimeError, match="(managed release|certification)"):
        fiscal.preflight_certified_dataset(adapter.key)
    assert adapter.downloads == [] and adapter.simulations == []


@pytest.mark.parametrize("field", ["sha256", "size_bytes", "data_year"])
def test_preflight_refuses_cached_digest_size_or_data_year_drift(adapter, field):
    if field == "sha256":
        adapter.cached.write_bytes(b"x" * adapter.pin["size_bytes"])
    elif field == "size_bytes":
        adapter.pin[field] += 1
        adapter.pin_path.write_text(json.dumps(adapter.pin))
    else:
        adapter.data_year[:] = ["2026"]
    with pytest.raises(RuntimeError, match="(digest or size|data year)"):
        fiscal.preflight_certified_dataset(adapter.key)
    assert adapter.materializations == [] and adapter.simulations == []


def test_preflight_refuses_materializer_reporting_a_different_file(
    adapter, monkeypatch
):
    monkeypatch.setitem(
        sys.modules,
        "policyengine.provenance.dataset_materialization",
        SimpleNamespace(
            materialize_dataset=lambda country: SimpleNamespace(
                path=adapter.root / "other.h5"
            )
        ),
    )
    with pytest.raises(RuntimeError, match="exact hash-verified file"):
        fiscal.preflight_certified_dataset(adapter.key)


@pytest.mark.parametrize("selection", ["baseline", "reform", "scenario"])
def test_managed_loader_receives_reform_or_scenario_and_projects_requested_year(
    adapter, selection
):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    reform = {"gov.tax.rate": {"2026-01-01.2030-12-31": 0.3}}
    scenario = object()
    overrides = (
        {"reform": reform}
        if selection == "reform"
        else {"scenario": scenario}
        if selection == "scenario"
        else {}
    )
    result = run(adapter, pre, **overrides)
    assert adapter.simulations == (
        [{"reform": reform}]
        if selection == "reform"
        else [{"scenario": scenario}]
        if selection == "scenario"
        else [{}]
    )
    assert adapter.calculations == [("income_tax", "2026")]
    assert (
        result["dataset_sha256_before"]
        == result["dataset_sha256_after"]
        == adapter.pin["sha256"]
    )
    assert (
        Path(result["policyengine_bundle"]["runtime_dataset_source"]).resolve()
        == adapter.cached.resolve()
    )


@pytest.mark.parametrize("years", [[2026, 2027, 2028], [2024, 2025]])
def test_managed_simulation_refuses_projected_year_as_base_or_missing_year(
    adapter, years
):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    adapter.dataset_years[:] = years
    with pytest.raises(RuntimeError, match="project the pinned data year"):
        run(adapter, pre)
    assert adapter.calculations == []


@pytest.mark.parametrize("package", ["policyengine", "policyengine-core"])
def test_managed_simulation_rechecks_loader_and_core_at_construction(adapter, package):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    adapter.versions[package] = "0.0.1"
    with pytest.raises(RuntimeError, match="version differs"):
        run(adapter, pre)
    assert adapter.simulations == []


def test_managed_simulation_refuses_mutation_after_calculation(adapter):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    adapter.mutation[0] = True
    with pytest.raises(RuntimeError, match="immediately after aggregate reads"):
        run(adapter, pre)


def test_managed_simulation_refuses_wrong_reported_runtime_path(adapter):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    managed = adapter.pe.uk.managed_microsimulation

    def wrong_source(**kwargs):
        sim = managed(**kwargs)
        sim.policyengine_bundle["runtime_dataset_source"] = str(
            adapter.root / "other.h5"
        )
        return sim

    adapter.pe.uk.managed_microsimulation = wrong_source
    with pytest.raises(RuntimeError, match="exact file hashed"):
        run(adapter, pre)
    assert adapter.calculations == []


@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.integers(min_value=2015, max_value=2040))
def test_year_window_comes_from_selected_bundle(adapter, year):
    registry = {"calendar_years": list(range(2015, 2041))}
    if 2024 <= year <= 2030:
        assert compute.validate_years([year], registry, adapter.key) == [year]
    else:
        with pytest.raises(ValueError, match="2024 through 2030"):
            compute.validate_years([year], registry, adapter.key)


@pytest.mark.parametrize("kind", ["manifest", "progress"])
def test_retained_receipt_foreign_bundle_is_rejected(adapter, kind):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    output = bundles.event_output_dir(
        "autumn_budget_2024", adapter.key, root=adapter.root
    )
    output.mkdir(parents=True)
    receipt = compute.progress_receipt(
        {
            "event": "autumn_budget_2024",
            "year": 2026,
            "registry_sha256": "c" * 64,
            "pre": pre,
            "bundle": adapter.key,
        },
        {},
    )
    receipt["bundle_key"] = bundles.DEFAULT_BUNDLE
    (
        output
        / ("RUN_MANIFEST.json" if kind == "manifest" else "RUN_PROGRESS_2026.json")
    ).write_bytes(compute.canonical_bytes(receipt))
    with pytest.raises(ValueError, match="bundle identity mismatch"):
        compute.retained_artifact_digests(
            output,
            event="autumn_budget_2024",
            years=[2026],
            registry_sha256="c" * 64,
            pre=pre,
            bundle=adapter.key,
        )


@pytest.mark.parametrize("kind", ["manifest", "progress"])
@pytest.mark.parametrize(
    "field",
    [
        "engine_version",
        "policyengine_version",
        "policyengine_core_version",
        "data_bundle",
    ],
)
def test_retained_receipt_runtime_drift_is_rejected_even_with_correct_nested_identity(
    adapter, kind, field
):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    output = bundles.event_output_dir(
        "autumn_budget_2024", adapter.key, root=adapter.root
    )
    output.mkdir(parents=True)
    receipt = compute.progress_receipt(
        {
            "event": "autumn_budget_2024",
            "year": 2026,
            "registry_sha256": "c" * 64,
            "pre": pre,
            "bundle": adapter.key,
        },
        {},
    )
    receipt[field] = "foreign-runtime"
    (
        output
        / ("RUN_MANIFEST.json" if kind == "manifest" else "RUN_PROGRESS_2026.json")
    ).write_bytes(compute.canonical_bytes(receipt))
    with pytest.raises(ValueError, match="runtime bundle mismatch"):
        compute.retained_artifact_digests(
            output,
            event="autumn_budget_2024",
            years=[2026],
            registry_sha256="c" * 64,
            pre=pre,
            bundle=adapter.key,
        )


def test_retained_receipt_cannot_name_another_bundle_artifact(adapter):
    pre = fiscal.preflight_certified_dataset(adapter.key)
    output = bundles.event_output_dir(
        "autumn_budget_2024", adapter.key, root=adapter.root
    )
    output.mkdir(parents=True)
    receipt = compute.progress_receipt(
        {
            "event": "autumn_budget_2024",
            "year": 2026,
            "registry_sha256": "c" * 64,
            "pre": pre,
            "bundle": adapter.key,
        },
        {"results/uk/events/autumn_budget_2024/foreign_2026.json": "d" * 64},
    )
    (output / "RUN_PROGRESS_2026.json").write_bytes(compute.canonical_bytes(receipt))
    with pytest.raises(ValueError, match="outside this event directory"):
        compute.retained_artifact_digests(
            output,
            event="autumn_budget_2024",
            years=[2026],
            registry_sha256="c" * 64,
            pre=pre,
            bundle=adapter.key,
        )


def test_default_progress_bytes_do_not_gain_bundle_identity(monkeypatch):
    monkeypatch.setattr(
        fiscal,
        "package_version",
        lambda package: {
            "policyengine": "5.0.2",
            "policyengine-core": "3.27.1",
            "policyengine-uk": "2.89.2",
        }[package],
    )
    compute.runtime_versions.cache_clear()
    job = {
        "event": "autumn_budget_2024",
        "year": 2026,
        "registry_sha256": "c" * 64,
        "pre": {
            "sha256": "d" * 64,
            "release_bundle": {"certified_data_build_id": "legacy"},
        },
    }
    implicit = compute.progress_receipt(job, {})
    explicit = compute.progress_receipt({**job, "bundle": bundles.DEFAULT_BUNDLE}, {})
    assert compute.canonical_bytes(implicit) == compute.canonical_bytes(explicit)
    assert "bundle_key" not in implicit and "engine_versions" not in implicit
    compute.runtime_versions.cache_clear()


def test_output_paths_cannot_cross_registered_bundle_namespaces(adapter):
    with pytest.raises(ValueError, match="another bundle"):
        compute.validate_output_bundle(
            adapter.root / "results/uk/events/autumn_budget_2024", adapter.key
        )
    with pytest.raises(ValueError, match="another bundle"):
        compute.validate_output_bundle(
            adapter.root
            / f"results/uk/events/bundles/{adapter.key}/autumn_budget_2024",
            bundles.DEFAULT_BUNDLE,
        )
