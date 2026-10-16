"""Readback invariants without an engine or population."""

import json
import math
import sys
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from hypothesis import given, settings, strategies as st

from pipeline import compute_uk_ab2025 as worlds
from pipeline import compute_uk_event as compute
from pipeline import uk_construction_revisions as revisions

PATH = "gov.hmrc.cgt.basic_rate"
KEY = "autumn_budget_2024__capital_gains_main_rates_and_reliefs"


def simulation(value):
    parameter = lambda instant: value
    return SimpleNamespace(
        tax_benefit_system=SimpleNamespace(
            parameters=SimpleNamespace(
                gov=SimpleNamespace(
                    hmrc=SimpleNamespace(cgt=SimpleNamespace(basic_rate=parameter))
                )
            )
        )
    )


def check(value, year=2024):
    return {
        "event": "autumn_budget_2024",
        "measure_key": KEY,
        "year": year,
        "world": "baseline_world",
        "intended_values": {PATH: value},
    }


def test_exact_readback_accepts_and_bleed_shaped_readback_refuses():
    intended = 0.1 * 207 / 365 + 0.18 * 158 / 365
    bleed = 0.1 * 302 / 365 + 0.18 * 63 / 365
    assert compute.check_processed_parameters(
        simulation(intended), [check(intended)]
    ) == {PATH: intended}
    with pytest.raises(compute.ProcessedValueMismatch) as caught:
        compute.check_processed_parameters(simulation(bleed), [check(intended)])
    assert caught.value.failure == {
        "code": "processed_value_mismatch",
        "event": "autumn_budget_2024",
        "measure_key": KEY,
        "year": 2024,
        "world": "baseline_world",
        "path": PATH,
        "intended": intended,
        "processed": bleed,
    }


@pytest.mark.parametrize("intended", [1e-12, 0.1, 1.0, 1e12, -0.1])
def test_tolerance_is_relative_and_one_part_per_billion(intended):
    assert compute.processed_values_match(intended, intended * (1 + 0.5e-9))
    assert not compute.processed_values_match(intended, intended * (1 + 2e-9))
    # Kills an absolute-tolerance mutation even for small rates/amounts.
    assert not compute.processed_values_match(0.0, abs(intended) * 1e-12)
    assert compute.processed_values_match(0.0, 0.0)


@pytest.mark.parametrize("value", [None, math.nan, math.inf, -math.inf])
def test_missing_and_nonfinite_numeric_values_do_not_pass(value):
    assert not compute.processed_values_match(value, value)


@settings(max_examples=100, deadline=None)
@given(
    windows=st.dictionaries(
        st.tuples(st.integers(2020, 2030), st.integers(0, 10)),
        st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10,
    ),
    year=st.integers(2019, 2041),
)
def test_any_annual_windows_match_sampled_annual_lookup(windows, year):
    # Include overlapping windows: the engine applies dict entries in order.
    authored = {
        PATH: {
            f"{start}-01-01.{start + length}-12-31": value
            for (start, length), value in windows.items()
        }
    }
    annual = compute.annual_reform(authored)
    processed = 0.3
    for window, value in annual[PATH].items():
        start, stop = window.split(".")
        if start <= f"{year}-01-01" <= stop:
            processed = value
    intended = revisions.intended_value(annual, PATH, year, lambda path, instant: 0.3)
    assert compute.check_processed_parameters(
        simulation(processed), [check(intended, year)]
    ) == {PATH: processed}


def cgt_world():
    registry = json.loads(
        (compute.ROOT / "data/uk/events/autumn_budget_2024_measures.json").read_text()
    )
    index = {m["measure_key"]: m for m in registry["measures"]}
    return worlds.computable(index, years=registry["calendar_years"])[KEY]


def install_scenario(monkeypatch, *, statutory):
    class Scenario:
        @staticmethod
        def from_reform(reform):
            return SimpleNamespace(dated_reforms=[reform] if statutory else None)

    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk.utils.scenario",
        SimpleNamespace(Scenario=Scenario),
    )


