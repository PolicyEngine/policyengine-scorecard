"""Certified-event numerical identities, exercised without a population download."""

import copy
import hashlib
import json
import os
import sys
from types import SimpleNamespace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compute_uk_ab2025 as ab
from pipeline import compute_uk_event as compute
from pipeline import stage_uk_event as stage


def test_optional_engine_provenance_preserves_legacy_metadata(monkeypatch):
    variable = SimpleNamespace(
        label="Income tax",
        entity=SimpleNamespace(key="person"),
        definition_period="year",
        unit="currency-GBP",
        documentation="The tax formula.",
    )
    system = SimpleNamespace(variables={"income_tax": variable})
    monkeypatch.setattr(
        compute.fiscal.inspect,
        "getsourcefile",
        lambda cls: "/venv/policyengine_uk/variables/income_tax.py",
    )
    legacy = compute.fiscal.variable_metadata(system, ["income_tax"])
    assert legacy == {
        "income_tax": {
            "label": "Income tax",
            "entity": "person",
            "definition_period": "year",
            "unit": "currency-GBP",
        }
    }
    enriched = compute.fiscal.variable_metadata(
        system, ["income_tax"], include_engine_provenance=True
    )
    assert enriched == {
        "income_tax": {
            **legacy["income_tax"],
            "documentation": "The tax formula.",
            "engine_source": "policyengine_uk/variables/income_tax.py",
        }
    }


def test_worker_interrupt_terminates_owned_children_before_shutdown(monkeypatch):
    calls = []

    class Process:
        def is_alive(self):
            return True

        def terminate(self):
            calls.append("terminate")

    class Executor:
        def __init__(self, **kwargs):
            assert kwargs["max_workers"] == 2
            self._processes = {1: Process(), 2: Process()}

        def map(self, *args):
            raise KeyboardInterrupt

        def shutdown(self, **kwargs):
            calls.append(("shutdown", kwargs))

    monkeypatch.setattr(compute, "ProcessPoolExecutor", Executor)
    with pytest.raises(KeyboardInterrupt):
        list(compute.parallel_year_results([{}], 2))
    assert calls == [
        "terminate",
        "terminate",
        ("shutdown", {"wait": True, "cancel_futures": True}),
    ]


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


def test_non_january_reform_dates_are_handled_by_explicit_annual_lookup():
    dated = {"gov.tax.rate": {"2023-04-06.2025-04-05": 0.21}}
    assert compute.annual_reform(dated) == {
        "gov.tax.rate": {"2024-01-01.2025-12-31": 0.21}
    }
    # A mid-year start does not acquire an effect in that same FY proxy.
    with pytest.raises(ValueError, match="no 1 January annual lookup"):
        compute.annual_reform({"gov.tax.rate": {"2023-04-06.2023-12-31": 0.21}})
    january = {"gov.tax.rate": {"2023-01-01.2025-12-31": 0.21}}
    assert compute.annual_reform(january) == january
    with pytest.raises(TypeError, match="explicit dated reform windows"):
        compute.annual_reform({"gov.tax.rate": 0.21})


def test_uc_health_reform_uses_managed_scenario_and_other_dicts_keep_path(monkeypatch):
    health = {compute.UC_HEALTH_ELEMENT_PARAMETER: {"2026-01-01.2029-12-31": 437.66}}
    scenario = object()
    monkeypatch.setattr(compute, "uc_health_scenario", lambda reform: scenario)
    calls = []

    def managed(**kwargs):
        calls.append(kwargs)
        return simulation()

    monkeypatch.setattr(compute.fiscal, "run_managed_simulation", managed)
    monkeypatch.setattr(compute.fiscal, "assert_managed_bundle", lambda *args: None)
    pre = {
        "runtime_dataset_source": "/certified.h5",
        "sha256": "a" * 64,
        "release_bundle": {},
    }
    compute.run_sim(2026, ["universal_credit"], health, pre)
    assert calls[0]["reform"] is None
    assert calls[0]["scenario"] is scenario
    tax = {"gov.tax.rate": {"2024-10-30.2035-12-31": 0.21}}
    compute.run_sim(2026, ["income_tax"], tax, pre)
    assert calls[1]["reform"] == {"gov.tax.rate": {"2025-01-01.2035-12-31": 0.21}}
    assert "scenario" not in calls[1]


