"""Certified-event numerical identities, exercised without a population download."""

import copy
import hashlib
import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compute_uk_ab2025 as ab
from pipeline import compute_uk_event as compute
from pipeline import stage_uk_event as stage


def measure(construction="reversal_on_certified_world"):
    return {
        "measure_key": "test_event__tax_and_benefit",
        "title": "An announcement",
        "computability": "partial",
        "construction": construction,
        "commences_fy": "2024-25",
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
        "source_rows": [
            {
                "source_row_id": "tax",
                "fy": "2024-25",
                "metric": "revenue_change",
                "tax_head": "Income tax",
                "value_gbp": 100,
            },
            {
                "source_row_id": "benefit",
                "fy": "2024-25",
                "metric": "exchequer_impact",
                "tax_head": "Welfare inside cap",
                "value_gbp": -30,
            },
        ],
    }


def simulation(tax=1000, benefit=1000):
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
            "model_version": "2.89.2",
            "certified_data_build_id": "certified-test",
        },
        "dataset_sha256_before": "a" * 64,
        "dataset_sha256_after": "a" * 64,
        "performance": {"wall_seconds": 1},
    }


def artifact(base, reform, construction="reversal_on_certified_world"):
    m = measure(construction)
    if construction != "reversal_on_certified_world":
        m.pop("pe_baseline_modifier")
        m["pe_reform_delta"] = {"gov.tax.rate": 0.3}
    world = ab.worlds_for(m, {m["measure_key"]: m}, years=[2024])
    return compute.build_artifact(
        measure=m,
        world=world,
        year=2024,
        baseline=base,
        reform=reform,
        certified=reform if construction == "reversal_on_certified_world" else base,
        registry_sha256="b" * 64,
        event="test_event",
    )


@settings(deadline=None)
@given(
    st.integers(-(10**10), 10**10),
    st.integers(-(10**10), 10**10),
    st.integers(-(10**10), 10**10),
    st.integers(-(10**10), 10**10),
)
def test_reversal_preserves_literal_delta_and_orients_exchequer_gain(bt, bb, rt, rb):
    a = artifact(simulation(bt, bb), simulation(rt, rb))
    assert a["head_effects"] == {"income_tax": rt - bt, "universal_credit": -(rb - bb)}
    assert a["literal_reversal_minus_certified_gbp"] == {
        "income_tax": bt - rt,
        "universal_credit": -(bb - rb),
    }
    assert all(
        a["head_effects"][v] == -a["literal_reform_minus_baseline"][v]
        for v in a["head_effects"]
    )
    assert sum(a["head_effects"].values()) == a["measure_total_gbp"]
    stage.validate_artifact(a, measure(), 2024, "b" * 64, "a" * 64)


@settings(deadline=None)
@given(st.integers(-(10**10), 10**10), st.integers(-(10**10), 10**10))
def test_forward_tax_receipts_positive_and_benefit_outlays_negative(tax, benefit):
    a = artifact(
        simulation(0, 0), simulation(tax, benefit), "forward_delta_on_certified_world"
    )
    assert a["head_effects"] == {"income_tax": tax, "universal_credit": -benefit}
    assert a["literal_reform_minus_baseline"] == a["head_effects"]
    assert a["measure_total_gbp"] == tax - benefit


def test_artifact_bytes_ignore_nondeterministic_runtime_measurements():
    b, r = simulation(900, 1000), simulation(1000, 1030)
    first = compute.canonical_bytes(artifact(b, r))
    b["performance"] = {"wall_seconds": 200, "peak_rss": 9000}
    r["performance"] = {"wall_seconds": 23, "peak_rss": 3000}
    assert compute.canonical_bytes(artifact(b, r)) == first


def test_shared_ab2025_world_defaults_and_explicit_old_window_identical():
    index = ab.load_registry()
    assert ab.computable(index) == ab.computable(index, years=ab.YEARS)
    assert ab.world_coverage_gaps(index) == ab.world_coverage_gaps(
        index, years=ab.YEARS
    )
    assert ab._windows(0.21) == [("2026-01-01.2035-12-31", 0.21)]
    assert ab._windows(0.21, years=[2023, 2024]) == [("2023-01-01.2035-12-31", 0.21)]
    assert ab._windows({"2023-04-06.2024-04-05": 0.21}) == [
        ("2023-04-06.2024-04-05", 0.21)
    ]
    with pytest.raises(ValueError, match="reversed period"):
        ab._windows({"2024-04-06.2023-04-05": 0.21})


def test_artifact_rejects_different_worlds_and_mutated_dataset():
    b, r = simulation(), simulation()
    r["dataset_sha256_after"] = "c" * 64
    with pytest.raises(ValueError, match="hashes differ"):
        artifact(b, r)
    r = simulation()
    r["policyengine_bundle"]["certified_data_build_id"] = "different"
    with pytest.raises(ValueError, match="same certified release"):
        artifact(b, r)


def test_head_mappings_cannot_double_count_a_variable():
    m = measure()
    m["heads"].append(
        {"obr_head": "Another tax", "pe_variables": ["income_tax"], "channel": "tax"}
    )
    with pytest.raises(ValueError, match="multiple fiscal heads"):
        compute.variable_channels(m)
    m = measure()
    m["heads"][0]["pe_variables"] = ["income_tax", "income_tax"]
    with pytest.raises(ValueError, match="duplicate variables"):
        compute.variable_channels(m)


