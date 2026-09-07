"""The take-up ASSUMPTION registry (#130).

Every other lane compares outputs. This one compares what the two
models assume, which is why it can say something without waiting on
the compute in #76.
"""

import json

import pytest

from pipeline.validate_takeup_assumptions import (
    full_take_up_parameters,
    load,
    validate,
)

REG = load()
PE = REG["policyengine_assumptions"]


def test_registry_validates():
    assert validate(REG) == len(PE) == 7


def test_four_benefits_assume_full_take_up():
    """The finding. PolicyEngine assumes everyone entitled claims, for
    four benefits where DWP and HMRC publish non-take-up."""
    full = {e["benefit"] for e in full_take_up_parameters(REG).values()}
    assert full == {
        "Housing Benefit",
        "Income Support",
        "Child Tax Credit",
        "Working Tax Credit",
    }
    for e in full_take_up_parameters(REG).values():
        assert e["value_2026"] == 1.0


def test_the_ukmod_counterparts_are_materially_lower():
    """0.32 for WTC with no children is not a rounding difference."""
    r = REG["ukmod_assumptions"]["rates"]
    assert r["Housing Benefit"]["working_age_in_work"] == 0.57
    assert r["Child Tax Credit + Working Tax Credit"]["wtc_no_children"] == 0.32
    assert r["Income Support"]["without_children"] == 0.89
    assert r["Pension Credit"]["savings_only"] == 0.37


def test_the_schedules_are_recorded_because_staleness_is_half_the_finding():
    """A single value hides that UC's rate is dated 2015."""
    assert PE["gov.dwp.universal_credit.takeup_rate"]["first_dated"] == "2015-01-01"
    assert PE["gov.dwp.pension_credit.takeup"]["first_dated"] == "2015-01-01"
    for e in PE.values():
        assert e["schedule"], e["benefit"]


def test_validate_rejects_a_missing_schedule():
    bad = json.loads(json.dumps(REG))
    next(iter(bad["policyengine_assumptions"].values()))["schedule"] = {}
    with pytest.raises(ValueError, match="how OLD"):
        validate(bad)


def test_the_entitlement_versus_receipt_axis_is_named():
    """Where full take-up is assumed, the model produces an entitlement
    count and the administrative benchmark is a receipt count. Unnamed,
    that difference gets attributed to the engine."""
    axis = REG["divergence_axis"]
    assert "ENTITLEMENT" in axis and "RECEIPT" in axis
    assert "#59" in axis


def test_validate_rejects_full_take_up_without_the_axis():
    bad = json.loads(json.dumps(REG))
    bad["divergence_axis"] = "take-up differs a bit"
    with pytest.raises(ValueError, match="unnamed axis"):
        validate(bad)


def test_the_ukmod_rates_are_attributed_to_their_originators():
    """The rates are DWP's and HMRC's; UKMOD's table is a transcription
    (#86/#91)."""
    uk = REG["ukmod_assumptions"]
    assert any("DWP (2020)" in s for s in uk["originating_sources"])
    assert any("HMRC (2019)" in s for s in uk["originating_sources"])
    assert "SECOND-HAND" in uk["transcription_note"]


def test_the_mechanism_difference_is_stated():
    """Household-level per-benefit allocation is not a national scalar,
    so only the assumed aggregate rate is comparable."""
    note = REG["ukmod_assumptions"]["mechanism_note"]
    assert "HOUSEHOLD level" in note
    assert "ASSUMED AGGREGATE RATE" in note


def test_the_registry_refuses_to_be_read_as_an_output_error():
    """Calibration and reported-recipient anchoring may bring outputs
    closer than the bare parameter implies."""
    n = REG["not_a_conclusion"]
    assert "does NOT claim" in n
    assert "reported-recipient anchoring" in n
    assert "#76" in n


def test_validate_requires_that_disclaimer():
    bad = json.loads(json.dumps(REG))
    bad["not_a_conclusion"] = ""
    with pytest.raises(ValueError, match="not an output error"):
        validate(bad)


def test_it_stages_no_value_claims():
    assert "stages NO value claims" in REG["registry_rule"]
    blob = json.dumps(REG)
    for k in ("value", "claims", "caseload", "expenditure_gbp"):
        assert f'"{k}"' not in blob


def test_the_pin_follows_the_certified_world():
    pin = REG["engine_pin"]
    assert pin["policyengine_uk"] == "2.89.2"
    assert "certified populace-uk bundle" in pin["pin_meaning"]
