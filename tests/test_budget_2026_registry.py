"""The Autumn Budget 2026 scoreability registry (#96).

A pre-event registry: what each reported measure would BE as a
PolicyEngine-UK reform, and whether the certified engine can express it,
so a counterpart can be computed on 28 October rather than started then.

What is pinned here is the honesty of the triage — that expressible was
resolved rather than asserted, that every gap names itself, and that the
registry states the WHOLE reported package including the half a
household model cannot touch.
"""

import json
from pathlib import Path

import pytest

from pipeline.validate_budget_2026_registry import (
    COMPUTABILITY,
    REPORTED_STATUS,
    load,
    validate,
)

REG = load()
MEASURES = {m["measure_key"]: m for m in REG["measures"]}


def test_registry_validates():
    assert validate(REG) == len(REG["measures"]) == 14


def test_the_two_false_gaps_are_corrected():
    """v1 recorded both of these not_expressible on GUESSED paths that
    failed to resolve. Both are expressible, and both are already in the
    certified baseline — so neither is a Budget-day scoring job."""
    for key, leaf, want in (
        (
            "ab2026__property_income_tax_rate_rise",
            "gov.hmrc.income_tax.rates.property.basic",
            0.20,
        ),
        (
            "ab2026__high_value_council_tax_surcharge",
            "gov.hmrc.council_tax.high_value_surcharge.amount[1].amount",
            2500.0,
        ),
    ):
        m = MEASURES[key]
        assert m["computability"] == "expressible", key
        assert m["already_in_baseline"] is True, key
        assert m["engine_baseline_2026"][leaf] == want, key
        assert "CORRECTED" in m["note"], key
        assert "why" not in m, key


def test_a_gap_claim_needs_a_name_search_not_a_guessed_path():
    """--resolve cannot catch a false gap, because a not_expressible
    entry carries no path to resolve. That is exactly how v1's two got
    through. So the claim must be backed by a search of the tree."""
    for k, m in MEASURES.items():
        if m["computability"] == "not_expressible" and not m.get("out_of_model_scope"):
            assert "Searched the whole parameter tree" in m["name_search"], k


def test_validate_rejects_an_unsearched_gap_claim():
    bad = json.loads(json.dumps(REG))
    m = next(
        x
        for x in bad["measures"]
        if x["computability"] == "not_expressible" and not x.get("out_of_model_scope")
    )
    m["name_search"] = ""
    with pytest.raises(ValueError, match="NAME SEARCH"):
        validate(bad)


def test_the_provenance_rule_citation_is_precise():
    """#86 is the lane; the rule was established in its PR, #91."""
    note = REG["provenance_rule_note"]
    assert "#91" in note and "#86" in note
    assert "the RULE was established in its PR" in note


def test_it_is_a_scoreability_registry_not_a_claims_lane():
    """The revenue figures in circulation are journalism citing third
    parties, and the #86 rule applies: a re-published figure belongs to
    its originator. So this file stages no values."""
    assert "stages NO value claims" in REG["registry_rule"]
    blob = json.dumps(REG)
    for numeric_claim_key in ("value", "revenue_gbp", "costing", "claims"):
        assert f'"{numeric_claim_key}"' not in blob


def test_the_event_is_pinned():
    assert REG["event_date"] == "2026-10-28"
    assert REG["fiscal_event"] == "autumn_budget_2026"
    assert REG["chancellor"] == "John Healey"


def test_every_measure_says_where_it_was_reported():
    for k, m in MEASURES.items():
        assert m["source_note"].strip(), k
        assert m["reported_status"] in REPORTED_STATUS, k
        assert m["computability"] in COMPUTABILITY, k


# --- expressible means RESOLVED --------------------------------------------


def test_the_flagship_measure_is_a_clean_parameter_reform():
    """CGT alignment is the most-reported broad-based option, and it is
    three parameters. The recorded baselines are what a real
    policyengine-uk 2.89.2 returns for 2026 — 18% / 24% / 24% — not
    numbers copied from reporting."""
    m = MEASURES["ab2026__cgt_align_with_income_tax_rates"]
    assert m["computability"] == "expressible"
    assert m["pe_reform_delta"] == {
        "gov.hmrc.cgt.basic_rate": 0.20,
        "gov.hmrc.cgt.higher_rate": 0.40,
        "gov.hmrc.cgt.additional_rate": 0.45,
    }
    assert m["engine_baseline_2026"]["gov.hmrc.cgt.basic_rate"] == 0.18
    assert m["engine_baseline_2026"]["gov.hmrc.cgt.higher_rate"] == 0.24


def test_the_cgt_measure_records_that_behaviour_is_the_whole_argument():
    m = MEASURES["ab2026__cgt_align_with_income_tax_rates"]
    note = m["behavioural_note"]
    assert "capital_gains_behavioural_response" in note
    assert "static-only PE number would not be comparable" in note


