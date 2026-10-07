"""HUD Picture of Subsidized Households (lane hud-psh): the committed extract
is exactly what the adapter derives from raw/, the QC catches a broken
identity, and the facts reach Chronicle staging — never scorecard claims
(boundary rule 2026-08-02)."""

import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_us_admin_outturns as staging

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "hud-psh"
EXTRACT = REPO / "data" / "externals" / "hud-psh.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location("hud_adapter", SRC / "adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def parsed():
    a = _adapter()
    rows, drops = [], Counter()
    for year in a.YEARS:
        for level, stem in (("state", "STATE"), ("us", "US")):
            got, dropped = a.parse_file(
                a.RAW / f"{stem}_{year}_2020census.xlsx", level, year
            )
            rows += got
            drops += dropped
    return a, rows, drops


def test_committed_extract_is_the_adapters_output(parsed):
    a, rows, drops = parsed
    assert rows == json.loads(EXTRACT.read_text())
    assert drops == {"mtw_split_rows": 235}
    a.qc(rows)


def test_every_column_is_accounted_for(parsed):
    a, _, _ = parsed
    for year in a.YEARS:
        for stem in ("STATE", "US"):
            cols = set(a.read_xlsx(a.RAW / f"{stem}_{year}_2020census.xlsx")[0])
            assert cols <= set(a.STAGED) | a.IDENTITY | set(a.NOT_STAGED)
    # nothing is both staged and set aside
    assert not set(a.STAGED) & set(a.NOT_STAGED)


def test_coded_cells_keep_their_status(parsed):
    _, rows, _ = parsed
    coded = [r for r in rows if r["status"] != "ok"]
    # dictionary codes -1 / -4 / -5; no State-level cell is NA
    assert Counter(r["status"] for r in coded) == {
        "missing": 45,
        "suppressed": 180,
        "non_reporting": 586,
    }
    assert all(r["value"] is None for r in coded)
    assert all(r["value"] is not None for r in rows if r["status"] == "ok")


def test_qc_catches_a_broken_us_total(parsed):
    a, rows, _ = parsed
    broken = [dict(r) for r in rows]
    us = next(
        r
        for r in broken
        if r["geography"] == "US"
        and r["metric"] == "subsidized_units"
        and r["program"] == "public_housing"
        and r["subgroup"] == "total"
    )
    us["value"] += 1000
    with pytest.raises(ValueError, match="QC failed"):
        a.qc(broken)


def test_facts_route_to_chronicle_not_claims():
    facts, by_year = staging.stage_hud_psh()
    assert len(facts) == 10398 and set(by_year) == {2024, 2025}
    assert len({f["fact_id"] for f in facts}) == len(facts)
    assert {f["routing"] for f in facts} == {staging.ROUTING}
    # us-6.2.1 has no housing targets: nothing consumes these facts
    assert {f["consumed_by"] for f in facts} == {None}
    committed = [
        json.loads(line)
        for line in staging.LEDGER_PATH.read_text().splitlines()
        if line
    ]
    assert committed == sorted(facts, key=lambda f: f["fact_id"])


def test_no_hud_claims_in_the_scorecard_db():
    import sqlite3

    db = REPO / "data" / "scorecard.db"
    if not db.exists():
        pytest.skip("scorecard.db not built")
    conn = sqlite3.connect(db)
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source LIKE 'hud%'"
    ).fetchone()[0]
    stage = conn.execute("SELECT stage FROM lanes WHERE lane = 'hud-psh'").fetchone()
    conn.close()
    assert n == 0
    assert stage == ("cataloged",)
