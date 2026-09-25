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
        "null_executed_as_no_limit": [],
        "engine_version": "2.89.2",
        "data_bundle": "populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z",
        "run_id": "test",
        "computed_at": "2026-09-25T00:00:00+00:00",
        "_path": "results/uk/ab2025/test.json",
    }


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
    v, notes, reason = stg.map_claim(_claim("revenue_change"), art)
    assert reason is None and v == 0.0  # +10 tax, +10 spending
    v, _, _ = stg.map_claim(
        _claim("revenue_change", sign_convention="positive = cost to the Exchequer"),
        {
            **art,
            "totals": {
                "baseline": art["totals"]["baseline"],
                "reform": {**art["totals"]["reform"], "gov_spending": 50.0},
            },
        },
    )
    assert v == -10.0
    v, _, reason = stg.map_claim(_claim("revenue_change", tax_head="Income tax"), art)
    assert v is None and "OBR head-level" in reason


def test_poverty_counts_follow_the_claim_line_basis_and_population():
    art = _artifact()
    v, notes, reason = stg.map_claim(
        _claim(
            "poverty_count_change",
            "children",
            housing_costs="ahc",
            poverty_line="relative_60_median",
            unit_population="children",
        ),
        art,
    )
    assert reason is None and v == -100.0 and "children" in notes[0]
    v, notes, _ = stg.map_claim(
        _claim(
            "poverty_count_change",
            "persons",
            housing_costs="bhc",
            poverty_line="absolute_60_fye2011_median",
        ),
        art,
    )
    assert v == -100.0 and "absolute_bhc" in notes[0]
    v, _, _ = stg.map_claim(
        _claim("poverty_rate_change", "percentage_points", housing_costs="ahc"), art
    )
    assert v == pytest.approx(-1.0)


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


def test_unanswerable_shapes_are_tallied_not_guessed():
    art = _artifact()
    v, _, reason = stg.map_claim(_claim("gini", "index_0_1"), art)
    assert v is None and "no counterpart shape" in reason
    v, _, reason = stg.map_claim(_claim("revenue_change", geography="Scotland"), art)
    assert v is None and "geography" in reason


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