def statutory_blend(reform, year):
    day = date(year, 4, 6)
    stop = date(year + 1, 4, 6)
    values = []
    while day < stop:
        value = 0.1 if day < date(2024, 10, 30) else 0.18
        for window, override in (reform or {}).get(PATH, {}).items():
            start, end = window.split(".")
            if start <= day.isoformat() <= end:
                value = override
        values.append(value)
        day += timedelta(days=1)
    return sum(values) / len(values)


@pytest.mark.parametrize("statutory", [False, True])
def test_revised_cgt_2024_matches_intent_and_preserves_neighboring_years(
    monkeypatch, statutory
):
    world = revisions.apply_revision(
        KEY, cgt_world(), lambda path: {"fiscal_year_blend": True}
    )
    annual = compute.annual_reform(world["baseline_reform"])
    install_scenario(monkeypatch, statutory=statutory)
    submitted = compute.revision_reform_route(annual, world["construction_revision"])
    for year in (2023, 2024, 2025, 2035, 2036):
        law = statutory_blend(None, year)
        intended = revisions.intended_value(annual, PATH, year, lambda p, d: law)
        processed = (
            statutory_blend(submitted, year)
            if statutory
            else revisions.intended_value(submitted, PATH, year, lambda p, d: law)
        )
        assert compute.check_processed_parameters(
            simulation(processed), [check(intended, year)]
        )[PATH] == pytest.approx(intended)
    if statutory:
        assert submitted[PATH] == {"2024-04-06.2036-04-05": 0.1}
    else:
        assert submitted == annual


def test_managed_check_runs_before_any_aggregate(tmp_path, monkeypatch):
    data = tmp_path / "certified.h5"
    data.write_bytes(b"fake certified data")
    sim = simulation(0.11)
    sim.policyengine_bundle = {
        "certified_data_build_id": "test",
        "runtime_dataset_source": str(data),
    }
    sim.tax_benefit_system.variables = {"capital_gains_tax": object()}
    calculated = []
    sim.calculate = lambda *args: calculated.append(args)
    monkeypatch.setitem(
        sys.modules,
        "policyengine",
        SimpleNamespace(
            uk=SimpleNamespace(managed_microsimulation=lambda **kwargs: sim)
        ),
    )
    with pytest.raises(compute.ProcessedValueMismatch):
        compute.fiscal.run_managed_simulation(
            year=2024,
            variables=["capital_gains_tax"],
            reform=None,
            runtime_dataset_source=data,
            expected_dataset_sha256=compute.fiscal.sha256_file(data),
            parameter_check=lambda own_sim: compute.check_processed_parameters(
                own_sim, [check(0.1)]
            ),
        )
    assert calculated == []


def test_artifact_records_both_worlds_and_legacy_omits_new_fields():
    from test_uk_event_compute import artifact, measure, simulation as aggregates

    baseline, reform = aggregates(900, 1000), aggregates(1000, 1030)
    for result, value in ((baseline, 0.2), (reform, 0.3)):
        result["processed_parameter_values"] = {"gov.tax.rate": value}
        result["parameter_reform_route"] = {
            "entry_point": "fake",
            "submitted_reform": None,
        }
    legacy = artifact(baseline, reform)
    assert "processed_parameter_values" not in legacy
    m = measure()
    world = worlds.worlds_for(m, {m["measure_key"]: m}, years=[2024])
    recorded = compute.build_artifact(
        measure=m,
        world=world,
        year=2024,
        baseline=baseline,
        reform=reform,
        certified=reform,
        registry_sha256="b" * 64,
        event="test_event",
        variant_fields={"variant_id": "test"},
    )
    assert recorded["processed_parameter_values"] == {
        "baseline_world": {"gov.tax.rate": {"intended": 0.2, "processed": 0.2}},
        "reform_world": {"gov.tax.rate": {"intended": 0.3, "processed": 0.3}},
    }


