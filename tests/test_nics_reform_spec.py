"""The salary-sacrifice NI cap spec (#109).

What is pinned here is that the lane cannot publish a PolicyEngine
incidence assumption as if it were arithmetic.
"""

import json

import pytest

from pipeline.validate_nics_reform_spec import EMPRESP, HAIRCUT, load, validate

SPEC = load()


def test_spec_validates():
    assert validate(SPEC) == len(SPEC["assumption_sweep"]) == 3


def test_the_measure_is_carried_in_the_certified_baseline():
    """The #99/#101 question, answered for this measure."""
    ev = SPEC["baseline_evidence"]
    assert SPEC["baseline_verdict"] == "carried"
    assert ev["schedule"]["2028"] is None  # uncapped
    assert ev["schedule"]["2029"] == 2000.0  # the announced cap
    assert ev["schedule"]["2030"] == 2000.0


def test_the_january_dating_is_recorded_as_checked_not_as_a_defect():
    """The step is dated 2029-01-01 while the measure starts April
    2029. Every gov.hmrc.national_insurance parameter uses 01-01."""
    note = SPEC["baseline_evidence"]["checked_and_not_a_finding"]
    assert "module-wide convention" in note
    assert "not an anomaly" in note


def test_validate_rejects_a_schedule_with_no_step():
    """A schedule showing only one state cannot evidence 'carried'."""
    bad = json.loads(json.dumps(SPEC))
    bad["baseline_evidence"]["schedule"] = {"2029": 2000.0, "2030": 2000.0}
    with pytest.raises(ValueError, match="BOTH an uncapped period"):
        validate(bad)


def test_validate_rejects_a_lapsing_cap():
    """The announced measure only ever switches on."""
    bad = json.loads(json.dumps(SPEC))
    bad["baseline_evidence"]["schedule"]["2031"] = None
    with pytest.raises(ValueError, match="LAPSE"):
        validate(bad)


# --- the finding: the default is not assumption-neutral --------------------


def test_the_two_assumptions_point_opposite_ways():
    ap = SPEC["assumption_parameters"]
    assert ap[HAIRCUT]["engine_default"] == 0.0016
    assert ap[HAIRCUT]["state"] == "ON"
    assert ap[EMPRESP]["engine_default"] == 0.0
    assert ap[EMPRESP]["state"] == "OFF"


def test_the_haircut_hits_everyone_not_just_sacrificers():
    ap = SPEC["assumption_parameters"][HAIRCUT]
    assert "ALL workers" in ap["applies_to"]
    assert "np.isinf(cap)" in ap["gated_on"]
    assert "PolicyEngine research" in ap["provenance"]


def test_the_finding_distinguishes_itself_from_the_cgt_lane():
    """#97's default asserted NO behaviour. This one asserts some."""
    f = SPEC["the_finding"]
    assert "not HMRC's and not OBR's" in f
    assert (
        "there the default asserted no behaviour and here the default asserts some" in f
    )


def test_validate_notices_if_the_haircut_default_ever_becomes_zero():
    """If it did, this lane's whole finding would evaporate — better to
    fail than to keep asserting it."""
    bad = json.loads(json.dumps(SPEC))
    bad["assumption_parameters"][HAIRCUT]["engine_default"] = 0
    with pytest.raises(ValueError, match="this lane's finding would not exist"):
        validate(bad)


def test_validate_notices_if_the_asymmetry_disappears():
    bad = json.loads(json.dumps(SPEC))
    bad["assumption_parameters"][EMPRESP]["engine_default"] = 0.2
    with pytest.raises(ValueError, match="ASYMMETRY"):
        validate(bad)


# --- disclosure is stronger than citation here -----------------------------


def test_every_leg_running_the_haircut_must_disclose_it():
    for leg in SPEC["assumption_sweep"]:
        if leg["haircut_rate"]:
            assert leg["disclosure_required"] is True, leg["label"]


def test_validate_rejects_publishing_the_haircut_undisclosed():
    bad = json.loads(json.dumps(SPEC))
    leg = next(x for x in bad["assumption_sweep"] if x["haircut_rate"])
    leg["disclosure_required"] = False
    with pytest.raises(ValueError, match="as if it were arithmetic"):
        validate(bad)


def test_an_assumption_free_leg_exists_for_the_official_costing():
    """A static official costing needs a comparable PE leg."""
    clean = [
        l
        for l in SPEC["assumption_sweep"]
        if not l["haircut_rate"] and l["publishable"]
    ]
    assert clean, "no assumption-free publishable leg"
    assert clean[0]["employee_reduction_rate"] == 0.0


def test_validate_requires_an_assumption_free_leg():
    bad = json.loads(json.dumps(SPEC))
    for leg in bad["assumption_sweep"]:
        leg["haircut_rate"] = 0.0016
        leg["disclosure_required"] = True
    with pytest.raises(ValueError, match="no comparable PE leg"):
        validate(bad)


def test_an_uncited_response_leg_is_not_publishable():
    leg = next(l for l in SPEC["assumption_sweep"] if l["citation_required"])
    assert leg["publishable"] is False
    assert leg["employee_reduction_rate"] is None


def test_the_published_comparison_must_name_its_leg():
    assert "must state which sweep leg it is" in SPEC["comparison_rule"]
    assert len(SPEC["divergence_axes"]) == 3


def test_it_stages_no_value_claims():
    assert "stages NO value claims" in SPEC["registry_rule"]
    blob = json.dumps(SPEC)
    for k in ("value", "revenue_gbp", "claims", "costing", "yield_gbp"):
        assert f'"{k}"' not in blob


def test_validate_rejects_a_staged_figure():
    bad = json.loads(json.dumps(SPEC))
    bad["yield_gbp"] = 4_500_000_000
    with pytest.raises(ValueError, match="belong to"):
        validate(bad)


def test_no_counterpart_is_claimed_yet():
    assert "#51" in SPEC["not_yet_run"]
