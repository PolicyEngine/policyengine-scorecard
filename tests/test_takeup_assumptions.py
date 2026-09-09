"""The take-up ASSUMPTION registry (#130), narrowed after review (#131).

Every other lane compares outputs. This one compares what the models
assume — but only where the two sides are the same kind of thing.
"""

import json

import pytest

from pipeline.validate_takeup_assumptions import (
    closed_cohort_parameters,
    comparable_parameters,
    load,
    validate,
)

REG = load()
PE = REG["policyengine_assumptions"]


def test_registry_validates():
    assert validate(REG) == len(PE) == 7


def test_the_four_ones_are_closed_cohorts_not_assumptions():
    """v1's error. These read 1.0 because the engine restricts
    eligibility to existing claimants — a denominator artifact, not a
    modelling choice about behaviour."""
    closed = {e["benefit"] for e in closed_cohort_parameters(REG).values()}
    assert closed == {
        "Housing Benefit",
        "Income Support",
        "Child Tax Credit",
        "Working Tax Credit",
    }
    for e in closed_cohort_parameters(REG).values():
        assert e["value_2026"] == 1.0
        assert "no new claims" in e["engine_description"]
        assert "BY CONSTRUCTION" in e["why_one"]
        assert e["comparable_to_an_open_programme_rate"] is False


def test_the_rationale_is_quoted_from_the_engine_not_asserted():
    """v1 read the values without reading the descriptions beside them.
    The description is the evidence, so it has to be present."""
    for e in closed_cohort_parameters(REG).values():
        assert "By definition, this is 100%" in e["engine_description"]


def test_validate_rejects_a_bare_one_with_no_rationale():
    bad = json.loads(json.dumps(REG))
    e = next(iter(closed_cohort_parameters(bad).values()))
    e["closed_cohort"] = False
    e["comparable_to_an_open_programme_rate"] = True
    with pytest.raises(ValueError, match="bigger claim"):
        validate(bad)


def test_validate_rejects_closed_cohort_asserted_without_the_engines_words():
    bad = json.loads(json.dumps(REG))
    next(iter(closed_cohort_parameters(bad).values()))["engine_description"] = "a rate"
    with pytest.raises(ValueError, match="without the engine's own"):
        validate(bad)


def test_what_survives_is_three_open_programme_rates():
    comparable = {e["benefit"] for e in comparable_parameters(REG).values()}
    assert comparable == {"Universal Credit", "Pension Credit", "income-based JSA"}
    for e in comparable_parameters(REG).values():
        assert "no new claims" not in e["engine_description"]


def test_the_universal_credit_spread_is_the_real_finding():
    """0.55 against 0.80 (RF) and 0.82 (the same engine, per the
    Scottish Government appendix) — open programmes both sides."""
    uc = PE["gov.dwp.universal_credit.takeup_rate"]
    assert uc["value_2026"] == 0.55
    assert uc["comparable_to_an_open_programme_rate"] is True
    finding = REG["the_finding"]
    assert "0.80" in finding and "0.82" in finding
    assert "25-27 point spread" in finding


def test_the_registry_records_that_it_overstated_v1():
    """A registry that quietly narrows its own claim is worse than one
    that never made it."""
    f = REG["the_finding"]
    assert "NARROWED after review" in f
    assert "WRONG, and unfair to PolicyEngine" in f
    assert "DTrim99" in f


def test_crossing_denominators_is_forbidden_not_merely_flagged():
    assert "may NOT be compared" in REG["comparability_rule"]
    axis = REG["divergence_axis"]
    assert "EXISTING CLAIMANTS" in axis and "ENTITLED" in axis


def test_validate_rejects_a_missing_comparability_rule():
    bad = json.loads(json.dumps(REG))
    bad["comparability_rule"] = "be careful"
    with pytest.raises(ValueError, match="what #131 caught"):
        validate(bad)


def test_the_ukmod_side_says_which_of_its_rows_are_comparable():
    note = REG["ukmod_assumptions"]["comparability_note"]
    assert "not comparable" in note
    assert "Pension Credit" in note


def test_the_ukmod_rates_are_attributed_to_their_originators():
    uk = REG["ukmod_assumptions"]
    assert any("DWP (2020)" in s for s in uk["originating_sources"])
    assert "SECOND-HAND" in uk["transcription_note"]


def test_the_registry_refuses_to_be_read_as_an_output_error():
    n = REG["not_a_conclusion"]
    assert "does NOT claim" in n
    assert "structural, not" in n
    assert "#76" in n


def test_it_stages_no_value_claims():
    assert "stages NO value claims" in REG["registry_rule"]
    blob = json.dumps(REG)
    for k in ("value", "claims", "caseload", "expenditure_gbp"):
        assert f'"{k}"' not in blob


def test_the_pin_follows_the_certified_world():
    assert REG["engine_pin"]["policyengine_uk"] == "2.89.2"