def test_refused_world_writes_integrity_failure_without_artifact(tmp_path, monkeypatch):
    from test_uk_event_compute import measure, simulation as aggregates

    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(compute, "check_variant_environment", lambda variant: {})
    monkeypatch.setattr(
        compute.registry_builder, "validate_registry", lambda document: None
    )
    monkeypatch.setattr(
        compute.worlds, "engine_resolver", lambda: lambda path, instant: 0.3
    )
    monkeypatch.setattr(
        compute,
        "preflight",
        lambda *args: {
            "sha256": "a" * 64,
            "release_bundle": {"certified_data_build_id": "test"},
        },
    )
    failure = {
        "code": "processed_value_mismatch",
        **{key: value for key, value in check(0.1).items() if key != "intended_values"},
        "path": PATH,
        "intended": 0.1,
        "processed": 0.11,
    }

    def run(year, variables, reform, pre):
        if reform:
            raise compute.ProcessedValueMismatch(failure)
        return aggregates()

    monkeypatch.setattr(compute, "run_sim", run)
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"calendar_years": [2024], "measures": [measure()]}))
    output = tmp_path / "results"
    with pytest.raises(compute.ProcessedValueMismatch):
        compute.main(
            [
                "--event",
                "test_event",
                "--registry",
                str(registry),
                "--output-dir",
                str(output),
            ]
        )
    assert json.loads((output / "INTEGRITY_FAILURES.json").read_text()) == [failure]
    assert list(output.glob("*.json")) == [output / "INTEGRITY_FAILURES.json"]


def test_integrity_exception_survives_year_worker_serialization():
    import pickle

    failure = {"code": "processed_value_mismatch", "processed": 0.11}
    exception = compute.ProcessedValueMismatch(failure)
    assert pickle.loads(pickle.dumps(exception)).failure == failure


def test_missing_processed_path_is_a_structured_mismatch():
    sim = SimpleNamespace(
        tax_benefit_system=SimpleNamespace(parameters=SimpleNamespace())
    )
    with pytest.raises(compute.ProcessedValueMismatch) as caught:
        compute.check_processed_parameters(sim, [check(0.1)])
    assert caught.value.failure["path"] == PATH
    assert caught.value.failure["intended"] == 0.1
    assert caught.value.failure["processed"] is None


def test_uc_constructor_guard_uses_structured_relative_check(monkeypatch):
    from test_uk_event_compute import uc_fakes

    calls = []
    uc_fakes(monkeypatch, calls, dated=True)
    intended = 437.66
    path = compute.UC_HEALTH_ELEMENT_PARAMETER
    reform = {path: {"2026-01-01.2029-12-31": intended}}
    # The old route silently leaves the parameter at 217.26. The guard runs
    # inside construction and must carry the same evidence as the outer hook.
    Scenario = sys.modules["policyengine_uk.utils.scenario"].Scenario
    original = Scenario.from_reform

    def broken(reform):
        scenario = original(reform)
        scenario.apply = lambda sim: None
        return scenario

    monkeypatch.setattr(Scenario, "from_reform", broken)
    sim = SimpleNamespace(
        health_parameter=217.26,
        tax_benefit_system=SimpleNamespace(
            reset_parameter_caches=lambda: None,
            parameters=SimpleNamespace(
                gov=SimpleNamespace(
                    dwp=SimpleNamespace(
                        universal_credit=SimpleNamespace(
                            rebalancing=SimpleNamespace(
                                new_claimant_health_element=lambda instant: 217.26
                            )
                        )
                    )
                )
            ),
        ),
    )
    checks = [{**check(intended, 2026), "intended_values": {path: intended}}]
    with pytest.raises(compute.ProcessedValueMismatch) as caught:
        compute.uc_health_scenario(reform, parameter_checks=checks).simulation_modifier(
            sim
        )
    assert caught.value.failure["path"] == path
    assert caught.value.failure["processed"] == 217.26
    assert "uc_modifier" not in calls

    # A difference within 1e-9 relative passes, although the previous absolute
    # assertion would have refused it before the general check ran.
    sim.tax_benefit_system.parameters.gov.dwp.universal_credit.rebalancing.new_claimant_health_element = (
        lambda instant: intended * (1 + 0.5e-9)
    )
    sim.health_parameter = intended
    compute.uc_health_scenario(reform, parameter_checks=checks).simulation_modifier(sim)
    assert "uc_modifier" in calls
