"""Does the certified world carry the law legislated into its future? (#99)

The repo has a baselines registry that DESCRIBES worlds and ingests that
stamp which world a run executed. Nothing checked that the certified
world CONTAINS the measures already legislated into the years it
computes at — a gap that is quiet by construction, because the resulting
divergence gets attributed to whatever axis the analyst reaches for.
"""

import json
from pathlib import Path

import pytest

from pipeline.check_baseline_integrity import (
    VERDICTS,
    affected_claims,
    load,
    validate,
)

ROOT = Path(__file__).resolve().parent.parent
REG = load()
BY = {m["key"]: m for m in REG["measures"]}


def test_registry_validates():
    assert validate(REG) == 5


def test_every_verdict_carries_the_probe_that_produced_it():
    """A verdict without a probe is an opinion."""
    for k, m in BY.items():
        assert m["verdict"] in VERDICTS, k
        assert m["probe"], k
        assert m["evidence"].strip(), k


def test_validate_rejects_a_verdict_with_no_probe():
    bad = json.loads(json.dumps(REG))
    bad["measures"][0]["probe"] = {}
    with pytest.raises(ValueError, match="a verdict without one is an opinion"):
        validate(bad)


# --- the good news is recorded, not just the bad -----------------------------


def test_the_two_child_abolition_is_in_the_baseline():
    """2 in 2025, unbounded from 2026 — which also confirms the registered
    pre_ab2025 world is a real counterfactual rather than a restatement
    of the baseline."""
    m = BY["ab2025__two_child_limit_abolition"]
    assert m["verdict"] == "carried"
    assert m["probe"]["2025"] == 2.0
    assert m["probe"]["2026"] == float("inf")
    assert "pre_ab2025" in m["evidence"]


def test_the_threshold_freeze_is_the_baseline_not_the_reform():
    m = BY["freeze__income_tax_thresholds"]
    assert m["verdict"] == "carried"
    assert m["probe"]["2026"] == m["probe"]["2028"] == 12570.0
    assert "INDEXED counterfactual" in m["evidence"]


def test_a_measure_with_no_parameter_can_still_be_verified():
    """No single parameter encodes 'a freeze was extended'. Rather than
    guess, it was checked against the OBR's own scored CPI profile: the
    sign flips negative in 2026-27 and positive in 2027-28, the signature
    of a freeze that ends and catches up."""
    m = BY["ab2025__fuel_duty_freeze_extension"]
    assert m["verdict"] == "consistent"
    assert m["probe"]["2026"] < m["probe"]["2027"] < m["probe"]["2028"]
    assert "-0.129pp" in m["evidence"] and "+0.076pp" in m["evidence"]
    assert "obr-policy-effects.json" in m["evidence"]


def test_a_consistent_verdict_must_be_argued_not_asserted():
    """It is the verdict that could be wishful thinking, so it carries
    the heaviest evidence requirement."""
    bad = json.loads(json.dumps(REG))
    m = next(x for x in bad["measures"] if x["verdict"] == "consistent")
    m["evidence"] = "looks fine"
    with pytest.raises(ValueError, match="could be wishful thinking"):
        validate(bad)


# --- and the gaps are located, not just noticed -----------------------------


def test_the_missing_measures_are_probed_and_located():
    for key, period in (
        ("ab2025__high_value_council_tax_surcharge", 2028),
        ("announced__property_income_tax_rates", 2027),
    ):
        m = BY[key]
        assert m["verdict"] == "missing"
        assert all(v is None for v in m["probe"].values()), key
        assert m["affected_from_period"] == period
        assert m["consequence"].strip(), key


def test_a_missing_measure_must_say_which_claims_it_affects():
    """An unlocated gap cannot be caveated."""
    bad = json.loads(json.dumps(REG))
    m = next(x for x in bad["measures"] if x["verdict"] == "missing")
    m["consequence"] = ""
    with pytest.raises(ValueError, match="must say WHICH claims"):
        validate(bad)
    bad2 = json.loads(json.dumps(REG))
    m2 = next(x for x in bad2["measures"] if x["verdict"] == "missing")
    del m2["affected_from_period"]
    with pytest.raises(ValueError, match="without affected_from_period"):
        validate(bad2)


@pytest.mark.skipif(not (ROOT / "data" / "scorecard.db").exists(), reason="no built DB")
def test_the_exposure_envelope_is_real_and_quantified():
    """Not a defect count — a claim inside the envelope is computed at a
    horizon where the certified world is missing law that exists, and
    whether that moves the claim depends on the quantity. The point is
    that it is currently neither triaged nor visible."""
    envelope = affected_claims(REG)
    assert envelope["announced__property_income_tax_rates"]["uk_claims"] > 0
    assert envelope["ab2025__high_value_council_tax_surcharge"]["uk_claims"] > 0
    # 2028 is a subset of 2027
    assert (
        envelope["ab2025__high_value_council_tax_surcharge"]["uk_claims"]
        <= envelope["announced__property_income_tax_rates"]["uk_claims"]
    )


def test_the_envelope_is_described_as_an_envelope_not_a_defect_count():
    src = (ROOT / "pipeline" / "check_baseline_integrity.py").read_text()
    assert "EXPOSURE ENVELOPE, not a defect count" in src
    assert "does not touch a taxpayer count" in src
