"""The pe_gap verdicts for Autumn Budget 2025 claims (#136).

For every claim on a measure the certified engine cannot express, the
build writes one pe_results row with status pe_gap AND one diagnoses row
of class pe_gap carrying the registry's action_link. The result row is
what the comparisons view and the page show; the diagnosis row is the
only place the schema holds the link, and the descriptive register (#9)
refuses a pe_gap diagnosis without one. So "every pe_gap row carries its
action_link" is checked here as a fact of the DB.
"""

import json
import sqlite3
from pathlib import Path

from scorecard_db import ScorecardDB
from scorecard_db.ingest_uk_ab2025 import (
    REGISTRY,
    REGISTRY_MARK,
    VERDICT_COMPUTED_AT,
    VERDICT_RUN_ID,
    ingest,
    ingest_verdicts,
    verdict_rows,
)

ROOT = Path(__file__).resolve().parent.parent


def _fresh(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    ingest(db_path)
    return db_path


def test_every_gap_claim_gets_one_result_and_one_diagnosis(tmp_path):
    db_path = _fresh(tmp_path)
    out = ingest_verdicts(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    gap_claims = conn.execute(
        "SELECT claim_id, json_extract(conditions, '$.measure_key') AS k"
        " FROM external_scores WHERE json_extract(publication, '$.registry') = ?"
        " AND json_extract(conditions, '$.pe_expressibility') = 'not_expressible'",
        (REGISTRY_MARK,),
    ).fetchall()
    assert len(gap_claims) == out["pe_gap_results"] == out["pe_gap_diagnoses"] > 500
    results = conn.execute(
        "SELECT * FROM pe_results WHERE run_id = ?", (VERDICT_RUN_ID,)
    ).fetchall()
    assert len(results) == len(gap_claims)
    assert {r["claim_id"] for r in results} == {c["claim_id"] for c in gap_claims}
    for r in results:
        assert r["status"] == "pe_gap"
        assert r["computed_value"] is None
        assert r["computed_at"] == VERDICT_COMPUTED_AT
        assert r["pe_construction"].startswith("pe_gap:not_expressible:ab2025")
        notes = json.loads(r["annotations"])
        assert len(notes) == 3 and "Parameters:" in notes[1]
    diags = conn.execute(
        "SELECT * FROM diagnoses WHERE claim_id IN ("
        " SELECT claim_id FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?)",
        (REGISTRY_MARK,),
    ).fetchall()
    assert len(diags) == len(gap_claims)
    for d in diags:
        assert d["diagnosis_class"] == "pe_gap"
        assert d["action_link"].startswith("https://github.com/PolicyEngine/")
        assert d["rationale"]
    conn.close()


def test_no_pe_gap_row_lacks_a_link_in_the_comparisons_view(tmp_path):
    db_path = _fresh(tmp_path)
    ingest_verdicts(db_path)
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM comparisons WHERE pe_status = 'pe_gap'"
        " AND COALESCE(action_link, '') = ''"
    ).fetchone()[0]
    assert n == 0
    effective = conn.execute(
        "SELECT DISTINCT pe_status_effective FROM comparisons"
        " WHERE pe_status = 'pe_gap'"
    ).fetchall()
    assert effective == [("pe_gap",)]
    conn.close()


def test_expressible_measures_get_no_verdict_row(tmp_path):
    """A measure the engine can express waits for its counterpart run
    (tranche 3); a verdict row there would be a false gap."""
    db_path = _fresh(tmp_path)
    ingest_verdicts(db_path)
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_results r JOIN external_scores s USING (claim_id)"
        " WHERE r.run_id = ? AND json_extract(s.conditions, '$.pe_expressibility')"
        " != 'not_expressible'",
        (VERDICT_RUN_ID,),
    ).fetchone()[0]
    assert n == 0
    conn.close()


def test_verdicts_are_idempotent(tmp_path):
    db_path = _fresh(tmp_path)
    a = ingest_verdicts(db_path)
    b = ingest_verdicts(db_path)
    assert a == b
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id = ?", (VERDICT_RUN_ID,)
    ).fetchone()[0]
    assert n == a["pe_gap_results"]
    conn.close()


def test_the_gate_refuses_a_gap_without_a_link():
    import pytest

    with pytest.raises(ValueError, match="citable known issue"):
        ScorecardDB.diagnosis_row("x", "pe_gap", "why", "")


def test_verdict_rows_follow_the_registry(tmp_path):
    db_path = _fresh(tmp_path)
    db = ScorecardDB(db_path)
    results, diagnoses = verdict_rows(db)
    db.close()
    keys = {r[5].split(":", 2)[2] for r in results}
    for k in keys:
        assert REGISTRY[k]["computability"] == "not_expressible", k
    links = {d[3] for d in diagnoses}
    assert links <= {
        m["action_link"] for m in REGISTRY.values() if m.get("action_link")
    }