def test_uc_health_scenario_updates_parameters_before_refreshing_fixed_inputs(
    monkeypatch,
):
    calls = []
    sim = SimpleNamespace(
        health_parameter=217.26,
        fixed_health_input=217.26 * 12,
        tax_benefit_system=SimpleNamespace(
            reset_parameter_caches=lambda: calls.append("reset")
        ),
    )

    class Scenario:
        def __init__(self, *, simulation_modifier):
            self.simulation_modifier = simulation_modifier

        @classmethod
        def from_reform(cls, reform):
            def update(simulation):
                calls.append("parameter_update")
                simulation.health_parameter = reform[
                    compute.UC_HEALTH_ELEMENT_PARAMETER
                ]["2026-01-01.2029-12-31"]

            return cls(simulation_modifier=update)

    def uc_modifier(simulation):
        calls.append("uc_modifier")
        simulation.fixed_health_input = simulation.health_parameter * 12

    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk.scenarios.uc_reform",
        SimpleNamespace(add_universal_credit_reform=uc_modifier),
    )
    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk.utils.scenario",
        SimpleNamespace(Scenario=Scenario),
    )
    reform = {compute.UC_HEALTH_ELEMENT_PARAMETER: {"2026-01-01.2029-12-31": 437.66}}
    compute.uc_health_scenario(reform).simulation_modifier(sim)
    assert calls == ["parameter_update", "reset", "uc_modifier"]
    assert sim.fixed_health_input == 437.66 * 12


@pytest.mark.skipif(
    os.environ.get("UK_REPLAY_ENGINE_TESTS") != "1",
    reason="set UK_REPLAY_ENGINE_TESTS=1 for the pinned synthetic-household integration check",
)
def test_uc_health_modifier_refresh_changes_awards_without_changing_cohorts():
    uk = pytest.importorskip("policyengine_uk")
    import numpy as np

    # The pinned seed assigns some of these otherwise identical claimants
    # to the new-claimant cohort. No population file is needed.
    situation = {"people": {}, "benunits": {}, "households": {}}
    for i in range(10):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {"2026": 40},
            "uc_limited_capability_for_WRA": {str(y): True for y in range(2026, 2030)},
        }
        situation["benunits"][f"b{i}"] = {"members": [person]}
        situation["households"][f"h{i}"] = {"members": [person]}
    reform = {compute.UC_HEALTH_ELEMENT_PARAMETER: {"2026-01-01.2029-12-31": 437.66}}
    certified = uk.Simulation(situation=situation)
    broken = uk.Simulation(situation=situation, reform=reform)
    fixed = uk.Simulation(
        situation=situation, scenario=compute.uc_health_scenario(reform)
    )
    baseline_awards = certified.calculate("uc_LCWRA_element", 2026)
    assert np.array_equal(broken.calculate("uc_LCWRA_element", 2026), baseline_awards)
    fixed_awards = fixed.calculate("uc_LCWRA_element", 2026)
    changed = fixed_awards != baseline_awards
    assert np.array_equal(changed, np.random.default_rng(43).random(10) < 0.11)
    assert (
        fixed.calculate("universal_credit", 2026).sum()
        > certified.calculate("universal_credit", 2026).sum()
    )


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
    duplicate = copy.deepcopy(registry)
    row = copy.deepcopy(duplicate["measures"][0]["source_rows"][0])
    row["source_row_id"] = "duplicate_tax_head"
    duplicate["measures"][0]["source_rows"].append(row)
    with pytest.raises(ValueError, match="mapped to multiple source rows"):
        stage.stage_event(duplicate, manifest, artifact_dir=d, registry_sha256="b" * 64)
    incomplete = copy.deepcopy(manifest)
    incomplete.update({"measures": [m["measure_key"]], "years": [2024, 2025]})
    with pytest.raises(ValueError, match="missing requested"):
        stage.stage_event(
            registry, incomplete, artifact_dir=d, registry_sha256="b" * 64
        )
    explicit_duplicate = copy.deepcopy(registry)
    explicit_duplicate["measures"][0]["source_rows"][0]["pe_variables"] = [
        "income_tax",
        "income_tax",
    ]
    with pytest.raises(ValueError, match="mapping repeats"):
        stage.stage_event(
            explicit_duplicate, manifest, artifact_dir=d, registry_sha256="b" * 64
        )
    (d / "measure.json").write_text("{}")
    with pytest.raises(ValueError, match="bytes differ"):
        stage.stage_event(registry, manifest, artifact_dir=d, registry_sha256="b" * 64)


