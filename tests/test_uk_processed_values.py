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
    exact = compute.check_processed_parameters(simulation(intended), [check(intended)])
    assert exact == {PATH: intended}
    assert compute.processed_mismatches(check(intended), exact) == []
    read = compute.check_processed_parameters(simulation(bleed), [check(intended)])
    assert compute.processed_mismatches(check(intended), read) == [
        {
            "code": "processed_value_mismatch",
            "event": "autumn_budget_2024",
            "measure_key": KEY,
            "year": 2024,
            "world": "baseline_world",
            "path": PATH,
            "intended": intended,
            "processed": bleed,
        }
    ]


@pytest.mark.parametrize("intended", [1e-12, 0.1, 1.0, 1e12, -0.1])
def test_tolerance_is_relative_and_one_part_per_billion(intended):
    assert compute.processed_values_match(intended, intended * (1 + 0.5e-9))
    assert not compute.processed_values_match(intended, intended * (1 + 2e-9))
    # Kills an absolute-tolerance mutation even for small rates/amounts.
    assert not compute.processed_values_match(0.0, abs(intended) * 1e-12)
    assert compute.processed_values_match(0.0, 0.0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_numeric_values_do_not_pass(value):
    assert not compute.processed_values_match(value, value)


def test_a_missing_value_agrees_only_with_a_missing_value():
    assert compute.processed_values_match(None, None)
    assert not compute.processed_values_match(0.1, None)
    assert not compute.processed_values_match(None, 0.1)


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


def test_managed_readback_runs_before_any_aggregate(tmp_path, monkeypatch):
    data = tmp_path / "certified.h5"
    data.write_bytes(b"fake certified data")
    sim = simulation(0.11)
    sim.policyengine_bundle = {
        "certified_data_build_id": "test",
        "runtime_dataset_source": str(data),
    }
    sim.tax_benefit_system.variables = {"capital_gains_tax": object()}
    order, read_values = [], []

    class FirstAggregate(Exception):
        pass

    def calculate(*args, **kwargs):
        order.append("calculate")
        raise FirstAggregate

    sim.calculate = calculate
    monkeypatch.setitem(
        sys.modules,
        "policyengine",
        SimpleNamespace(
            uk=SimpleNamespace(managed_microsimulation=lambda **kwargs: sim)
        ),
    )

    def read(own_sim):
        order.append("read")
        read_values.append(compute.check_processed_parameters(own_sim, [check(0.1)]))
        return read_values[-1]

    with pytest.raises(FirstAggregate):
        compute.fiscal.run_managed_simulation(
            year=2024,
            variables=["capital_gains_tax"],
            reform=None,
            runtime_dataset_source=data,
            expected_dataset_sha256=compute.fiscal.sha256_file(data),
            parameter_check=read,
        )
    # The simulation's own tree is read before any aggregate is calculated.
    assert order == ["read", "calculate"]
    assert read_values == [{PATH: 0.11}]


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
    read = compute.check_processed_parameters(sim, [check(0.1)])
    assert read == {PATH: None}
    (failure,) = compute.processed_mismatches(check(0.1), read)
    assert failure["path"] == PATH
    assert failure["intended"] == 0.1
    assert failure["processed"] is None


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
    # The modifier no longer refuses inside construction: the managed runner's
    # readback reads this same simulation afterwards, and the decision is made
    # once both worlds are computed.
    compute.uc_health_scenario(reform, parameter_checks=checks).simulation_modifier(sim)
    assert "uc_modifier" in calls
    (failure,) = compute.processed_mismatches(
        checks[0], compute.check_processed_parameters(sim, checks)
    )
    assert failure["path"] == path
    assert failure["processed"] == 217.26
    # A difference within 1e-9 relative passes.
    sim.tax_benefit_system.parameters.gov.dwp.universal_credit.rebalancing.new_claimant_health_element = (
        lambda instant: intended * (1 + 0.5e-9)
    )
    assert (
        compute.processed_mismatches(
            checks[0], compute.check_processed_parameters(sim, checks)
        )
        == []
    )


def artifact_with(identical):
    heads = {"income_tax": 1.0}
    baseline = {
        "gov_tax": 1.0,
        "gov_spending": 2.0,
        "household_net_income": 3.0,
        "heads": dict(heads),
    }
    reform = (
        {**baseline, "heads": dict(heads)}
        if identical
        else {**baseline, "gov_tax": 1.5, "heads": {"income_tax": 1.5}}
    )
    return {"totals": {"baseline": baseline, "reform": reform}}


@pytest.mark.parametrize(
    "world", ["baseline_world", "reform_world", "certified_current_law"]
)
@pytest.mark.parametrize("year", [2025, 2027, 2028, 2030])
@pytest.mark.parametrize("identical", [True, False])
def test_a_mismatch_is_recorded_only_before_commencement_with_identical_worlds(
    world, year, identical
):
    measure = {"commences_fy": "2028-29"}
    mismatch = {
        "code": "processed_value_mismatch",
        "event": "autumn_budget_2025",
        "measure_key": "ab2025__high_value_council_tax_surcharge",
        "year": year,
        "world": world,
        "path": "gov.hmrc.council_tax.high_value_surcharge.amount[1].amount",
        "intended": 2500,
        "processed": 0,
    }
    refusals, notes = compute.processed_value_failures(
        measure, year, artifact_with(identical), [mismatch]
    )
    accepted = world != "certified_current_law" and year < 2028 and identical
    assert refusals == ([] if accepted else [mismatch])
    assert notes == (
        [{**mismatch, "accepted": "not_in_force_identical_worlds"}] if accepted else []
    )


@pytest.mark.parametrize("label", ["2028", "2028-99", "FY2028-29", "2028-2029", 2028])
def test_a_malformed_commencement_label_refuses_rather_than_defers(label):
    # Review of 4679c54: only a complete "YYYY-YY" label can defer a mismatch.
    mismatch = {"world": "baseline_world", "year": 2025}
    with pytest.raises(ValueError, match="invalid fiscal-year label"):
        compute.processed_value_failures(
            {"commences_fy": label}, 2025, artifact_with(True), [mismatch]
        )


@pytest.mark.parametrize("label", ["1999-00", "2028-29", "2099-00"])
def test_commencement_year_reads_consecutive_fiscal_years(label):
    assert compute.commencement_year(label) == int(label[:4])


def test_a_measure_without_commencement_is_always_in_force():
    mismatch = {"world": "baseline_world", "year": 2020}
    refusals, notes = compute.processed_value_failures(
        {}, 2020, artifact_with(True), [mismatch]
    )
    assert refusals == [mismatch] and notes == []


BLENDED = {
    "gov.hmrc.cgt.basic_rate": 0.1 * 207 / 365 + 0.18 * 158 / 365,
    "gov.hmrc.cgt.higher_rate": 0.2 * 207 / 365 + 0.24 * 158 / 365,
    "gov.hmrc.cgt.additional_rate": 0.2 * 207 / 365 + 0.24 * 158 / 365,
}


def window_value(reform, path, year):
    """A submitted window's value for period Y (1 January, or 6 April when the
    statutory route submits fiscal-year windows), else None."""
    for window, value in ((reform or {}).get(path) or {}).items():
        start, stop = window.split(".")
        anchor = f"{year}-04-06" if start.endswith("-04-06") else f"{year}-01-01"
        if start <= anchor <= stop:
            return value
    return None


def parameter_tree(values, leaf=lambda value: lambda instant: value):
    """A parameter tree; by default its leaves return the given period values."""
    root = {}
    for path, value in values.items():
        *parents, name_of_leaf = path.split(".")
        node = root
        for name in parents:
            node = node.setdefault(name, {})
        node[name_of_leaf] = leaf(value)

    def build(node):
        return SimpleNamespace(
            **{k: build(v) if isinstance(v, dict) else v for k, v in node.items()}
        )

    return build(root)


def variant_run(
    tmp_path,
    monkeypatch,
    measure,
    current,
    *,
    statutory=False,
    blend=False,
    corrupt=None,
    omit=False,
):
    """Run compute.main on one variant year with the managed runner faked.

    Each simulation's processed tree applies its submitted reform's windows over
    `current`. `corrupt` names the simulation ("certified", "baseline_world" or
    "reform_world") whose tree is off by 0.01; `omit` drops the evidence."""
    from test_uk_replay_variants import CURRENT, simulation as aggregates

    monkeypatch.setattr(compute, "ROOT", tmp_path)
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "event_slug": "autumn_budget_2024",
                "calendar_years": [2024],
                "measures": [measure],
            }
        )
    )
    monkeypatch.setattr(compute.registry_builder, "validate_registry", lambda d: None)
    monkeypatch.setattr(
        compute.worlds,
        "engine_resolver",
        lambda: lambda path, instant: current.get(path),
    )
    data = tmp_path / "certified.h5"
    data.write_bytes(b"fake")
    release = {"certified_data_build_id": "policyengine-uk-data-1.58.0"}
    monkeypatch.setattr(
        compute,
        "variant_preflight",
        lambda variant, dataset_source=None: {
            "sha256": variant["identity"]["dataset"]["sha256"],
            "release_bundle": release,
            "runtime_dataset_source": str(data),
        },
    )
    metadata = {"fiscal_year_blend": True} if blend else {}
    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk",
        SimpleNamespace(
            CountryTaxBenefitSystem=lambda: SimpleNamespace(
                parameters=parameter_tree(
                    {path: SimpleNamespace(metadata=metadata) for path in current},
                    leaf=lambda node: node,
                )
            )
        ),
    )
    install_scenario(monkeypatch, statutory=statutory)
    state = {"submitted": [], "calls": [], "world": None}

    def managed(**kwargs):
        reform = kwargs.get("reform")
        state["submitted"].append(reform)
        values = {}
        for path, law in current.items():
            value = window_value(reform, path, kwargs["year"])
            values[path] = law if value is None else value
            if state["world"] == corrupt:
                values[path] += 0.01
        result = aggregates(0, 0)
        result["aggregates_gbp"] = {
            variable: 1000.0 + 100 * len(state["calls"])
            for variable in kwargs["variables"]
        }
        result["variable_metadata"] = {
            variable: {"entity": "person", "definition_period": "year"}
            for variable in kwargs["variables"]
        }
        result["policyengine_bundle"] = dict(release)
        if kwargs.get("parameter_check") and not omit:
            sim = SimpleNamespace(
                tax_benefit_system=SimpleNamespace(parameters=parameter_tree(values))
            )
            result["processed_parameter_values"] = kwargs["parameter_check"](sim)
        return result

    monkeypatch.setattr(compute.fiscal, "run_managed_simulation", managed)
    run_sim = compute.run_sim

    def recording(year, variables, reform, pre):
        state["world"] = (
            "certified" if reform is None else pre["parameter_checks"][0]["world"]
        )
        state["calls"].append(
            {
                "reform": reform is not None,
                "checks": [
                    (check["world"], check["measure_key"])
                    for check in pre["parameter_checks"]
                ],
                "revision": pre.get("construction_revision"),
            }
        )
        return run_sim(year, variables, reform, pre)

    monkeypatch.setattr(compute, "run_sim", recording)
    state["output"] = (
        tmp_path / "results" / "uk" / "replays" / CURRENT / "autumn_budget_2024"
    )
    state["argv"] = [
        "--event",
        "autumn_budget_2024",
        "--variant",
        CURRENT,
        "--registry",
        str(registry_path),
        "--output-dir",
        str(state["output"]),
    ]
    return state


