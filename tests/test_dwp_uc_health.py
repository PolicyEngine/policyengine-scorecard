"""DWP UC Health statistics (lane dwp-uc-health, #87): the committed extract
is the adapter's output, the LCWRA rates add to their totals, and only the
new-claimant share has a counterpart until a certified-bundle run."""

import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

from scorecard_db import ingest_dwp_uc_health as uch
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.models import ComparisonStatus, Metric

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "dwp-uc-health"
EXTRACT = REPO / "data" / "externals" / "dwp-uc-health.json"


def _adapter():
    # unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(
        "dwp_uc_health_adapter", SRC / "adapter.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_raw_files_match_their_recorded_hashes():
    recorded = json.loads((SRC / "source.json").read_text())["raw_sha256"]
    for name, digest in recorded.items():
        assert hashlib.sha256((SRC / "raw" / name).read_bytes()).hexdigest() == digest


def test_committed_extract_is_the_adapters_output():
    pytest.importorskip("odf")
    pytest.importorskip("pandas")
    rows = _adapter().extract()
    assert rows == json.loads(EXTRACT.read_text())
    june = {
        r["subgroup"]: r["value"]
        for r in rows
        if r["period"] == "2026-06" and r["metric"] == "caseload"
    }
    assert june == {
        "total": 2_776_867,
        "higher_severe_conditions": 145_821,
        "higher_terminally_ill": 11_864,
        "higher_protected": 2_618_363,
        "lower_new_claimant": 815,
    }


def test_low_is_suppressed_and_parts_must_add_up():
    a = _adapter()
    assert a.count("[low]") is None
    assert a.count("423") == 423
    header = ["", *a.RATES]
    table = [[""]] * 5 + [header, ["April 2026", "100", "10", "1", "50", "[low]"]]
    with pytest.raises(ValueError, match="rates 61 vs total 100"):
        a.lcwra_rows(table)


def test_claims():
    scores = uch.stage()
    assert len(scores) == 16
    assert {s.calibration_relationship for s in scores} == {CR.HELD_OUT}
    suppressed = [s for s in scores if s.status == "suppressed"]
    assert [
        (s.conditions["month"], s.conditions["lcwra_rate"]) for s in suppressed
    ] == [("2026-04", "lower_new_claimant")]
    published = [s for s in scores if s.publication.get("publish_without_result")]
    assert len(published) == 14
    assert all(s.metric == Metric.CASELOAD for s in published)
    (share,) = [s for s in scores if s.metric == Metric.AFFECTED_SHARE]
    assert share.value == pytest.approx(815 / 2_776_867)


def test_only_the_share_has_a_result():
    scores = uch.stage()
    (r,) = uch.results(scores)
    assert r.status == ComparisonStatus.CONSTRUCTED
    assert r.computed_value == 0.11
    assert r.policyengine_variables == ["uc_LCWRA_element"]
    assert r.annotations[-1] == (
        "Measured: DWP lower-rate claimants 2026-04 [low], 2026-05 423, 2026-06 815."
    )


def test_lane_rows_in_the_built_db():
    db = REPO / "data" / "scorecard.db"
    if not db.exists():
        pytest.skip("scorecard.db not built")
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT s.metric, COUNT(DISTINCT s.claim_id), COUNT(r.id) FROM external_scores s "
        "LEFT JOIN pe_results r USING (claim_id) WHERE s.source = ? GROUP BY 1",
        (uch.SOURCE,),
    ).fetchall()
    conn.close()
    assert sorted(rows) == [("affected_share", 1, 1), ("caseload", 15, 0)]
