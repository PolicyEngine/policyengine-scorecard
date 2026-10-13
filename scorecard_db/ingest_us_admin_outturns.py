"""Stage US administrative outturns for Chronicle -> data/ledger/us_admin_outturns.jsonl.

The 2026-08-02 boundary ruling (issue #6, Max): administrative OUTTURN
tables — caseloads, units, spending — belong in Ledger/Chronicle as
calibration material, never in the scorecard's external_scores, which hold
model claims only. This module is the US writer of that staging file, the
analogue of the UK file written by ingest_uk_externals. It writes no claims.

Sources staged today:
    hud_psh  HUD Picture of Subsidized Households, 31 Dec 2024 and 2025,
             State and U.S. (sources/hud-psh/, adapter QC'd; lane hud-psh)
    snap_qc  Characteristics of SNAP Households, FY 2023, Tables B.1-B.2:
             households, participants and benefits by State (QC sample
             weighted to Program Operations) and the caseload's averages,
             including household size (sources/snap-qc-characteristics/;
             lane snap-qc)

consumed_by: null for every HUD fact — read 2026-10-06 from the us-6.2.1
release's calibration_diagnostics.json, none of its 5,659 targets
mentions housing, HUD, vouchers, Section 8 or subsidized units in any field (housing is held out:
relationships.py, "§4: zero housing targets"). A later release that
targets these facts names its pin here.

consumed_by: null for every SNAP QC fact too. us-6.2.1 targets FY 2024
Program Operations SNAP households and benefits, national and by State
(104 usda_snap.fy2024.* targets) — the same class as B.1's households and
benefits but a later year and without the QC adjustments. Nothing targets
SNAP participants (people) or household size, which is where PE's SNAP
person counts diverge (fns-snap-rates lane: 2.7 people per participating
SPM unit against B.2's 1.9).

Each fact keeps a deterministic id over its identity, so re-staging
rewrites the same facts and Chronicle can key on them. Coded HUD cells
(missing, suppressed, non-reporting, not applicable) are staged with their
status and a null value — the code is information, not an absence.

    PYTHONPATH=. python -m scorecard_db.ingest_us_admin_outturns data/scorecard.db
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from .db import LANE_SQL, ScorecardDB
from .harvest import REPO, require_fields

EXTERNALS = REPO / "data" / "externals"
LEDGER_PATH = REPO / "data" / "ledger" / "us_admin_outturns.jsonl"
ROUTING = "chronicle: admin outturn (boundary rule 2026-08-02)"

LANE_ID = "hud-psh"
LANE_UPDATED = "2026-10-06"
FEED_UPDATED = "2026-10-07"
LANE_FEED_META = {
    "source": "HUD",
    "area": "Picture of Subsidized Households",
    "mode": 1,
    "country": "US",
}
SNAP_QC_LANE_ID = "snap-qc"
SNAP_QC_LANE_UPDATED = "2026-10-07"
SNAP_QC_LANE_FEED_META = {
    "source": "SNAP QC",
    "area": "caseload composition",
    "mode": 1,
    "country": "US",
}
SNAP_QC_PUBLICATION = {
    "title": "Characteristics of SNAP Households: Fiscal Year 2023",
    "url": "https://www.fns.usda.gov/research/snap/characteristics-fy23",
    "source_json": "sources/snap-qc-characteristics/source.json",
}
SNAP_QC_PERIOD_SEMANTICS = (
    "FY 2023 monthly average; QC sample weighted to Program Operations "
    "(erroneous and disaster-only households removed)"
)

# Repeated on every fact, so kept short; the full method, dictionary and
# sha256 pins are in sources/hud-psh/source.json.
HUD_PUBLICATION = {
    "title": "HUD Picture of Subsidized Households",
    "url": "https://www.huduser.gov/portal/datasets/assthsg.html",
    "source_json": "sources/hud-psh/source.json",
}
HUD_PERIOD_SEMANTICS = "point_in_time_dec31; tenant reports over the prior 18 months"


_KNOWN_FIELDS = frozenset(
    {
        "country",
        "geography",
        "metric",
        "period",
        "program",
        "source",
        "source_column",
        "status",
        "subgroup",
        "unit_concept",
        "value",
        "variant",
    }
)
_STATUSES = frozenset(
    {"ok", "missing", "suppressed", "non_reporting", "not_applicable"}
)


def _fact_id(*identity) -> str:
    key = "|".join(str(x) for x in identity)
    return "us-admin-" + hashlib.sha256(key.encode()).hexdigest()[:16]


def stage_hud_psh() -> tuple[list[dict], Counter]:
    path = EXTERNALS / "hud-psh.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — run sources/hud-psh/adapter.py")
    facts, by_year = [], Counter()
    for row in json.loads(path.read_text()):
        require_fields(row, _KNOWN_FIELDS, "hud_psh")
        if row["source"] != "hud-psh" or row["country"] != "US":
            raise ValueError(f"hud_psh: foreign row {row['source_column']!r}")
        if row["status"] not in _STATUSES:
            raise ValueError(f"hud_psh: unknown status {row['status']!r}")
        if row["variant"] is not None:
            raise ValueError(f"hud_psh: unexpected variant {row['variant']!r}")
        year = int(row["period"].removeprefix("31 Dec "))
        file = row["source_column"].split(":", 1)[0]
        facts.append(
            {
                "fact_id": _fact_id(
                    "hud_psh",
                    row["metric"],
                    row["program"],
                    row["subgroup"],
                    row["geography"],
                    year,
                ),
                "source": "hud_psh",
                "publication": {
                    **HUD_PUBLICATION,
                    "file": file,
                    "snapshot": f"{year}-12-31",
                },
                "metric": row["metric"],
                "program": row["program"],
                "subgroup": row["subgroup"],
                "geography": row["geography"],
                "period": year,
                "period_semantics": HUD_PERIOD_SEMANTICS,
                "unit": row["unit_concept"],
                "value": row["value"],
                "status": row["status"],
                "source_column": row["source_column"],
                "consumed_by": None,
                "routing": ROUTING,
            }
        )
        by_year[year] += 1
    return facts, by_year


def stage_snap_qc() -> list[dict]:
    path = EXTERNALS / "snap-qc-characteristics.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — run the snap-qc adapter")
    facts = []
    for row in json.loads(path.read_text()):
        require_fields(row, _KNOWN_FIELDS, "snap_qc")
        if row["source"] != "snap-qc-characteristics" or row["status"] != "ok":
            raise ValueError(f"snap_qc: unexpected row {row['source_column']!r}")
        facts.append(
            {
                "fact_id": _fact_id(
                    "snap_qc", row["metric"], row["geography"], row["period"]
                ),
                "source": "snap_qc",
                "publication": SNAP_QC_PUBLICATION,
                "metric": row["metric"],
                "program": "snap",
                "subgroup": row["subgroup"],
                "geography": row["geography"],
                "period": 2023,
                "period_semantics": SNAP_QC_PERIOD_SEMANTICS,
                "unit": row["unit_concept"],
                "value": row["value"],
                "status": row["status"],
                "source_column": row["source_column"],
                "consumed_by": None,
                "routing": ROUTING,
            }
        )
    return facts


_EXPECTED = {"hud_psh": 10398, "snap_qc": 540}


def ingest(db_path: Path) -> dict:
    hud, by_year = stage_hud_psh()
    snap = stage_snap_qc()
    counts = {"hud_psh": len(hud), "snap_qc": len(snap)}
    facts = hud + snap
    if counts != _EXPECTED:
        raise ValueError(f"fact accounting drifted: {counts} != {_EXPECTED}")
    ids = Counter(f["fact_id"] for f in facts)
    dupes = [k for k, n in ids.items() if n > 1]
    if dupes:
        raise ValueError(f"fact_id collisions (identity lost an axis): {dupes[:5]}")
    facts.sort(key=lambda f: f["fact_id"])
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(
        "\n".join(json.dumps(f, sort_keys=True) for f in facts) + "\n"
    )

    from .ingest_harvest import sync_lane_feed

    db = ScorecardDB(db_path)
    with db.conn:
        detail = (
            f"{len(facts)} administrative facts staged for Chronicle "
            f"(data/ledger/us_admin_outturns.jsonl; 31 Dec 2024 and 2025, "
            "State and U.S.) — admin outturns are calibration material, not "
            "scorecard claims (boundary rule 2026-08-02); us-6.2.1 consumes "
            "none (no housing targets)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "cataloged", detail, LANE_UPDATED))
        snap_detail = (
            f"{len(snap)} administrative facts staged for Chronicle "
            "(data/ledger/us_admin_outturns.jsonl; FY 2023 SNAP QC Tables "
            "B.1-B.2 by State: households, participants, benefits, average "
            "household size and income) — caseload composition is calibration "
            "material, not scorecard claims (boundary rule 2026-08-02); "
            "us-6.2.1 targets FY 2024 households and benefits, nothing on "
            "participants or household size"
        )
        db.conn.execute(
            LANE_SQL,
            (SNAP_QC_LANE_ID, "cataloged", snap_detail, SNAP_QC_LANE_UPDATED),
        )
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={
            LANE_ID: LANE_FEED_META,
            SNAP_QC_LANE_ID: SNAP_QC_LANE_FEED_META,
        },
    )
    db.close()
    return {
        **counts,
        "hud_by_year": dict(sorted(by_year.items())),
        "ledger_path": str(LEDGER_PATH),
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
