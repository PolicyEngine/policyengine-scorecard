"""The CGT alignment reform spec and its elasticity sweep (#97).

The Budget's flagship broad-based option, and three clean parameters in
PolicyEngine-UK. What is pinned here is the finding that reshaped the
lane: the engine's capital-gains response is OFF by default, so the
elasticity is an assumption this repo makes rather than something the
engine supplies — and an elasticity without a citation is an opinion
with a decimal point.
"""

import json

import pytest

from pipeline.validate_cgt_reform_spec import (
    load,
    publishable_legs,
    validate,
)

SPEC = load()
SWEEP = {s["label"]: s for s in SPEC["elasticity_sweep"]}


def test_spec_validates():
    assert validate(SPEC) is SPEC


def test_the_reform_is_three_clean_parameters():
    """18/24/24 today, aligned to the income tax bands 20/40/45."""
    assert SPEC["reform"] == {
        "gov.hmrc.cgt.basic_rate": 0.20,
        "gov.hmrc.cgt.higher_rate": 0.40,
        "gov.hmrc.cgt.additional_rate": 0.45,
    }
    assert SPEC["engine_baseline_2026"] == {
        "gov.hmrc.cgt.basic_rate": 0.18,
        "gov.hmrc.cgt.higher_rate": 0.24,
        "gov.hmrc.cgt.additional_rate": 0.24,
    }


def test_a_reform_that_restates_the_baseline_is_refused():
    """It would score zero and read as agreement."""
    bad = json.loads(json.dumps(SPEC))
    bad["reform"]["gov.hmrc.cgt.higher_rate"] = bad["engine_baseline_2026"][
        "gov.hmrc.cgt.higher_rate"
    ]
    with pytest.raises(ValueError, match="restates the baseline"):
        validate(bad)


# --- the finding that reshaped the lane -------------------------------------


def test_the_engine_response_is_off_by_default():
    """VERIFIED against 2.89.2: the elasticity is 0 from 2000-01-01 and
    capital_gains_behavioural_response short-circuits when it is. So a
    default PE-UK score of this measure is STATIC — the engine hands you
    machinery, not a behavioural number."""
    assert SPEC["engine_default_elasticity"] == 0.0
    finding = SPEC["behavioural_finding"]
    assert "VERIFIED against the certified engine" in finding
    assert "short-circuits" in finding
    assert "ASSUMPTION THIS REPO MAKES" in finding


def test_the_lane_sweeps_rather_than_picking_a_number():
    assert len(SPEC["elasticity_sweep"]) >= 2
    assert "static" in SWEEP
    assert SWEEP["static"]["value"] == 0.0


def test_only_the_static_leg_is_publishable_today():
    """The static leg asserts no behaviour, so it needs no external
    citation. Everything else is held until one exists."""
    pub = [s["label"] for s in publishable_legs(SPEC)]
    assert pub == ["static"]
    for label in ("central", "high_response"):
        assert SWEEP[label]["publishable"] is False
        assert SWEEP[label]["citation_required"] is True
        assert SWEEP[label]["value"] is None
        assert SWEEP[label]["note"].strip()


def test_an_uncited_elasticity_cannot_be_marked_publishable():
    """An elasticity without a citation is an opinion with a decimal
    point."""
    bad = json.loads(json.dumps(SPEC))
    leg = next(s for s in bad["elasticity_sweep"] if s["label"] == "central")
    leg["publishable"] = True
    leg["value"] = -0.7
    with pytest.raises(ValueError, match="opinion with a decimal point"):
        validate(bad)


def test_the_citation_must_state_which_elasticity_definition():
    """Semi-elasticity vs elasticity, and with respect to which rate, are
    different numbers wearing the same word."""
    note = SWEEP["central"]["note"]
    assert "semi-elasticity" in note
    assert "WHICH rate" in note


def test_a_sweep_with_no_static_leg_is_refused():
    bad = json.loads(json.dumps(SPEC))
    bad["elasticity_sweep"] = [
        s for s in bad["elasticity_sweep"] if s["label"] != "static"
    ]
    with pytest.raises(ValueError, match="wedge cannot be reported"):
        validate(bad)


