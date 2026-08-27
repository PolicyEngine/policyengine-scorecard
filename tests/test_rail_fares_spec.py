"""The rail fares freeze spec (#105).

What is pinned here is the honesty of the specification: that the
counterfactual is a real change in the right direction, that the scope
mismatch is named before any comparison runs, and that the lane stages
none of DfT's numbers.
"""

import json

import pytest

from pipeline.validate_rail_fares_spec import load, validate

SPEC = load()


def test_spec_validates():
    assert validate(SPEC) == len(SPEC["years"]) == 3


def test_the_engine_ships_both_legs_of_the_counterfactual():
    """The reason this lane is cheap: #13 and #67 had to construct an
    indexed counterfactual by hand. Here it is a parameter."""
    assert SPEC["counterfactual"] == {
        "gov.dft.rail.fare_index": "gov.dft.rail.prior_law_fare_index"
    }
    for y in SPEC["years"]:
        r = SPEC["engine_readings"][str(y)]
        assert r["gov.dft.rail.prior_law_fare_index"] > r["gov.dft.rail.fare_index"], y


def test_the_freeze_gap_is_recorded_from_the_engine():
    r = SPEC["engine_readings"]["2026"]
    assert r["gov.dft.rail.fare_index"] == 1.217
    assert r["gov.dft.rail.prior_law_fare_index"] == 1.288


def test_validate_rejects_a_counterfactual_that_is_not_a_change():
    bad = json.loads(json.dumps(SPEC))
    bad["engine_readings"]["2026"]["gov.dft.rail.prior_law_fare_index"] = bad[
        "engine_readings"
    ]["2026"]["gov.dft.rail.fare_index"]
    with pytest.raises(ValueError, match="scores nothing"):
        validate(bad)


def test_validate_rejects_swapped_legs():
    """A spec with the legs swapped scores a fare CUT and still looks
    plausible — the failure mode a direction check exists for."""
    bad = json.loads(json.dumps(SPEC))
    r = bad["engine_readings"]["2027"]
    r["gov.dft.rail.fare_index"], r["gov.dft.rail.prior_law_fare_index"] = (
        r["gov.dft.rail.prior_law_fare_index"],
        r["gov.dft.rail.fare_index"],
    )
    with pytest.raises(ValueError, match="legs are swapped"):
        validate(bad)


def test_the_direction_is_checked_every_year_not_once():
    """A freeze that lapses mid-horizon would pass a single-year check."""
    bad = json.loads(json.dumps(SPEC))
    r = bad["engine_readings"]["2028"]
    r["gov.dft.rail.prior_law_fare_index"] = r["gov.dft.rail.fare_index"]
    with pytest.raises(ValueError, match="2028"):
        validate(bad)


def test_it_stages_no_value_claims():
    """DfT's saving figures belong to DfT (#86/#91)."""
    assert "stages NO value claims" in SPEC["registry_rule"]
    blob = json.dumps(SPEC)
    for k in ("value", "saving_gbp", "claims", "costing", "revenue_gbp"):
        assert f'"{k}"' not in blob


def test_validate_rejects_a_staged_figure():
    bad = json.loads(json.dumps(SPEC))
    bad["saving_gbp"] = 600_000_000
    with pytest.raises(ValueError, match="belong to DfT"):
        validate(bad)


def test_the_scope_mismatch_is_named_before_any_comparison():
    """Regulated fares are a minority of tickets and DfT counts
    passengers, not households. Unnamed, either gap gets attributed to
    the engine (#59)."""
    scope = SPEC["scope_conditions"]
    assert "MINORITY" in scope["regulated_share_note"]
    assert "per household" in scope["entity_mismatch"]


def test_validate_requires_the_scope_conditions():
    for key in ("regulated_share_note", "entity_mismatch"):
        bad = json.loads(json.dumps(SPEC))
        bad["scope_conditions"][key] = ""
        with pytest.raises(ValueError, match="attributed to the engine"):
            validate(bad)


def test_the_mechanism_is_recorded_from_the_engines_own_docstring():
    note = SPEC["mechanism_note"]
    assert "rail_usage x fare_index" in note
    assert "independently of usage quantity" in note


def test_no_counterpart_is_claimed_yet():
    """#51 carries UK counterpart compute and is not merged."""
    assert "#51" in SPEC["not_yet_run"]
    assert "computes no counterpart" in SPEC["not_yet_run"]