def ab2024_cgt():
    source = json.loads(
        (
            compute.registry_builder.ROOT
            / "data/uk/events/autumn_budget_2024_measures.json"
        ).read_text()
    )
    (cgt,) = [m for m in source["measures"] if m["measure_key"] == KEY]
    return cgt


@pytest.mark.parametrize("statutory", [False, True])
@pytest.mark.parametrize("blend", [True, False])
def test_a_variant_run_selects_the_revision_and_checks_each_world(
    tmp_path, monkeypatch, statutory, blend
):
    # Review of cce7cbb: the run path is pinned at compute.main with the real
    # AB2024 CGT measure, so dropping the revision selection or swapping the
    # worlds' checks fails here.
    run = variant_run(
        tmp_path, monkeypatch, ab2024_cgt(), BLENDED, statutory=statutory, blend=blend
    )
    assert compute.main(run["argv"]) == 0
    output, calls = run["output"], run["calls"]
    manifest = json.loads((output / "RUN_MANIFEST.json").read_bytes())
    artifact = json.loads((output / f"{KEY}_2024.json").read_bytes())
    # The certified baseline is the reform world (current law) and also reads
    # current law; the reversal world carries its own check and the revision.
    assert calls == [
        {
            "reform": False,
            "checks": [("reform_world", KEY), ("certified_current_law", KEY)],
            "revision": None,
        },
        {
            "reform": True,
            "checks": [("baseline_world", KEY)],
            "revision": artifact.get("construction_revision"),
        },
    ]
    (reversal,) = [r for r in run["submitted"] if r]
    recorded = artifact["processed_parameter_values"]
    if blend:
        assert KEY in manifest["construction_revisions"]
        assert artifact["construction_revision"]["revision_id"] == (
            "ab2024_cgt_fiscal_year_blend.v2"
        )
        window = "2024-04-06.2036-04-05" if statutory else "2024-01-01.2035-12-31"
        assert reversal[PATH] == {window: 0.1}
        # The reversal world holds the pre-announcement rate through FY2024-25.
        assert recorded["baseline_world"][PATH] == {"intended": 0.1, "processed": 0.1}
    else:
        assert "construction_revisions" not in manifest
        assert "construction_revision" not in artifact
        # The frozen reversal reads from 2025: period 2024 keeps current law.
        assert recorded["baseline_world"][PATH] == {
            "intended": BLENDED[PATH],
            "processed": BLENDED[PATH],
        }
    # The reform world is the certified current law in both cases.
    assert recorded["reform_world"][PATH] == {
        "intended": BLENDED[PATH],
        "processed": BLENDED[PATH],
    }
    assert "processed_value_notes" not in artifact


