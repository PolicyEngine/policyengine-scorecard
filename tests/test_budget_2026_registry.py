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


def test_already_announced_measures_raise_a_baseline_integrity_question():
    """Two measures are already law. The interesting question is not how
    to score them but whether the certified world's future baselines
    already carry them — if not, every counterpart at those years is
    measured against the wrong law."""
    flagged = [m for m in MEASURES.values() if m.get("baseline_integrity_flag")]
    assert len(flagged) == 2
    for m in flagged:
        assert m["reported_status"] == "already_announced"
        assert "baseline" in m["why"].lower()


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