def test_injected_b1_identical_health_worlds_block_numerical_replay(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    m = measure()
    m.update(
        measure_key="spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut",
        commences_fy="2026-27",
        pe_baseline_modifier={compute.UC_HEALTH_ELEMENT_PARAMETER: {"2026": 437.66}},
    )
    for source in m["source_rows"]:
        source["fy"] = "2026-27"
    world = ab.worlds_for(m, {m["measure_key"]: m}, years=[2026])
    # Inject B1's observable defect: the dict changed, but fixed health inputs
    # make every fiscal aggregate identical in the two constructed worlds.
    a = compute.build_artifact(
        measure=m,
        world=world,
        year=2026,
        baseline=simulation(),
        reform=simulation(),
        certified=simulation(),
        registry_sha256="b" * 64,
        event="test_event",
    )
    payload = compute.canonical_bytes(a)
    (tmp_path / "health.json").write_bytes(payload)
    manifest = {
        "registry_sha256": "b" * 64,
        "certified_dataset_sha256": "a" * 64,
        "artifacts": {"health.json": hashlib.sha256(payload).hexdigest()},
    }
    registry = {"event": "test_event", "calendar_years": [2026], "measures": [m]}
    rows, tally = stage.stage_event(
        registry, manifest, artifact_dir=tmp_path, registry_sha256="b" * 64
    )
    assert {row["status"] for row in rows} == {"inert_construction"}
    assert all(row["pe_value"] is None for row in rows)
    assert tally["full_event_complete"] is False
    assert tally["inert_measure_years"] == [
        {"measure_key": m["measure_key"], "year": 2026}
    ]


def test_explicit_delayed_january_activation_keeps_timing_gap(tmp_path, monkeypatch):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    m = measure()
    m["pe_baseline_modifier"] = {"gov.tax.rate": {"2024-10-30": 0.2}}
    m["annual_activation_fy"] = "2025-26"
    a = artifact(simulation(), simulation())
    payload = compute.canonical_bytes(a)
    (tmp_path / "timing.json").write_bytes(payload)
    manifest = {
        "registry_sha256": "b" * 64,
        "certified_dataset_sha256": "a" * 64,
        "artifacts": {"timing.json": hashlib.sha256(payload).hexdigest()},
    }
    rows, tally = stage.stage_event(
        {"event": "test_event", "calendar_years": [2024], "measures": [m]},
        manifest,
        artifact_dir=tmp_path,
        registry_sha256="b" * 64,
    )
    assert {row["status"] for row in rows} == {"not_computed"}
    assert tally["full_event_complete"] is True
    assert "inert_measure_years" not in tally


def test_injected_original_aa_april_start_blocks_numerical_replay(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    m = measure()
    m.update(
        measure_key="spring_budget_2023__pension_annual_allowance_package",
        commences_fy="2023-24",
        pe_baseline_modifier={
            "gov.hmrc.income_tax.allowances.annual_allowance.default": {
                "2023-04-06": 40000
            }
        },
    )
    for source in m["source_rows"]:
        source["fy"] = "2023-24"
    world = ab.worlds_for(m, {m["measure_key"]: m}, years=[2023])
    a = compute.build_artifact(
        measure=m,
        world=world,
        year=2023,
        baseline=simulation(),
        reform=simulation(),
        certified=simulation(),
        registry_sha256="b" * 64,
        event="test_event",
    )
    payload = compute.canonical_bytes(a)
    (tmp_path / "aa.json").write_bytes(payload)
    rows, tally = stage.stage_event(
        {"event": "test_event", "calendar_years": [2023], "measures": [m]},
        {
            "registry_sha256": "b" * 64,
            "certified_dataset_sha256": "a" * 64,
            "artifacts": {"aa.json": hashlib.sha256(payload).hexdigest()},
        },
        artifact_dir=tmp_path,
        registry_sha256="b" * 64,
    )
    assert {row["status"] for row in rows} == {"inert_construction"}
    assert all(row["pe_value"] is None for row in rows)
    assert tally["full_event_complete"] is False
    assert tally["inert_measure_years"] == [
        {"measure_key": m["measure_key"], "year": 2023}
    ]


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


@pytest.mark.parametrize(
    ("classification", "head", "scope_reason"),
    [
        ("partial", "Scottish BGA", None),
        ("not_expressible", "Corporation tax", None),
        (
            "partial",
            "Scottish BGA",
            "A devolved block-grant adjustment is outside household scope.",
        ),
    ],
)
def test_outside_heads_keep_source_reason_within_mixed_packages(
    classification, head, scope_reason, tmp_path, monkeypatch
):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    m = measure()
    m["computability"] = classification
    m["pe_gap"] = "The household package is missing an unported leg."
    source_reason = f"{head} is outside the household fiscal-head model."
    m["source_rows"].append(
        {
            "source_row_id": "outside",
            "fy": "2024-25",
            "metric": "exchequer_impact"
            if head == "Scottish BGA"
            else "revenue_change",
            "tax_head": head,
            "value_gbp": 4,
            "classification": "out_of_household_scope",
            "classification_reason": source_reason,
            "scope_reason": scope_reason,
            "pe_gap": "A generic package gap must not mask source-head scope.",
        }
    )
    manifest = None
    if classification == "partial":
        payload = compute.canonical_bytes(
            artifact(simulation(900, 1000), simulation(1000, 1030))
        )
        (tmp_path / "measure.json").write_bytes(payload)
        manifest = {
            "registry_sha256": "b" * 64,
            "certified_dataset_sha256": "a" * 64,
            "artifacts": {"measure.json": hashlib.sha256(payload).hexdigest()},
        }
    rows, tally = stage.stage_event(
        {"event": "test_event", "calendar_years": [2024], "measures": [m]},
        manifest,
        artifact_dir=tmp_path,
        registry_sha256="b" * 64,
    )
    by_id = {row["source_row_id"]: row for row in rows}
    assert by_id["outside"]["reason"] == (scope_reason or source_reason)
    assert by_id["outside"]["pe_value"] is None
    assert by_id["outside"]["computability"] == "out_of_household_scope"
    if classification == "partial":
        assert by_id["tax"]["pe_value"] == 100
        assert by_id["benefit"]["pe_value"] == -30
    else:
        assert by_id["tax"]["reason"] == m["pe_gap"]
    assert tally["source_rows"] == tally["staged_rows"] == 3
    assert tally["source_value_gbp"] == 74


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


def test_staging_preserves_fractional_source_gbp_beside_large_values(tmp_path):
    m = measure()
    m["source_rows"] = [
        {
            "source_row_id": str(i),
            "fy": "2024-25",
            "metric": "revenue_change",
            "tax_head": "Income tax",
            "value_gbp": float(value),
            "value_gbp_decimal": value,
        }
        for i, value in enumerate(["1000000000000000000000000000000", "0.1", "0.2"])
    ]
    rows, tally = stage.stage_event(
        {"calendar_years": [2024], "measures": [m]},
        None,
        artifact_dir=tmp_path,
        registry_sha256="b" * 64,
    )
    assert tally["source_value_gbp_decimal"] == "1000000000000000000000000000000.3"
    assert tally["source_value_gbp_decimal"] == tally["staged_value_gbp_decimal"]
    assert [row["external_value_gbp_decimal"] for row in rows] == [
        "1000000000000000000000000000000",
        "0.1",
        "0.2",
    ]


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
    (output / "RUN_MANIFEST.json").unlink()
    assert compute.main(args + ["--resume"]) == 0
    assert len(calls) == 12
    assert numerical == {name: (output / name).read_bytes() for name in numerical}
    assert (
        compute.main(args + ["--measures", first["measure_key"], "--years", "2024"])
        == 0
    )
    assert len(calls) == 14
    manifest = json.loads((output / "RUN_MANIFEST.json").read_bytes())
    assert len(manifest["artifacts"]) == len(manifest["artifact_grid"]) == 4
    assert len(manifest["requested_grid"]) == 1
    assert manifest["full_event_complete"] is True
    assert (
        numerical[f"{first['measure_key']}_2024.json"]
        == (output / f"{first['measure_key']}_2024.json").read_bytes()
    )
    (output / f"{first['measure_key']}_2024.json").write_text("{}")
    with pytest.raises(ValueError, match="retained artifact bytes"):
        compute.main(args + ["--resume"])
    assert len(calls) == 14


def test_cli_event_identity_checked_before_preflight(tmp_path, monkeypatch):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"event_slug": "another_event"}))
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda: (_ for _ in ()).throw(AssertionError("preflight must not run")),
    )
    with pytest.raises(ValueError, match="event identity"):
        compute.main(["--event", "test_event", "--registry", str(path)])
    with pytest.raises(ValueError, match="event identity"):
        stage.main(["--event", "test_event", "--registry", str(path)])


