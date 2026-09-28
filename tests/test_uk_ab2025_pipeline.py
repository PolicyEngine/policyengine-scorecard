"""Engine-free tests for the tranche-3 runner and stager (#136).

The runner's world construction and the stager's claim mapping are pure
functions of the registry and of an artifact; the simulation is the one
part that needs the certified bundle, and it is not exercised here.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from pipeline import compute_uk_ab2025 as comp
from pipeline import stage_uk_ab2025 as stg
from scorecard_db.baselines import BASELINES
from scorecard_db.models import baseline_key

ROOT = Path(__file__).resolve().parent.parent
INDEX = comp.load_registry()
LABELS = {b[1]: baseline_key(b[0]) for b in BASELINES}


# --- worlds --------------------------------------------------------------------


def test_scalar_year_and_date_keys_become_periods():
    assert comp._windows(0.21) == [("2026-01-01.2035-12-31", 0.21)]
    assert comp._windows({"2027": 1, "2026": 2}) == [
        ("2026-01-01.2026-12-31", 2),
        ("2027-01-01.2027-12-31", 1),
    ]
    assert comp._windows({"2026-04-06": 5, "2027-04-06": 6}) == [
        ("2026-04-06.2027-04-05", 5),
        ("2027-04-06.2035-12-31", 6),
    ]
    with pytest.raises(ValueError, match="unparseable"):
        comp._windows({"soon": 1})


def test_a_null_executes_as_the_recorded_no_limit_sentinel():
    rd, sentinels = comp.reform_dict({"gov.x.cap": None, "gov.y.rate": 0.2})
    assert rd["gov.x.cap"] == {"2026-01-01.2035-12-31": comp.NO_LIMIT}
    assert sentinels == ["gov.x.cap"]


def test_reversal_executes_the_modifier_as_the_baseline_world():
    w = comp.worlds_for(INDEX["ab2025__uc_child_element_remove_two_child_limit"], INDEX)
    assert w["construction"] == "reversal_on_certified_world"
    assert w["reform_reform"] is None
    assert (
        w["baseline_reform"][
            "gov.dwp.universal_credit.elements.child.limit.child_count"
        ]["2026-01-01.2026-12-31"]
        == 2
    )


def test_an_option_executes_its_delta_as_the_reform_world():
    w = comp.worlds_for(INDEX["ab2025_option__income_tax_basic_rate_plus_1p"], INDEX)
    assert w["baseline_reform"] is None
    assert w["reform_reform"]["gov.hmrc.income_tax.rates.uk[0].rate"] == {
        "2026-01-01.2035-12-31": 0.21
    }


def test_a_package_composes_its_components_and_an_alias_points_at_its_lever():
    w = comp.worlds_for(INDEX["ab2025__package_ifs_decile_chart_scope"], INDEX)
    assert len(w["components"]) >= 5
    assert (
        "gov.dwp.universal_credit.elements.child.limit.child_count"
        in w["baseline_reform"]
    )
    assert comp.worlds_for(INDEX["ab2025_option__scrap_two_child_limit"], INDEX) == {
        "alias_of": "ab2025__uc_child_element_remove_two_child_limit"
    }


def test_every_expressible_measure_is_computable_or_listed():
    comp_ = comp.computable(INDEX)
    exp = [k for k, m in INDEX.items() if m["computability"] == "expressible"]
    missing = [k for k in exp if k not in comp_]
    assert missing == [], missing
    # by design (nothing to execute) is a reason, malformed is an error
    reasons = comp.not_computable(INDEX)
    assert reasons and all(reasons.values())
    assert not (set(reasons) & set(comp_))
    bad = {
        **INDEX,
        "ab2025__broken": {
            **INDEX["ab2025__dividend_rates_plus_2pp"],
            "measure_key": "ab2025__broken",
            "pe_baseline_modifier": None,
        },
    }
    with pytest.raises(ValueError, match="reversal without"):
        comp.worlds_for(bad["ab2025__broken"], bad)


def test_a_package_refuses_conflicting_components_and_executes_mixed_ones():
    a = INDEX["ab2025__dividend_rates_plus_2pp"]
    b = {
        **a,
        "measure_key": "x",
        "pe_baseline_modifier": {k: {"2026": 0.5} for k in a["pe_baseline_modifier"]},
    }
    idx = {
        **INDEX,
        "x": b,
        "pkg": {
            "measure_key": "pkg",
            "computability": "partial",
            "construction": "package_of_registry_measures",
            "package_of": ["ab2025__dividend_rates_plus_2pp", "x"],
        },
    }
    with pytest.raises(ValueError, match="differently"):
        comp.worlds_for(idx["pkg"], idx)
    mixed = {
        **INDEX,
        "pkg": {
            "measure_key": "pkg",
            "computability": "partial",
            "construction": "package_of_registry_measures",
            "package_of": [
                "ab2025__dividend_rates_plus_2pp",
                "ab2025_option__income_tax_basic_rate_plus_1p",
            ],
        },
    }
    # a package that reverses one component and applies another executes two
    # modified worlds (the mixed path): both sides, never merged into one
    w = comp.worlds_for(mixed["pkg"], mixed)
    assert w["baseline_reform"] and w["reform_reform"]


def test_weighted_quantile_groups_are_person_weighted():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    w = np.array([1.0, 1.0, 1.0, 97.0])
    g = comp._weighted_quantile_groups(x, w, 10)
    assert g[3] == 10 and g[0] == 1
    assert comp._weighted_median(x, w) == 4.0


# --- staging -------------------------------------------------------------------


def _artifact(
    measure_key="ab2025__uc_child_element_remove_two_child_limit", reversal=True
):
    def group(n):
        return [
            {
                "group": i + 1,
                "households": 100.0,
                "people": 250.0,
                "hni_baseline": 3_000_000.0,
                "hni_reform": 3_000_000.0 + 52_000.0 * (i + 1),
                "gaining_over_0": 60.0,
                "losing_over_0": 10.0,
                "gaining_over_0.01": 30.0,
                "losing_over_0.01": 5.0,
                "gaining_over_0.05": 4.0,
                "losing_over_0.05": 1.0,
            }
            for i in range(n)
        ]

    pov = {}
    for key in (
        "relative_60_median_moving_ahc",
        "relative_60_median_moving_bhc",
        "absolute_ahc",
        "absolute_bhc",
        "relative_60_median_fixed_at_baseline_ahc",
        "relative_60_median_fixed_at_baseline_bhc",
    ):
        pov[f"{key}__baseline"] = {"people": 1000.0, "children": 400.0}
        pov[f"{key}__reform"] = {"people": 900.0, "children": 300.0}
    return {
        "measure_key": measure_key,
        "year": 2026,
        "fy_proxy": "2026-27",
        "construction": "reversal_on_certified_world"
        if reversal
        else "forward_delta_on_certified_world",
        "components": [measure_key],
        "baseline_world": {
            "executed": "x",
            "reform_dict": {"p": {}} if reversal else None,
        },
        "reform_world": {"executed": "y", "reform_dict": None},
        "totals": {
            "baseline": {
                "gov_tax": 100.0,
                "gov_spending": 50.0,
                "people": 10000.0,
                "children": 2000.0,
            },
            "reform": {
                "gov_tax": 110.0,
                "gov_spending": 60.0,
                "people": 10000.0,
                "children": 2000.0,
            },
        },
        "poverty": pov,
        "distribution": {
            "bhc_decile": group(10),
            "ahc_decile": group(10),
            "bhc_vigintile": group(20),
            "ahc_vigintile": group(20),
            "all": {
                **group(1)[0],
                "households": 1000.0,
                "hni_baseline": 30_000_000.0,
                "hni_reform": 30_520_000.0,
            },
        },
        "affected": {"households": 7.0, "people": 9.0, "children": 3.0},
        "head_variables": ["universal_credit"],
        "null_executed_as_no_limit": [],
        "engine_version": "2.89.2",
        "data_bundle": "populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z",
        "run_id": "test",
        "computed_at": "2026-09-25T00:00:00+00:00",
        "_path": "results/uk/ab2025/test.json",
    }


YIELD = "positive = yield to the Exchequer (reduces borrowing); negative = cost"
OBR_NEG = "Note (verbatim): This table uses the convention that a negative figure means a reduction in PSNB."
OBR_POS = "Note (verbatim): A positive sign implies an increase in borrowing."
POV_UP = "positive = more people in poverty under the reform"
POV_DOWN = "positive = children lifted out of poverty"


def _claim(metric, unit="gbp", **cond):
    return {
        "claim_id": "c",
        "source": "t",
        "metric": metric,
        "period": 2027,
        "unit": unit,
        "value": 1.0,
        "conditions": {"measure_key": "k", "geography": "UK", **cond},
    }


def test_revenue_change_is_the_static_exchequer_effect_oriented_to_the_claim():
    art = _artifact()
    yield_art = {
        **art,
        "totals": {
            "baseline": art["totals"]["baseline"],
            "reform": {**art["totals"]["reform"], "gov_spending": 50.0},
        },
    }  # +10 tax, spending unchanged: a £10 yield
    v, notes, reason = stg.map_claim(
        _claim("revenue_change", sign_convention=YIELD), yield_art
    )
    assert reason is None and v == 10.0
    # the OBR states the opposite convention in two phrasings: both are costs
    for text in (OBR_NEG, OBR_POS, "positive = cost to the Exchequer"):
        v, _, _ = stg.map_claim(
            _claim("revenue_change", sign_convention=text), yield_art
        )
        assert v == -10.0, text
    v, _, reason = stg.map_claim(
        _claim("revenue_change", tax_head="Income tax", sign_convention=YIELD), art
    )
    assert v is None and "OBR head-level" in reason


def test_an_unrecognised_sign_convention_is_a_gap_not_a_default():
    art = _artifact()
    for text in (
        None,
        "as worded",
        "as worded: 'reduces the yield by' (positive = reduction in yield)",
    ):
        v, _, reason = stg.map_claim(
            _claim("revenue_change", sign_convention=text), art
        )
        assert v is None and reason, text
    v, _, reason = stg.map_claim(
        _claim("revenue_change", "percent_of_gdp", sign_convention=YIELD), art
    )
    assert v is None and "unit" in reason


def test_poverty_counts_follow_the_claim_line_basis_population_and_sign():
    art = _artifact()
    v, notes, reason = stg.map_claim(
        _claim(
            "poverty_count_change",
            "children",
            housing_costs="ahc",
            poverty_line="relative_60_median",
            unit_population="children",
            sign_convention=POV_UP,
        ),
        art,
    )
    assert reason is None and v == -100.0 and "children" in notes[0]
    # "lifted out of poverty" is the opposite orientation: PE's −100 becomes +100
    v, notes, _ = stg.map_claim(
        _claim(
            "poverty_count_change",
            "children",
            housing_costs="ahc",
            poverty_line="relative_60_median",
            sign_convention=POV_DOWN,
        ),
        art,
    )
    assert v == 100.0
    v, notes, _ = stg.map_claim(
        _claim(
            "poverty_count_change",
            "persons",
            housing_costs="bhc",
            poverty_line="absolute_60_fye2011_median",
            sign_convention=POV_UP,
        ),
        art,
    )
    assert v == -100.0 and "absolute_bhc" in notes[0]
    v, _, _ = stg.map_claim(
        _claim(
            "poverty_rate_change",
            "percentage_points",
            housing_costs="ahc",
            poverty_line="fixed_at_baseline",
            sign_convention=POV_UP,
        ),
        art,
    )
    assert v == pytest.approx(-1.0)
    # a basis, a line or a population PE did not compute is a gap
    for cond in (
        dict(poverty_line="relative_60_median", sign_convention=POV_UP),  # no basis
        dict(
            housing_costs="ahc",
            poverty_line="absolute_40_fye2011_median",
            sign_convention=POV_UP,
        ),
        dict(
            housing_costs="ahc",
            poverty_line="relative_60_median",
            subgroup="elderly",
            sign_convention=POV_UP,
        ),
        dict(
            housing_costs="ahc",
            poverty_line="relative_60_median",
            sign_convention="positive = children whose depth of poverty is reduced",
        ),
    ):
        v, _, reason = stg.map_claim(
            _claim("poverty_count_change", "persons", **cond), art
        )
        assert v is None and reason, cond


def test_group_shapes_use_the_baseline_world_groups():
    art = _artifact()
    v, notes, reason = stg.map_claim(
        _claim(
            "average_household_income_change",
            "gbp_per_week",
            income_group="decile_3",
            housing_costs="ahc",
        ),
        art,
    )
    assert reason is None and v == pytest.approx(52_000.0 * 3 / 100 / 52)
    v, notes, _ = stg.map_claim(
        _claim("pct_change_after_tax_income", "percent", income_group="vigintile_20"),
        art,
    )
    assert (
        v == pytest.approx(100 * 52_000.0 * 20 / 3_000_000.0) and "ASSUMED" in notes[0]
    )
    v, _, _ = stg.map_claim(
        _claim(
            "share_gaining",
            "share",
            income_group="all",
            threshold="1_percent_of_equivalised_ahc_disposable_income",
        ),
        art,
    )
    assert v == pytest.approx(30.0 / 1000.0)
    v, _, reason = stg.map_claim(
        _claim("share_losing", "share", income_group="bottom_half"), art
    )
    assert v is None and "income_group" in reason
    # income shares: a level share, or a change in percentage points, never mixed
    v, _, _ = stg.map_claim(
        _claim(
            "income_share",
            "share",
            income_group="decile_1",
            housing_costs="ahc",
            scenario="reform",
        ),
        art,
    )
    assert v == pytest.approx(3_052_000.0 / 30_520_000.0)
    v, _, _ = stg.map_claim(
        _claim(
            "income_share",
            "percentage_points",
            income_group="decile_1",
            housing_costs="ahc",
            scenario="reform_minus_baseline",
        ),
        art,
    )
    assert v == pytest.approx(
        100 * (3_052_000.0 / 30_520_000.0 - 3_000_000.0 / 30_000_000.0)
    )
    v, _, reason = stg.map_claim(
        _claim(
            "income_share",
            "percentage_points",
            income_group="decile_1",
            housing_costs="ahc",
            scenario="reform",
        ),
        art,
    )
    assert v is None and "income_share" in reason
    # units off the list are gaps
    v, _, reason = stg.map_claim(
        _claim(
            "average_household_income_change",
            "gbp_per_person",
            income_group="decile_1",
            housing_costs="ahc",
        ),
        art,
    )
    assert v is None and "unit" in reason
    v, _, _ = stg.map_claim(
        _claim(
            "average_household_income_change",
            "gbp_per_month",
            income_group="decile_1",
            housing_costs="ahc",
        ),
        art,
    )
    assert v == pytest.approx(52_000.0 / 100 / 12)


def test_unanswerable_shapes_are_tallied_not_guessed():
    art = _artifact()
    v, _, reason = stg.map_claim(_claim("gini", "index_0_1"), art)
    assert v is None and "no counterpart shape" in reason
    v, _, reason = stg.map_claim(
        _claim("revenue_change", geography="Scotland", sign_convention=YIELD), art
    )
    assert v is None and "geography" in reason
    # affected populations: persons, households or children, and only where
    # the measure names head variables
    v, _, _ = stg.map_claim(_claim("affected_count", "children"), art)
    assert v == 3.0
    v, _, reason = stg.map_claim(_claim("affected_count", "families"), art)
    assert v is None and "unit" in reason
    v, _, reason = stg.map_claim(
        _claim("affected_count", "persons"), {**art, "head_variables": []}
    )
    assert v is None and "no head variables" in reason


def test_executed_worlds_are_registered():
    art = _artifact()
    assert (
        stg.executed_world_key("ab2025__uc_child_element_remove_two_child_limit", art)
        == LABELS["pre_ab2025"]
    )
    assert (
        stg.executed_world_key("ab2025__dividend_rates_plus_2pp", art)
        == LABELS["pre_ab2025__dividend_rates_plus_2pp"]
    )
    assert (
        stg.executed_world_key("ab2025__package_ifs_decile_chart_scope", art)
        == LABELS["pre_ab2025__package_ifs_decile_chart_scope"]
    )
    fwd = _artifact("ab2025_option__income_tax_basic_rate_plus_1p", reversal=False)
    assert (
        stg.executed_world_key("ab2025_option__income_tax_basic_rate_plus_1p", fwd)
        == stg._CURRENT_LAW
    )
    with pytest.raises(ValueError, match="not registered"):
        stg.executed_world_key("ab2025__not_a_measure", art)
    # a variant on another measure's pre-Budget path executes THAT world: the
    # two-year option's modifier is the announced freeze's modifier verbatim
    key = "ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030"
    assert (
        INDEX[key]["pe_baseline_modifier"]
        == INDEX["ab2025__personal_tax_thresholds_freeze_to_2031"][
            "pe_baseline_modifier"
        ]
    )
    variant = {
        **art,
        "construction": "two_year_variant_of_ab2025__personal_tax_thresholds_freeze_to_2031",
    }
    assert (
        stg.executed_world_key(key, variant)
        == LABELS["pre_ab2025__personal_tax_thresholds_freeze_to_2031"]
    )


def test_a_claim_in_the_obr_costings_slice_is_owned_elsewhere():
    """The #56 / #140 rule: obr_measure_key marks the OBR costings lane's
    claims; the stager tallies them and never attaches, so no claim can
    carry two computed answers."""
    assert (
        stg.owned_elsewhere({"measure_key": "ab2025__dividend_rates_plus_2pp"}) is None
    )
    assert "OBR costings lane" in stg.owned_elsewhere(
        {
            "measure_key": "ab2025__dividend_rates_plus_2pp",
            "obr_measure_key": "autumn_budget_2025__dividend_income_rate_increase",
        }
    )


def test_only_a_lever_inert_in_every_year_is_inert():
    """Identical worlds in every year of the run: the lever did not bite,
    the measure is inert and its claims are tallied. Identical in some years
    and moving in others is not inert; whether such a year is a real zero is
    decided against the recorded commencement (next test)."""
    art = _artifact()
    same = {
        **art,
        "totals": {
            "baseline": art["totals"]["baseline"],
            "reform": art["totals"]["baseline"],
        },
    }
    assert stg.identical_worlds(same) and not stg.identical_worlds(art)
    # a head that moved while the aggregates did not is NOT identical
    b = {**art["totals"]["baseline"], "heads": {"scottish_child_payment": 1.0}}
    r = {**art["totals"]["baseline"], "heads": {"scottish_child_payment": 2.0}}
    assert not stg.identical_worlds({**art, "totals": {"baseline": b, "reform": r}})
    arts = {
        ("dead", 2026): same,
        ("dead", 2027): same,
        ("later", 2026): same,
        ("later", 2027): art,
    }
    assert stg.inert_measures(arts, [2026, 2027]) == {"dead"}
    # inertness is judged over the FULL run only: a --years subset raises
    with pytest.raises(ValueError, match="full run"):
        stg.inert_measures(arts, [2026, 2027, 2028])
    # identical in every run year because it commences after the run: not inert
    assert stg.inert_measures(arts, [2026, 2027], {"dead": "2031-32"}) == set()


def test_identical_worlds_are_a_zero_only_before_the_recorded_commencement():
    """'Not yet in force' is checked against the registry's commences_fy (from
    the HM Treasury Table 4.1 title), never inferred from world identity:
    identical worlds in a year the measure is in force, or with no recorded
    commencement, assert nothing (the student-loan freeze's 2030-31 was such a
    year before its pre-Budget world gained a 2030 leg)."""
    note, gap = stg.identical_year_verdict("2027-28", "2028-29")
    assert (
        gap is None and "not yet in force in FY 2027-28" in note and "2028-29" in note
    )
    note, gap = stg.identical_year_verdict("2030-31", "2027-28")
    assert note is None and "a year the measure is in force" in gap
    note, gap = stg.identical_year_verdict("2026-27", None)
    assert note is None and "no commencement on record" in gap


def test_every_executed_world_covers_the_run():
    """The mirror of the reversal guard, engine-free and so run in CI here: a
    year-keyed world that stops before the run ends reverts to current law
    and asserts a zero. The registry has no such world; a stub that stops
    early is flagged, and a recorded effect_ends_fy is honoured."""
    assert comp.world_coverage_gaps(INDEX) == []
    stub = {
        "m": {
            "measure_key": "m",
            "computability": "expressible",
            "construction": "reversal_on_certified_world",
            "pe_baseline_modifier": {"gov.a": {"2027": 1, "2028": 2, "2029": 3}},
            "head_variables": [],
        }
    }
    gaps = comp.world_coverage_gaps(stub)
    assert len(gaps) == 1 and "[2030]" in gaps[0] and "gov.a" in gaps[0]
    stub["m"]["effect_ends_fy"] = "2029-30"
    assert comp.world_coverage_gaps(stub) == []


def test_an_exchequer_effect_reads_the_head_the_aggregates_do_not_carry():
    """gov_tax and gov_spending unchanged while the measure's head moved: the
    certified engine's aggregates do not carry that head, so the exchequer
    effect is read from the head — receipts positive, outlays negative — and
    a head whose side is not recorded is unanswerable, never guessed."""
    art = _artifact()
    base = art["totals"]["baseline"]

    def with_head(name, delta):
        b = {**base, "heads": {name: 1.0}}
        r = {**base, "heads": {name: 1.0 + delta}}
        return {**art, "totals": {"baseline": b, "reform": r}}

    claim = _claim("revenue_change", sign_convention=YIELD)
    v, notes, reason = stg.map_claim(claim, with_head("student_loan_repayment", 5.0))
    assert reason is None and v == 5.0 and "read from the head" in notes[0]
    v, _, reason = stg.map_claim(claim, with_head("scottish_child_payment", 5.0))
    assert reason is None and v == -5.0
    v, _, reason = stg.map_claim(claim, with_head("some_other_head", 5.0))
    assert v is None and "side (receipt or outlay) is not recorded" in reason
    # aggregates that moved answer as before
    v, _, reason = stg.map_claim(claim, art)
    assert reason is None and v == (110.0 - 100.0) - (60.0 - 50.0)


def test_a_reversal_delta_must_restate_current_law():
    """A reversal never executes its pe_reform_delta (its reform world is
    current law), so a delta that differs from current law at the end of its
    window is a reform leg that would be dropped silently: refused."""
    index = {
        "ab2025__m": {
            "measure_key": "ab2025__m",
            "computability": "expressible",
            "construction": "reversal_on_certified_world",
            "pe_baseline_modifier": {"gov.a.b": {"2028": 1.0}},
            "pe_reform_delta": {"gov.a.b": {"2028": 2.0}, "gov.c": 7, "gov.d": None},
        }
    }
    # current law holds the announced level at commencement (6 April 2028)
    # and uprates it afterwards: a restatement, not a reform leg
    law = {"gov.a.b": {"2028-04-06": 2.0}, "gov.c": 7.0, "gov.d": float("inf")}

    def resolve(path, date):
        v = law.get(path)
        if v is None:
            return None
        return v.get(date, 9.9) if isinstance(v, dict) else v

    assert comp.reversal_delta_mismatches(index, resolve) == []
    law["gov.a.b"] = {"2028-04-06": 1.5}  # never 2.0 at any date: a dropped leg
    bad = comp.reversal_delta_mismatches(index, resolve)
    assert len(bad) == 1 and "gov.a.b = 2.0" in bad[0] and "dropped silently" in bad[0]
    del law["gov.c"]
    assert any(
        "does not resolve" in b for b in comp.reversal_delta_mismatches(index, resolve)
    )
    # every reversal in the registry restates current law at the pin: checked
    # against the engine by the runner's preflight and --dry-run; here the
    # shape is asserted: a reversal always carries its modifier
    for m in INDEX.values():
        if m.get("construction") == "reversal_on_certified_world":
            assert m.get("pe_baseline_modifier")


def test_a_mixed_construction_simulates_both_worlds_one_at_a_time(
    tmp_path, monkeypatch
):
    """A measure with a modifier AND a delta outside a reversal executes the
    modifier as the baseline world and the delta as the reform world, both
    simulated, the modified baseline released before the reform is built."""
    import weakref

    key = "ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030"
    worlds = comp.worlds_for(INDEX[key], INDEX)
    assert worlds["baseline_reform"] and worlds["reform_reform"]

    class Sim:
        def __init__(self, reform):
            self.reform = reform

    built = []
    alive = []

    def build_sim(reform):
        assert reform is not None, "a mixed construction never simulates current law"
        if alive:
            assert alive[-1]() is None, "two simulations alive at once"
        sim = Sim(reform)
        built.append(reform)
        alive.append(weakref.ref(sim))
        return sim

    def household_frame(sim, year, heads):
        scale = 1.0 if sim.reform is worlds["baseline_reform"] else 2.0
        n = 3
        return {
            "weight": np.ones(n),
            "people": np.ones(n),
            "children": np.zeros(n),
            "hni": np.full(n, 10.0 * scale),
            "gov_tax": np.full(n, 5.0 * scale),
            "gov_spending": np.zeros(n),
            "heads": {h: np.full(n, scale) for h in heads},
        }

    monkeypatch.setattr(comp, "build_sim", build_sim)
    monkeypatch.setattr(comp, "household_frame", household_frame)
    monkeypatch.setattr(comp, "poverty_block", lambda b, r: {})
    monkeypatch.setattr(comp, "distribution_block", lambda b, r: {})
    monkeypatch.setattr(comp, "affected_block", lambda b, r: None)
    monkeypatch.setattr(comp, "sha256_file", lambda p: "deadbeef")
    heads = INDEX[key]["head_variables"]
    base_frames = {
        2029: {
            "heads": {h: np.zeros(3) for h in heads},
            "weight": np.ones(3),
            "people": np.ones(3),
            "children": np.zeros(3),
            "hni": np.zeros(3),
            "gov_tax": np.zeros(3),
            "gov_spending": np.zeros(3),
        }
    }
    pre = {"artifact": tmp_path / "x.h5", "engine_version": "2.89.2", "revision": "r"}
    written = comp.run_measure(
        key, worlds, INDEX[key], [2029], base_frames, pre, "t", tmp_path
    )
    assert built == [worlds["baseline_reform"], worlds["reform_reform"]]
    art = json.loads(written[0].read_text())
    assert (
        art["baseline_world"]["executed"] == "certified world with pe_baseline_modifier"
    )
    assert art["reform_world"]["executed"] == "certified world with pe_reform_delta"
    assert (
        art["totals"]["baseline"]["gov_tax"] == 15.0
        and art["totals"]["reform"]["gov_tax"] == 30.0
    )