def test_expressible_measures_record_an_engine_baseline_to_check_against():
    for k, m in MEASURES.items():
        if m["computability"] == "expressible":
            assert m.get("engine_baseline_2026"), k
            assert set(m["engine_baseline_2026"]) == set(m["pe_reform_delta"]), k


def test_a_freeze_is_not_treated_as_a_delta_on_current_law():
    """A threshold freeze is only measurable against an INDEXED
    counterfactual — the axis #67 found undecomposed on the OBR's own
    PA/HRT re-estimates."""
    m = MEASURES["ab2026__personal_allowance_freeze_extension"]
    note = m["baseline_construction_note"]
    assert "INDEXED counterfactual" in note
    assert "#13" in note and "#67" in note


# --- gaps have to name themselves ------------------------------------------


def test_the_pensions_gap_survived_the_re_check():
    """The other two gaps did not. This one was verified by name search:
    no lump|commencement|tax_free_cash|pcls node anywhere in the tree."""
    m = MEASURES["ab2026__pension_tax_free_lump_sum_restriction"]
    assert m["computability"] == "not_expressible"
    assert "no nodes" in m["name_search"]


def test_the_pensions_measure_gap_was_verified_not_assumed():
    """The most-reported pensions measure of this Budget cannot be scored
    at all: gov.hmrc.pensions has no tax-free lump sum parameter at the
    certified pin. That was probed, not guessed."""
    m = MEASURES["ab2026__pension_tax_free_lump_sum_restriction"]
    assert m["computability"] == "not_expressible"
    assert "VERIFIED, not assumed" in m["why"]
    assert "AttributeError" in m["why"]
    assert m["policyengine_uk_development_item"] is True


def test_every_gap_is_either_an_upstream_item_or_out_of_scope():
    for k, m in MEASURES.items():
        if m["computability"] == "not_expressible":
            assert m["why"].strip(), k
            assert m.get("policyengine_uk_development_item") or m.get(
                "out_of_model_scope"
            ), k


def test_validate_rejects_an_unexplained_gap():
    bad = json.loads(json.dumps(REG))
    m = next(x for x in bad["measures"] if x["computability"] == "not_expressible")
    m["why"] = ""
    with pytest.raises(ValueError, match="without a named gap"):
        validate(bad)


def test_validate_rejects_an_expressible_measure_with_no_delta():
    bad = json.loads(json.dumps(REG))
    m = next(x for x in bad["measures"] if x["computability"] == "expressible")
    m["pe_reform_delta"] = None
    with pytest.raises(ValueError, match="carries no reform delta"):
        validate(bad)


# --- the whole package, including what we cannot touch ----------------------


def test_the_unmodellable_half_is_stated_not_omitted():
    """Roughly half the reported Budget is business levies a household
    microsimulation cannot touch. Listing only the modellable measures
    would overstate coverage."""
    out_of_scope = [m for m in MEASURES.values() if m.get("out_of_model_scope")]
    assert len(out_of_scope) >= 5
    for m in out_of_scope:
        assert m["computability"] == "not_expressible"
        assert "no firm entity" in m["why"]


def test_validate_rejects_a_registry_that_hides_the_unmodellable_half():
    bad = json.loads(json.dumps(REG))
    bad["measures"] = [m for m in bad["measures"] if not m.get("out_of_model_scope")]
    with pytest.raises(ValueError, match="overstate coverage"):
        validate(bad)


def test_the_already_announced_measures_are_confirmed_in_the_baseline():
    """v1 raised these two as an OPEN question — did the certified
    world's future baselines carry measures already in law? It then
    answered it the wrong way, recording both as engine gaps. Reading
    the tree settled it: both are carried, with the dated schedules.
    So the question is closed, not flagged."""
    announced = [
        m for m in MEASURES.values() if m["reported_status"] == "already_announced"
    ]
    assert len(announced) == 2
    for m in announced:
        assert m["already_in_baseline"] is True
        assert m["computability"] == "expressible"
        assert m["engine_baseline_2026"], m["measure_key"]
        # no open flag and no gap prose survives the correction
        assert not m.get("baseline_integrity_flag")
        assert "why" not in m


def test_a_ruled_out_measure_is_kept_as_a_counterfactual():
    m = MEASURES["ab2026__council_tax_and_sdlt_to_land_value_tax"]
    assert m["reported_status"] == "ruled_out_for_this_budget"
    assert m["computability"] == "partial"
    assert "model the hole, not the replacement" in m["missing"]


def test_the_wealth_tax_entry_separates_expressible_from_credible():
    """Expressible does not mean credible. The schedule applies to
    survey-imputed wealth, the weakest data in the certified world for
    exactly the population the measure targets."""
    m = MEASURES["ab2026__wealth_tax_2pc_above_10m"]
    assert m["computability"] == "expressible"
    assert "Expressible does NOT mean credible" in m["caveat"]
    assert "survey-imputed wealth" in m["caveat"]
