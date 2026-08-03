"""Run all seven 2026-08-02 UK-harvest adapters.

    PYTHONPATH=. python -m scorecard_db.ingest_uk data/scorecard.db

Beyond the per-source ingests this runner:

1. Collects every admin-outturn row the adapters routed OUT of
   external_scores and writes the Ledger staging file
   (data/ledger/uk_admin_outturns.jsonl) — the populace/Ledger lane's
   handoff, with deterministic pre-agreed fact ids (routing rule, Max
   2026-08-02: admin facts → Ledger, model claims → Scorecard).
2. Seeds the baselines registry and fails loudly on any baseline world
   the data references that is not deliberately described (issue #13).
3. Mirrors the UK lanes into data/lanes.json (the app's
   mission-control feed), adding entries for the lanes new with this
   population.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import (
    ingest_uk_dwp,
    ingest_uk_hmrc,
    ingest_uk_hmt,
    ingest_uk_ifs,
    ingest_uk_obr,
    ingest_uk_rf,
    ingest_uk_ukmod_jrf,
)
from .baselines import register_baselines
from .db import ScorecardDB
from .harvest import REPO
from .ingest_harvest import sync_lane_feed
from .uk import write_ledger_staging

ADAPTERS = {
    "uk_obr": ingest_uk_obr,
    "uk_hmrc": ingest_uk_hmrc,
    "uk_dwp": ingest_uk_dwp,
    "uk_hmt": ingest_uk_hmt,
    "uk_ukmod_jrf": ingest_uk_ukmod_jrf,
    "uk_ifs": ingest_uk_ifs,
    "uk_rf": ingest_uk_rf,
}

UK_LANE_FEED = {
    "obr-measures": {
        "source": "OBR", "area": "policy measures database (1970→)",
        "mode": 2,
    },
    "obr-welfare": {
        "source": "OBR", "area": "welfare trends / EFO baselines", "mode": 1,
    },
    "hmrc-personal-tax": {
        "source": "HMRC", "area": "UK personal tax statistics", "mode": 1,
    },
    "hbai-poverty": {
        "source": "DWP HBAI", "area": "UK poverty rates", "mode": 1,
    },
    "dwp-takeup": {
        "source": "DWP", "area": "UK income-related benefits take-up",
        "mode": 1,
    },
    "hmt-costings": {
        "source": "HM Treasury", "area": "fiscal-event scorecards + DA",
        "mode": 2,
    },
    "ukmod-stats": {
        "source": "UKMOD", "area": "published statistics", "mode": 1,
    },
    "ifs-taxben": {
        "source": "IFS TAXBEN", "area": "poverty + benefit options",
        "mode": 2,
    },
    "rf-outlook": {
        "source": "Resolution Foundation",
        "area": "living standards outlook + Budget analysis", "mode": 2,
    },
}


def ingest(db_path: Path) -> dict:
    stats: dict = {}
    ledger_rows: list[dict] = []
    for name, adapter in ADAPTERS.items():
        # stage() runs twice (here for the ledger rows, again inside the
        # adapter's own ingest) — staging is pure and cheap, and keeping
        # each adapter independently runnable beats threading state.
        ledger_rows.extend(adapter.stage()[1])
        stats[name] = adapter.ingest(db_path)

    stats["ledger_staging_rows"] = write_ledger_staging(ledger_rows)

    db = ScorecardDB(db_path)
    stats["baselines_registered"] = register_baselines(db)
    stats["lanes_synced"] = sync_lane_feed(
        db, REPO / "data" / "lanes.json", "2026-08-02",
        lane_feed=UK_LANE_FEED,
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
