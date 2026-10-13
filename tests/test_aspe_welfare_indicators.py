"""ASPE Welfare Indicators, Indicator 4 (lane aspe-welfare-indicators): the
extract's rates recompute from its counts, the QC catches a revision or a
broken rate, and the ingest's claims, drops, statuses and relationships are
exact."""

import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_aspe_welfare_indicators as aspe
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.models import ComparisonStatus, Metric

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "aspe-welfare-indicators"
EXTRACT = REPO / "data" / "externals" / "aspe-welfare-indicators.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location("aspe_adapter", SRC / "adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows():
    return json.loads(EXTRACT.read_text())


def test_committed_extract_matches_contract():
    a = _adapter()
    rows = _rows()
    assert len(rows) == a.EXPECTED_ROWS
    assert Counter(r["program"] for r in rows) == {
        "tanf": 39 * 3,
        "snap": 40 * 3,
        "ssi": 31 * 9,
    }
    # "no data" (SNAP FY 2021) and "n.a." (SSI counts before 1998)
    suppressed = [r for r in rows if r["status"] == "suppressed"]
    assert len(suppressed) == 3 + 30 and all(r["value"] is None for r in suppressed)


def test_rates_recompute_from_the_extracts_counts():
    """The QC's interval check, re-run on the committed extract (no pypdf):
    reconstruct the published cells and call the adapter's qc."""
    a = _adapter()
    cells = {}
    for r in _rows():
        table = {"tanf": 10, "snap": 11, "ssi": 12}[r["program"]]
        label = r["period"].replace("FY ", "Fiscal Year ")
        col = {
            "eligible_count": "eligible",
            "participant_count": "participating",
            "participation_rate": "rate",
        }[r["metric"]]
        if table == 12:
            col = f"{r['subgroup']}|{col}"
        v = r["value"]
        cells[(table, label, col)] = (
            None
            if v is None
            else (round(v * 100, 1) if col.endswith("rate") else v / 1e6)
        )
    a.qc(cells, cells)  # an edition agrees with itself
    broken = dict(cells)
    broken[(10, "2023", "rate")] = 25.0
    with pytest.raises(ValueError, match="QC failed"):
        a.qc(broken, cells)


def test_edition_check_catches_a_silent_revision():
    a = _adapter()
    cur = {(10, "2022", "rate"): 21.9, (10, "2022", "eligible"): 3.839}
    prev = {(10, "2022", "rate"): 21.8, (10, "2022", "eligible"): 3.839}
    with pytest.raises(ValueError, match="revised"):
        a.qc(cur, prev)


def test_claims_drops_and_relationships():
    scores, drops = aspe.stage()
    assert len(scores) == 476
    assert drops == {"admin:snap_participating_households": 40}
    rel = Counter(
        (s.conditions["program"], s.metric, s.calibration_relationship) for s in scores
    )
    assert rel[("tanf", Metric.PARTICIPATION_RATE, CR.SEED_SOURCE)] == 39
    assert rel[("tanf", Metric.ELIGIBLE_COUNT, CR.HELD_OUT)] == 39
    assert rel[("snap", Metric.PARTICIPATION_RATE, CR.CONSUMED_AS_TARGET)] == 40
    assert rel[("ssi", Metric.PARTICIPANT_COUNT, CR.CONSUMED_AS_TARGET)] == 93
    assert rel[("ssi", Metric.ELIGIBLE_COUNT, CR.HELD_OUT)] == 93


def test_results_attach_to_the_latest_periods():
    scores, _ = aspe.stage()
    claims = {s.claim_id(): s for s in scores}
    results = aspe.results(scores)
    assert len(results) == 14
    windows = Counter(
        (
            claims[r.claim_id].conditions["program"],
            claims[r.claim_id].publication["window"],
        )
        for r in results
    )
    assert windows == {("tanf", "2023"): 3, ("snap", "FY 2022"): 2, ("ssi", "2023"): 9}
    for r in results:
        s = claims[r.claim_id]
        tanf_count = (
            s.conditions["program"] == "tanf" and s.metric != Metric.PARTICIPATION_RATE
        )
        want = (
            ComparisonStatus.CONCEPT_MISMATCH
            if tanf_count
            else ComparisonStatus.CONSTRUCTED
        )
        assert r.status == want
        assert r.computed_value > 0
        if s.metric == Metric.PARTICIPATION_RATE:
            assert r.computed_value < 1


def test_staged_counterpart_records_its_toggle_check():
    staged = json.loads((SRC / "pe" / "us-6.2.1.json").read_text())
    assert set(staged["toggle_check"]["federal_bbce_input_mean"].values()) == {0.0}
    assert set(staged["series"]) == {
        "tanf",
        "snap",
        "ssi_aged",
        "ssi_disabled",
        "ssi_couples",
    }