def two_world_measure():
    from test_uk_event_compute import measure

    return {
        **measure("delta_on_modified_baseline"),
        "pe_reform_delta": {"gov.tax.rate": 0.25},
    }


@pytest.mark.parametrize(
    ("measure", "current", "corrupt", "refused"),
    [
        # A reversal: the reform world is the certified simulation.
        (ab2024_cgt, BLENDED, "baseline_world", "baseline_world"),
        (ab2024_cgt, BLENDED, "certified", "reform_world"),
        # Both worlds modified: only the current-law readback sees the
        # certified simulation.
        (two_world_measure, {"gov.tax.rate": 0.3}, "baseline_world", "baseline_world"),
        (two_world_measure, {"gov.tax.rate": 0.3}, "reform_world", "reform_world"),
        (
            two_world_measure,
            {"gov.tax.rate": 0.3},
            "certified",
            "certified_current_law",
        ),
    ],
)
def test_a_variant_run_refuses_a_wrong_processed_world(
    tmp_path, monkeypatch, measure, current, corrupt, refused
):
    # Review of 4679c54: the decision after both worlds run is exercised through
    # the managed runner, not by raising from a faked run_sim.
    run = variant_run(
        tmp_path, monkeypatch, measure(), current, blend=True, corrupt=corrupt
    )
    with pytest.raises(compute.ProcessedValueMismatch) as refusal:
        compute.main(run["argv"])
    assert refusal.value.failure["world"] == refused
    assert refusal.value.failure["processed"] == pytest.approx(
        refusal.value.failure["intended"] + 0.01
    )
    output = run["output"]
    assert json.loads((output / "INTEGRITY_FAILURES.json").read_bytes()) == [
        refusal.value.failure
    ]
    assert not list(output.glob("*_2024.json"))
    assert not (output / "RUN_MANIFEST.json").exists()


