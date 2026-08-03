"""Run all seven 2026-08-02 harvest adapters and sync the lane feed.

Each adapter sets its DB lane; this runner then mirrors those lanes into
data/lanes.json (the repo-committed mission-control feed the app reads,
which ingest_platform seeds the DB from on rebuild).

    PYTHONPATH=. python -m scorecard_db.ingest_harvest data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from . import (
    ingest_budget_lab,
    ingest_cbo,
    ingest_cpsp,
    ingest_jct,
    ingest_pwbm,
    ingest_tax_foundation,
    ingest_tpc,
)
from .baselines import register_baselines
from .db import ScorecardDB
from .harvest import REPO

ADAPTERS = {
    "jct": ingest_jct,
    "tpc": ingest_tpc,
    "budget_lab": ingest_budget_lab,
    "cpsp": ingest_cpsp,
    "cbo": ingest_cbo,
    "pwbm": ingest_pwbm,
    "tax_foundation": ingest_tax_foundation,
}

# Lane feed metadata for the lanes each adapter writes (id -> feed entry
# fields beyond stage/note/updated, which mirror the DB lane).
LANE_FEED = {
    "jct-reform-scores": {
        "source": "JCT", "area": "tax expenditures + revenue estimates",
        "mode": 2,
    },
    "tpc-distribution": {
        "source": "TPC", "area": "distribution tables", "mode": 2,
    },
    "cbo-baseline": {
        "source": "CBO", "area": "Feb-2026 baseline workbooks", "mode": 1,
    },
    "cbo-cost-estimates": {
        "source": "CBO", "area": "per-bill cost estimates", "mode": 2,
    },
    "pwbm-reform-scores": {
        "source": "PWBM", "area": "reform scores + distributions", "mode": 2,
    },
    "tax-foundation-scores": {
        "source": "Tax Foundation", "area": "revenue + tariff scores",
        "mode": 2,
    },
    "budget-lab-scores": {
        "source": "Budget Lab", "area": "budget + distribution scores",
        "mode": 2,
    },
    "cpsp-poverty": {
        "source": "Columbia CPSP", "area": "US poverty statistics",
        "mode": 1,
    },
}


def sync_lane_feed(db: ScorecardDB, feed_path: Path, updated: str) -> int:
    feed = json.loads(feed_path.read_text())
    by_id = {lane["id"]: lane for lane in feed["lanes"]}
    n = 0
    for lane_id, meta in LANE_FEED.items():
        row = db.conn.execute(
            "SELECT stage, detail, updated_at FROM lanes WHERE lane = ?",
            (lane_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"lane {lane_id} missing from DB after ingest")
        entry = by_id.get(lane_id)
        if entry is None:
            entry = {"id": lane_id, **meta}
            feed["lanes"].append(entry)
            by_id[lane_id] = entry
        entry.update(
            stage=row["stage"],
            running=False,
            updated=row["updated_at"],
            note=row["detail"],
        )
        n += 1
    feed["updated"] = updated
    feed_path.write_text(json.dumps(feed, indent=1) + "\n")
    return n


def ingest(db_path: Path) -> dict:
    stats = {}
    for name, adapter in ADAPTERS.items():
        stats[name] = adapter.ingest(db_path)
    db = ScorecardDB(db_path)
    stats["baselines_registered"] = register_baselines(db)
    stats["lanes_synced"] = sync_lane_feed(
        db, REPO / "data" / "lanes.json", "2026-08-02"
    )
    stats["coverage"] = db.coverage()
    stats["claims_by_source"] = {
        r["source"]: r["n"]
        for r in db.conn.execute(
            "SELECT source, COUNT(*) n FROM external_scores GROUP BY source"
        )
    }
    db.close()
    return stats


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
