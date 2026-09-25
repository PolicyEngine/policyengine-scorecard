"""Persist the OBR costings divergence decomposition (#59).

pipeline/decompose_uk_obr_divergence.py writes DECOMPOSITION.json beside
the comparison it decomposed. Nothing registered in build_db.py, so the
artifact vanished on every CI rebuild — a decomposition that exists only
on the machine that ran it is not a finding anyone can cite.

This step reads that artifact and writes the lane row, carrying the one
number that matters for the lane's honesty: how many of the twelve
(measure, FY) decompositions are still PARTIAL. It writes no
external_scores or pe_results rows — a decomposition is not a claim and
not a PE result; it is diagnostic structure over comparisons that already
exist. When the focal divergences are sized, THIS is where their records
attach to the diagnoses table through db.diagnose(), which is what
enforces the citable-known-issue gate.

    PYTHONPATH=. python -m scorecard_db.ingest_obr_divergence data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, ScorecardDB
from .harvest import REPO

DECOMPOSITION = REPO / "results" / "uk" / "obr_divergence" / "DECOMPOSITION.json"

LANE_ID = "obr-divergence-decomposition"
LANE_UPDATED = "2026-08-17"
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "OBR",
    "area": "costings divergence decomposition",
    "mode": 2,
    "country": "UK",
}


def summarize(records: list[dict]) -> dict:
    partial = [r for r in records if r["decomposition_status"] == "partial"]
    executed = sum(
        1 for r in records for c in r["valued_components"] if c["status"] == "computed"
    )
    explained = [r for r in records if "explained_share" in r]
    withheld = [r for r in records if "explained_share_withheld" in r]
    understated = [r for r in records if r.get("divergence_understated")]
    return {
        "records": len(records),
        "partial": len(partial),
        "complete": len(records) - len(partial),
        "executed_components": executed,
        "with_explained_share": len(explained),
        "explained_share_withheld": len(withheld),
        "divergence_understated": len(understated),
    }


def ingest(db_path: Path) -> dict:
    if not DECOMPOSITION.exists():
        # Honest, and visible: the decomposition has not been run against
        # a comparison yet. The lane is still WRITTEN, so a build says
        # "not run" rather than saying nothing.
        summary = {"records": 0, "partial": 0, "complete": 0, "not_run": True}
        detail = (
            "not run — no DECOMPOSITION.json; run "
            "pipeline/decompose_uk_obr_divergence.py against #56's "
            "COMPARISON.csv (or the committed fixture)"
        )
        stage = "registered"
    else:
        records = json.loads(DECOMPOSITION.read_text())
        summary = summarize(records)
        detail = (
            f"{summary['records']} decompositions, {summary['partial']} partial "
            f"({summary['complete']} complete), "
            f"{summary['executed_components']} executed components, "
            f"{summary['with_explained_share']} carrying an explained_share"
        )
        stage = "diagnosing"

    from .ingest_harvest import sync_lane_feed

    db = ScorecardDB(db_path)
    with db.conn:
        db.conn.execute(LANE_SQL, (LANE_ID, stage, detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return summary


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
