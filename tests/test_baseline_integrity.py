"""Does the certified world carry the law legislated into its future? (#99)

Version 1 of this registry published TWO FALSE ENGINE GAPS. Both came
from the same mistake — guessing a parameter path, watching it fail to
resolve, and recording that as absence — and neither was caught, because
the only function that queries the engine was gated behind a flag no
test and no workflow ever passed. CI checked the registry against its
own recorded numbers.

So the tests here pin the DISCIPLINE that stops it recurring, and the
engine half now runs in .github/workflows/baseline-probe.yml.
"""

import json
import re
from pathlib import Path

import pytest

from pipeline.check_baseline_integrity import (
    VERDICTS,
    baseline_gaps,
    load,
    validate,
)

ROOT = Path(__file__).resolve().parent.parent
REG = load()
BY = {m["key"]: m for m in REG["measures"]}


def test_registry_validates():
    assert validate(REG) == 6


def test_the_file_is_strict_json():
    """v1 wrote bare `Infinity` literals. Python accepts them; the JSON
    spec does not, and the app side would fail to parse."""
    raw = (ROOT / "data" / "uk" / "baseline_integrity.json").read_text()
    assert not re.search(r":\s*(Infinity|-Infinity|NaN)\b", raw)
    json.loads(raw)


# --- the mistake that produced two false gaps -------------------------------


def test_a_probe_records_its_kind():
    """Collapsing SUBTREE into ABSENT is what did it: a path that exists
    but is not a scalar raises, and v1 read that as 'no such parameter'."""
    for k, m in BY.items():
        for reading in m["probe"]:
            assert reading["kind"] in ("scalar", "subtree", "absent"), k
            # and each reading says where it came from, so a re-probe
            # re-runs exactly that rather than reconstructing a path
            assert reading["path"] and reading["date"], k


def test_validate_rejects_a_kindless_probe():
    bad = json.loads(json.dumps(REG))
    bad["measures"][0]["probe"][0] = 12570.0
    with pytest.raises(ValueError, match="must record its KIND"):
        validate(bad)


def test_validate_rejects_a_reading_with_no_path():
    """Reconstructing a path from a key name was itself a source of
    false readings while this registry was being repaired."""
    bad = json.loads(json.dumps(REG))
    del bad["measures"][0]["probe"][0]["path"]
    with pytest.raises(ValueError, match="must record the PATH and DATE"):
        validate(bad)


def test_an_absent_verdict_requires_a_name_search():
    """An absent verdict asserts the engine cannot do something. A
    guessed path that fails to resolve proves nothing."""
    for k, m in BY.items():
        if m["verdict"] == "absent":
            assert m["name_search"].strip(), k
            assert "Searched the whole parameter tree" in m["name_search"], k


def test_validate_rejects_an_absent_verdict_without_one():
    bad = json.loads(json.dumps(REG))
    m = next(x for x in bad["measures"] if x["verdict"] == "absent")
    m["name_search"] = ""
    with pytest.raises(ValueError, match="must record the NAME SEARCH"):
        validate(bad)


def test_the_corrections_are_kept_not_dropped():
    """The two false gaps are part of this registry's evidence."""
    log = " ".join(REG["corrections_log"])
    assert "property income tax" in log.lower() or "rates.property" in log
    assert "high_value_surcharge" in log
    assert "FALSE ENGINE GAP" in log
    assert "DTrim99" in log


def test_validate_rejects_dropping_the_corrections_log():
    bad = json.loads(json.dumps(REG))
    bad["corrections_log"] = []
    with pytest.raises(ValueError, match="corrections_log is empty"):
        validate(bad)


# --- the corrected verdicts --------------------------------------------------


def test_property_income_rates_are_carried_after_all():
    m = BY["announced__property_income_tax_rates"]
    assert m["verdict"] == "carried"
    readings = {(r["path"], r["date"]): r for r in m["probe"]}
    assert (
        readings[("gov.hmrc.income_tax.rates.property", "2027-06-01")]["kind"]
        == "subtree"
    )
    assert (
        readings[("gov.hmrc.income_tax.rates.property.basic", "2026-06-01")]["value"]
        == 0.20
    )
    assert (
        readings[("gov.hmrc.income_tax.rates.property.basic", "2027-06-01")]["value"]
        == 0.22
    )
    assert (
        readings[("gov.hmrc.income_tax.rates.property.higher", "2027-06-01")]["value"]
        == 0.42
    )
    assert "CORRECTED" in m["evidence"]


def test_the_council_tax_surcharge_is_carried_after_all():
    m = BY["ab2025__high_value_council_tax_surcharge"]
    assert m["verdict"] == "carried"
    amounts = sorted(r["value"] for r in m["probe"] if r["path"].endswith(".amount"))
    thresholds = sorted(
        r["value"] for r in m["probe"] if r["path"].endswith(".threshold")
    )
    assert amounts == [0.0, 2500.0, 3500.0, 5000.0, 7500.0]
    assert thresholds == [2_000_000.0, 2_500_000.0, 3_500_000.0, 5_000_000.0]
    assert all(r["kind"] == "scalar" for r in m["probe"])
    assert "below-threshold band" in m["evidence"]


def test_the_only_absent_measure_is_not_a_baseline_gap():
    """The pension lump sum is not law, so the baseline is CORRECT to
    omit it. That is a scoring capability gap, not a baseline failure."""
    m = BY["reported__pension_tax_free_lump_sum"]
    assert m["verdict"] == "absent"
    assert m["scoring_gap_not_baseline_gap"] is True
    assert baseline_gaps(REG) == []


def test_the_honest_headline_is_that_nothing_is_missing():
    """After correction, every legislated measure checked is carried.
    The tooling is the deliverable, not a finding."""
    verdicts = {
        m["verdict"]
        for m in REG["measures"]
        if not m.get("scoring_gap_not_baseline_gap")
    }
    assert verdicts <= {"carried", "consistent"}


def test_the_fuel_duty_evidence_flags_its_unmerged_artifact():
    """The OBR scoring it rests on is not on main — it arrives with #81."""
    m = BY["ab2025__fuel_duty_freeze_extension"]
    assert m["verdict"] == "consistent"
    assert m["evidence_artifact_unmerged"] is True
    assert "NOT" in m["evidence"] and "#81" in m["evidence"]


# --- the check now actually runs --------------------------------------------


def test_the_engine_probe_is_wired_into_a_workflow():
    """v1's reprobe() was gated behind a flag nothing ever passed."""
    wf = ROOT / ".github" / "workflows" / "baseline-probe.yml"
    assert wf.exists()
    text = wf.read_text()
    assert "check_baseline_integrity.py --probe" in text
    assert "policyengine-uk==" in text
    assert "schedule:" in text  # notices the engine moving with no diff
