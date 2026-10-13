"""Diagnosis batch 3 (FNS, EITC, ASPE lanes): every item names real claims
from its lane, no claim is diagnosed twice, every pe_gap routes to an issue,
and the ingest writes exactly the batch."""

import json
import sqlite3
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_aspe_welfare_indicators as aspe
from scorecard_db import ingest_fns_snap_rates as fns
from scorecard_db import ingest_irs_eitc_participation as eitc

REPO = Path(__file__).resolve().parent.parent
BATCH = REPO / "diagnosis" / "batch3"
LANE_SOURCE = {"F": fns, "E": eitc, "A": aspe}


def _items():
    return {key: json.loads((BATCH / f"{key}.json").read_text()) for key in LANE_SOURCE}


def _claims(module):
    staged = module.stage()
    scores = staged[0] if isinstance(staged, tuple) else staged
    return {s.claim_id() for s in scores}


def test_items_name_real_claims_of_their_lane_once():
    seen = Counter()
    for key, items in _items().items():
        lane_claims = _claims(LANE_SOURCE[key])
        for item in items:
            assert set(item["claim_ids"]) <= lane_claims, item["title"]
            seen.update(item["claim_ids"])
    assert sum(seen.values()) == 57
    assert max(seen.values()) == 1


def test_classes_and_routes():
    by_class = Counter()
    for items in _items().values():
        for item in items:
            by_class[item["classification"]] += len(item["claim_ids"])
            if item["classification"] == "pe_gap":
                assert item["action_link"].startswith(
                    "https://github.com/PolicyEngine/microcosm/issues/"
                )
            if item["classification"] == "open":
                assert item["action_link"] is None
    assert by_class == {"pe_gap": 50, "concept_mismatch": 2, "open": 5}


def test_memos_match_the_records():
    for key, items in _items().items():
        memo = (BATCH / f"{key}.md").read_text()
        for n, item in enumerate(items, start=1):
            assert f"## {key}{n}. {item['title']}" in memo


def test_ingest_wrote_the_batch():
    db = REPO / "data" / "scorecard.db"
    if not db.exists():
        pytest.skip("scorecard.db not built")
    ids = [c for items in _items().values() for i in items for c in i["claim_ids"]]
    conn = sqlite3.connect(db)
    marks = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT diagnosis_class, COUNT(*) FROM diagnoses WHERE claim_id IN ({marks})"
        " GROUP BY 1",
        ids,
    ).fetchall()
    stage = conn.execute(
        "SELECT stage FROM lanes WHERE lane = 'diagnosis-batch-3'"
    ).fetchone()
    conn.close()
    assert dict(rows) == {"pe_gap": 50, "concept_mismatch": 2, "undiagnosed": 5}
    assert stage == ("computed",)