# --- comparability -----------------------------------------------------------


def test_the_static_leg_is_never_comparable_to_a_behavioural_costing():
    """#67's finding, one level up: an OBR costing of this measure will be
    post-behavioural, and presenting a static PE number against it
    produces a divergence nobody can attribute."""
    rule = SPEC["comparison_rule"]
    assert "LIKE FOR LIKE" in rule
    assert "post-behavioural" in rule
    assert "not folded into a residual" in rule


def test_the_lane_says_it_has_not_run():
    """Same honesty as #51 and #66: the compute needs the managed
    environment and the certified bundle."""
    assert "unexecuted" in SPEC["not_yet_run"]
    assert "refuses without an explicit dataset" in SPEC["not_yet_run"]


def test_the_pin_follows_the_certified_world():
    """v1 of the re-certification moved this pin to 2.92.0, arguing a
    lane that has computed nothing is free to pin its verification
    engine. Too clever: this lane WILL be computed against the
    certified bundle, and pinning away from it made --resolve refuse
    there. Verification at an engine you cannot compute at is not
    useful verification."""
    rc = SPEC["recertification"]
    assert SPEC["engine_pin"]["policyengine_uk"] == "2.89.2"
    assert (
        "follows the certified populace-uk bundle" in SPEC["engine_pin"]["pin_meaning"]
    )
    assert "THE PIN FOLLOWS THE CERTIFIED WORLD" in rc["correction"]
    assert "no special case" in rc["correction"]
    # every baseline carries both readings, so the claim is checkable
    for path in SPEC["engine_baseline_2026"]:
        assert path in rc["readings"]
        assert "at_2_89_2" in rc["readings"][path]
        assert "at_2_92_0" in rc["readings"][path]


def test_the_basic_rate_float_artifact_is_recorded_not_enshrined():
    """basic_rate reads 0.18000000000000002 because the parameter is
    fiscal-year blended. The recorded baseline stays the legislated
    0.18 — writing the float artifact in as the rate would turn an
    arithmetic detail into a policy claim."""
    assert SPEC["engine_baseline_2026"]["gov.hmrc.cgt.basic_rate"] == 0.18
    note = SPEC["recertification"]["float_note"]
    assert "fiscal_year_blend" in note
    assert "NOT a policy" in note
    assert "1e-12" in note


def test_the_elasticity_finding_survived_the_bump():
    """If the engine had switched the response on by default, this
    lane's static/behavioural framing would need rewriting."""
    assert SPEC["engine_default_elasticity"] == 0.0
    assert "still 0" in SPEC["recertification"]["verdict"]


def test_the_bundle_constraint_is_recorded_with_its_source():
    """Self-review caught this: the pin moved to 2.92.0 while the
    certified bundle declares ==2.89.2, so 'verified at' and 'must run
    at' had silently diverged with nothing saying so. A registry that
    implies the newer engine is usable end to end would send a compute
    at an engine the data does not support."""
    c = SPEC["compute_engine_constraint"]
    assert c["required_specifier"] == "==2.89.2"
    assert c["bundle"]["compatible_model_packages"] == [
        {"name": "policyengine-uk", "specifier": "==2.89.2"}
    ]
    assert "needs a NEW certified bundle, not a pin edit" in c["note"]


def test_the_moved_pin_is_only_safe_because_the_readings_agree():
    """The per-path before/after readings are what license the move: if
    a value had differed between engines, a 2.89.2 compute against
    2.92.0-verified baselines would be wrong."""
    rc = SPEC["recertification"]
    assert "identical on 2.89.2 and 2.92.0" in rc["holds_on_both_engines"]
    for path, r in rc["readings"].items():
        assert abs(r["at_2_92_0"] - r["at_2_89_2"]) <= 1e-12, path


def test_the_bundle_is_identified_by_digest_not_by_name():
    b = SPEC["compute_engine_constraint"]["bundle"]
    assert b["revision"] == "populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z"
    assert len(b["sha256"]) == 64