def test_stage_exact_inventory_oriented_heads_and_row_classification(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    m = measure()
    a = artifact(simulation(900, 1000), simulation(1000, 1030))
    d = tmp_path / "artifacts"
    d.mkdir()
    payload = compute.canonical_bytes(a)
    (d / "measure.json").write_bytes(payload)
    m["source_rows"].append(
        {
            "source_row_id": "corporation",
            "fy": "2024-25",
            "metric": "revenue_change",
            "tax_head": "Corporation tax",
            "value_gbp": 4,
            "classification": "out_of_household_scope",
        }
    )
    registry = {"event": "test_event", "calendar_years": [2024], "measures": [m]}
    manifest = {
        "registry_sha256": "b" * 64,
        "certified_dataset_sha256": "a" * 64,
        "artifacts": {"artifacts/measure.json": hashlib.sha256(payload).hexdigest()},
    }
    rows, tally = stage.stage_event(
        registry, manifest, artifact_dir=d, registry_sha256="b" * 64
    )
    by_id = {row["source_row_id"]: row for row in rows}
    assert by_id["tax"]["pe_value"] == 100
    assert by_id["benefit"]["pe_value"] == -30
    assert by_id["corporation"]["pe_value"] is None
    assert by_id["corporation"]["computability"] == "out_of_household_scope"
    assert tally["source_rows"] == tally["staged_rows"] == 3
    assert tally["source_value_gbp"] == 74
    assert all("population_vintage" in row["axes"] for row in rows)
    second_rows, second_tally = stage.stage_event(
        registry, manifest, artifact_dir=d, registry_sha256="b" * 64
    )
    assert compute.canonical_bytes(rows) == compute.canonical_bytes(second_rows)
    assert tally == second_tally
    (d / "measure.json").write_text("{}")
    with pytest.raises(ValueError, match="bytes differ"):
        stage.stage_event(registry, manifest, artifact_dir=d, registry_sha256="b" * 64)


def test_no_digest_no_simulation(tmp_path, monkeypatch):
    m = measure()
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"event": "test_event", "calendar_years": [2024], "measures": [m]})
    )
    monkeypatch.setattr(
        compute.registry_builder, "validate_registry", lambda registry: None
    )
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda: (_ for _ in ()).throw(RuntimeError("missing digest")),
    )
    called = []
    monkeypatch.setattr(compute, "run_sim", lambda *args: called.append(args))
    with pytest.raises(RuntimeError, match="missing digest"):
        compute.main(["--event", "test_event", "--registry", str(registry)])
    assert not called


def test_staging_rejects_duplicate_source_rows_without_artifacts(tmp_path):
    m = measure()
    m["source_rows"].append(copy.deepcopy(m["source_rows"][0]))
    with pytest.raises(ValueError, match="more than once"):
        stage.stage_event(
            {"calendar_years": [2024], "measures": [m]},
            None,
            artifact_dir=tmp_path,
            registry_sha256="b" * 64,
        )


def test_changed_registry_refused_before_preflight(tmp_path, monkeypatch):
    m = measure()
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"calendar_years": [2024], "measures": [m]}))
    monkeypatch.setattr(
        compute.registry_builder,
        "validate_registry",
        lambda document: registry.write_text("{}"),
    )
    called = []
    monkeypatch.setattr(compute, "preflight", lambda: called.append("preflight"))
    with pytest.raises(ValueError, match="registry bytes changed"):
        compute.main(["--event", "test_event", "--registry", str(registry)])
    assert not called


def test_compute_reuses_baselines_and_reruns_produce_identical_bytes(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    first = measure()
    second = copy.deepcopy(first)
    second["measure_key"] = "test_event__second_measure"
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"calendar_years": [2024, 2025], "measures": [first, second]})
    )
    monkeypatch.setattr(
        compute.registry_builder, "validate_registry", lambda registry: None
    )
    monkeypatch.setattr(
        compute.worlds, "engine_resolver", lambda: lambda path, date: None
    )
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda: {
            "sha256": "a" * 64,
            "release_bundle": {"certified_data_build_id": "certified-test"},
        },
    )
    calls = []

    def fake_run(year, variables, reform, pre):
        calls.append((year, variables, reform))
        result = simulation(900, 1000) if reform else simulation(1000, 1030)
        result["performance"]["wall_seconds"] = len(calls)
        return result

    monkeypatch.setattr(compute, "run_sim", fake_run)
    output = tmp_path / "results"
    args = [
        "--event",
        "test_event",
        "--registry",
        str(registry),
        "--output-dir",
        str(output),
    ]
    assert compute.main(args) == 0
    assert len(calls) == 6
    assert sum(reform is None for _, _, reform in calls) == 2
    numerical = {
        path.name: path.read_bytes()
        for path in output.glob("*.json")
        if path.name != "RUN_LOG.json"
    }
    assert compute.main(args) == 0
    assert len(calls) == 12
    assert numerical == {name: (output / name).read_bytes() for name in numerical}
    assert compute.main(args + ["--resume"]) == 0
    assert len(calls) == 12
    assert numerical == {name: (output / name).read_bytes() for name in numerical}
    (output / f"{first['measure_key']}_2024.json").write_text("{}")
    with pytest.raises(ValueError, match="retained artifact bytes"):
        compute.main(args + ["--resume"])
    assert len(calls) == 12


def test_supported_years_require_documented_event_window():
    assert compute.validate_years([2025, 2024], {"calendar_years": [2024, 2025]}) == [
        2024,
        2025,
    ]
    with pytest.raises(ValueError, match="outside"):
        compute.validate_years([2025], {"calendar_years": [2024]})
    with pytest.raises(ValueError, match="record"):
        compute.validate_years([2024], {})
    for unsupported in (2022, 2031):
        with pytest.raises(ValueError, match="2023 through 2030"):
            compute.validate_years([unsupported], {"calendar_years": [unsupported]})
