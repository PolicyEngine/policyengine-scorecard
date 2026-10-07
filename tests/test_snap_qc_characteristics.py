"""SNAP QC characteristics, FY 2023 (lane snap-qc): the committed extract
matches the adapter's contract and its own arithmetic, and the facts reach
Chronicle staging — never scorecard claims (boundary rule 2026-08-02)."""

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

from scorecard_db import ingest_us_admin_outturns as staging

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "snap-qc-characteristics"
EXTRACT = REPO / "data" / "externals" / "snap-qc-characteristics.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location("snapqc_adapter", SRC / "adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tables():
    """Rebuild B.1 and B.2 rows (in published units) from the extract."""
    a = _adapter()
    by = {"B.1": {}, "B.2": {}}
    for r in json.loads(EXTRACT.read_text()):
        table, rest = r["source_column"].removeprefix("Table ").split(": ", 1)
        code, col = rest.split(", column ")
        spec = a.COLUMNS[(table, int(col) - 1)]
        value = r["value"] / spec[2]
        width = a.TABLES[table][1]
        by[table].setdefault(code, [0.0] * width)[int(col) - 1] = value
    return a, by["B.1"], by["B.2"]


def test_committed_extract_matches_contract():
    a = _adapter()
    rows = json.loads(EXTRACT.read_text())
    assert len(rows) == a.EXPECTED_ROWS
    assert {r["geography"] for r in rows} == set(a.JURISDICTIONS.values()) | {"US"}
    us = {r["metric"]: r["value"] for r in rows if r["geography"] == "US"}
    assert us["households"] == 21_375_000 and us["participants"] == 40_065_000
    assert us["avg_household_size"] == 1.9


def test_b2_averages_recompute_from_b1_counts():
    a, b1, b2 = _tables()
    # the column percents are not staged; the count checks need only counts
    for code in b1:
        b1[code][1] = b1[code][3] = b1[code][5] = 100.0 / (len(b1) - 1)
    b1["US"][1] = b1["US"][3] = b1["US"][5] = 100.0
    a.qc(b1, b2)


def test_qc_catches_a_wrong_household_size():
    a, b1, b2 = _tables()
    for code in b1:
        b1[code][1] = b1[code][3] = b1[code][5] = 100.0 / (len(b1) - 1)
    b2["TX"][5] = 3.4  # Texas: 3,377 / 1,514 thousand = 2.23
    with pytest.raises(ValueError, match="household size"):
        a.qc(b1, b2)


def test_facts_route_to_chronicle_not_claims():
    facts = staging.stage_snap_qc()
    assert len(facts) == 540
    assert {f["routing"] for f in facts} == {staging.ROUTING}
    assert {f["consumed_by"] for f in facts} == {None}
    ids = {f["fact_id"] for f in facts}
    committed = [
        json.loads(line)
        for line in staging.LEDGER_PATH.read_text().splitlines()
        if line
    ]
    assert [f for f in committed if f["fact_id"] in ids] == sorted(
        facts, key=lambda f: f["fact_id"]
    )
    db = REPO / "data" / "scorecard.db"
    if db.exists():
        conn = sqlite3.connect(db)
        stage = conn.execute(
            "SELECT stage FROM lanes WHERE lane = 'snap-qc'"
        ).fetchone()
        n = conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE source LIKE 'snap_qc%'"
        ).fetchone()[0]
        conn.close()
        assert stage == ("cataloged",) and n == 0
