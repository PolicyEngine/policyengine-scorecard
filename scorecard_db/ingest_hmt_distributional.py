"""Register the HMT distributional-analysis lane in the built DB (#61).

The lane emits ZERO value claims and says so: HM Treasury publishes the
Budget 2025 decile impacts as unlabeled chart bars in a PDF, with no data
tables (sources/hmt-distributional/adapter.py explains the whole call).
That honesty was the point of the lane — but it was also why the lane
VANISHED from a post-#74 build: the adapter wrote standalone metadata,
nothing registered in build_db.py, and no lane row existed, so a fresh
CI-built database contained no trace of HMT at all. Not even a zero.

This module is the missing step. It writes the lane row and mirrors it
into the committed feed, carrying the adapter's exact chart-cell
accounting as the lane detail:

    132 source marks = 0 emitted + 132 chart_not_digitized

so a reader of the DB (or mission control) sees a declared, quantified
omission rather than an absence. It deliberately writes no
external_scores rows; when HMT releases data tables or a documented
digitization lands, THIS is where the ingest goes, and the identity and
baseline machinery it will need is already carried in the metadata
artifact (income_identity, chart_baselines) and registered in
baselines.py / uk_aliases.py.

    PYTHONPATH=. python -m scorecard_db.ingest_hmt_distributional data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, ScorecardDB
from .harvest import REPO

META = REPO / "data" / "externals" / "hmt-distributional-meta.json"

LANE_ID = "hmt-distributional"
LANE_UPDATED = "2026-08-17"
# The UK family's shared top-level feed literal (sync_lane_feed's
# contract: every caller in a build must pass the same one).
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "HM Treasury",
    "area": "Budget distributional analysis (chart-only)",
    "mode": 2,
    "country": "UK",
}


def ingest(db_path: Path) -> dict:
    if not META.exists():
        raise FileNotFoundError(
            f"{META} missing — run sources/hmt-distributional/adapter.py "
            "(needs pypdf + pyyaml)"
        )
    meta = json.loads(META.read_text())
    if meta["value_claims_emitted"] != 0:
        raise ValueError(
            "hmt-distributional is a chart-only lane: a metadata artifact "
            "claiming emitted values means the digitization landed without "
            "an ingest path for it"
        )
    cells = meta["chart_cells"]
    if cells["emitted"] + cells["chart_not_digitized"] != cells["source_marks"]:
        raise ValueError(
            f"chart-cell accounting does not close: {cells['emitted']} + "
            f"{cells['chart_not_digitized']} != {cells['source_marks']}"
        )
    detail = (
        f"0 claims — chart-only publication; {cells['source_marks']} source "
        f"marks = {cells['emitted']} emitted + "
        f"{cells['chart_not_digitized']} chart_not_digitized "
        f"({len(meta['income_identity']['income_groups'])} income groups x "
        f"{len(cells['series'])} series x {len(cells['by_figure'])} figures)"
    )

    from .ingest_harvest import sync_lane_feed

    db = ScorecardDB(db_path)
    with db.conn:
        db.conn.execute(LANE_SQL, (LANE_ID, "cataloged", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {
        "claims": 0,
        "source_marks": cells["source_marks"],
        "chart_not_digitized": cells["chart_not_digitized"],
        "components": meta["components"],
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