def test_a_two_world_variant_run_checks_both_worlds_and_current_law(
    tmp_path, monkeypatch
):
    run = variant_run(tmp_path, monkeypatch, two_world_measure(), {"gov.tax.rate": 0.3})
    assert compute.main(run["argv"]) == 0
    key = "test_event__tax_and_benefit"
    assert run["calls"] == [
        {"reform": False, "checks": [("certified_current_law", key)], "revision": None},
        {"reform": True, "checks": [("baseline_world", key)], "revision": None},
        {"reform": True, "checks": [("reform_world", key)], "revision": None},
    ]
    artifact = json.loads((run["output"] / f"{key}_2024.json").read_bytes())
    assert artifact["processed_parameter_values"] == {
        "baseline_world": {"gov.tax.rate": {"intended": 0.2, "processed": 0.2}},
        "reform_world": {"gov.tax.rate": {"intended": 0.25, "processed": 0.25}},
    }


def test_a_variant_run_refuses_a_world_without_processed_evidence(
    tmp_path, monkeypatch
):
    run = variant_run(tmp_path, monkeypatch, ab2024_cgt(), BLENDED, omit=True)
    with pytest.raises(RuntimeError, match="processed parameter evidence"):
        compute.main(run["argv"])
    assert not list(run["output"].glob("*_2024.json"))