def test_focused_default_rerun_guard_precedes_preflight(tmp_path, monkeypatch):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    registry, output = compute.event_paths("test_event")
    registry.parent.mkdir(parents=True)
    registry.write_text(json.dumps({"calendar_years": [2024], "measures": [measure()]}))
    output.mkdir(parents=True)
    (output / "RUN_MANIFEST.json").write_text("{}")
    monkeypatch.setattr(
        compute.registry_builder, "validate_registry", lambda document: None
    )
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda: (_ for _ in ()).throw(AssertionError("preflight reached")),
    )
    args = ["--event", "test_event", "--measures", measure()["measure_key"]]
    with pytest.raises(ValueError, match="focused reruns"):
        compute.main(args)
    with pytest.raises(AssertionError, match="preflight reached"):
        compute.main(args + ["--resume"])
    with pytest.raises(AssertionError, match="preflight reached"):
        compute.main(args + ["--output-dir", str(tmp_path / "alternative")])


def test_interrupted_compute_resumes_only_receipted_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    first = measure()
    second = copy.deepcopy(first)
    second["measure_key"] = "test_event__second_measure"
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"calendar_years": [2024], "measures": [first, second]})
    )
    monkeypatch.setattr(
        compute.registry_builder, "validate_registry", lambda document: None
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

    def interrupted(year, variables, reform, pre):
        calls.append(reform)
        if len(calls) == 3:
            raise KeyboardInterrupt
        return simulation(900, 1000) if reform else simulation(1000, 1030)

    monkeypatch.setattr(compute, "run_sim", interrupted)
    output = tmp_path / "results"
    args = [
        "--event",
        "test_event",
        "--registry",
        str(registry),
        "--output-dir",
        str(output),
    ]
    with pytest.raises(KeyboardInterrupt):
        compute.main(args)
    assert not (output / "RUN_MANIFEST.json").exists()
    receipt = json.loads((output / "RUN_PROGRESS_2024.json").read_bytes())
    assert len(receipt["artifacts"]) == 1
    first_path = output / f"{first['measure_key']}_2024.json"
    first_bytes = first_path.read_bytes()
    unreceipted = output / f"{second['measure_key']}_2024.json"
    unreceipted.write_bytes(b"uncommitted interrupted output")
    calls.clear()

    def resumed(year, variables, reform, pre):
        calls.append(reform)
        return simulation(900, 1000) if reform else simulation(1000, 1030)

    monkeypatch.setattr(compute, "run_sim", resumed)
    assert compute.main(args + ["--resume"]) == 0
    assert len(calls) == 2  # One new baseline and the unfinished alternate only.
    assert first_path.read_bytes() == first_bytes
    assert json.loads(unreceipted.read_bytes())["measure_key"] == second["measure_key"]
    manifest = json.loads((output / "RUN_MANIFEST.json").read_bytes())
    assert manifest["full_event_complete"] is True
    assert len(manifest["artifact_grid"]) == 2


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
