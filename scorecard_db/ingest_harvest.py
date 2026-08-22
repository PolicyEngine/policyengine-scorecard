"""Run all seven 2026-08-02 harvest adapters and sync the lane feed.

Each adapter sets its DB lane; this runner then mirrors those lanes into
data/lanes.json (the repo-committed mission-control feed the app reads,
which ingest_platform seeds the DB from on rebuild).

    PYTHONPATH=. python -m scorecard_db.ingest_harvest data/scorecard.db
"""

from __future__ import annotations

import json
from datetime import date
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
# fields beyond stage/note/updated, which mirror the DB lane). Every entry
# carries an explicit country: appended feed entries must never rely on the
# app's missing-country-means-US default (sync_lane_feed enforces this).
LANE_FEED = {
    "jct-reform-scores": {
        "source": "JCT",
        "area": "tax expenditures + revenue estimates",
        "mode": 2,
        "country": "US",
    },
    "tpc-distribution": {
        "source": "TPC",
        "area": "distribution tables",
        "mode": 2,
        "country": "US",
    },
    "cbo-baseline": {
        "source": "CBO",
        "area": "Feb-2026 baseline workbooks",
        "mode": 1,
        "country": "US",
    },
    "cbo-cost-estimates": {
        "source": "CBO",
        "area": "per-bill cost estimates",
        "mode": 2,
        "country": "US",
    },
    "pwbm-reform-scores": {
        "source": "PWBM",
        "area": "reform scores + distributions",
        "mode": 2,
        "country": "US",
    },
    "tax-foundation-scores": {
        "source": "Tax Foundation",
        "area": "revenue + tariff scores",
        "mode": 2,
        "country": "US",
    },
    "budget-lab-scores": {
        "source": "Budget Lab",
        "area": "budget + distribution scores",
        "mode": 2,
        "country": "US",
    },
    "cpsp-poverty": {
        "source": "Columbia CPSP",
        "area": "US poverty statistics",
        "mode": 1,
        "country": "US",
    },
}


def sync_lane_feed(
    db: ScorecardDB,
    feed_path: Path,
    updated: str,
    lanes: dict | None = None,
) -> int:
    """Merge DB lane rows into the committed feed. `lanes` maps lane id ->
    display meta; defaults to this module's harvest registry (other
    exporters pass their own — the merge only touches listed ids).

    ``updated`` is a LITERAL the caller supplies, not a derived value.
    That is the contract, stated here because it is easy to misread: the
    feed's top-level `updated` stamp is whatever the LAST caller in a
    build passes, so every ingest that syncs this feed must pass the SAME
    constant. If two callers disagree, the committed data/lanes.json
    drifts depending on ingest order and the no-drift gate fails — the
    exact breakage that had to be repaired once already. A lane's own
    `updated_at` comes from its DB row and is per-lane; only this
    top-level stamp is the shared literal.
    """
    feed = json.loads(feed_path.read_text())
    by_id = {lane["id"]: lane for lane in feed["lanes"]}
    n = 0
    for lane_id, meta in (LANE_FEED if lanes is None else lanes).items():
        row = db.conn.execute(
            "SELECT stage, detail, updated_at FROM lanes WHERE lane = ?",
            (lane_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"lane {lane_id} missing from DB after ingest")
        entry = by_id.get(lane_id)
        if entry is None:
            # A newly appended entry must state its country explicitly:
            # the app's countryOf() defaults a missing key to "US", so a
            # country-less append would silently file a UK lane under US.
            if "country" not in meta:
                raise ValueError(
                    f"lane {lane_id}: feed meta has no 'country' — appended "
                    "lane entries must carry it explicitly (missing country "
                    "renders as US in the app)"
                )
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
    # Lane writers run independently and some source modules carry an older
    # pinned update date. Never let a later build/test step regress the feed's
    # top-level freshness marker (the BE 2026-08-21 lane used to be followed
    # by a UK 2026-08-19 sync). Non-date legacy placeholders such as "old" are
    # replaced by the incoming date.
    try:
        existing_date = date.fromisoformat(feed.get("updated", ""))
        incoming_date = date.fromisoformat(updated)
    except (TypeError, ValueError):
        feed["updated"] = updated
    else:
        feed["updated"] = max(existing_date, incoming_date).isoformat()
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
