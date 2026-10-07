"""Stage US administrative outturns for Chronicle -> data/ledger/us_admin_outturns.jsonl.

The 2026-08-02 boundary ruling (issue #6, Max): administrative OUTTURN
tables — caseloads, units, spending — belong in Ledger/Chronicle as
calibration material, never in the scorecard's external_scores, which hold
model claims only. This module is the US writer of that staging file, the
analogue of the UK file written by ingest_uk_externals. It writes no claims.

Sources staged today:
    hud_psh  HUD Picture of Subsidized Households, 31 Dec 2024 and 2025,
             State and U.S. (sources/hud-psh/, adapter QC'd; lane hud-psh)

consumed_by: null for every HUD fact — read 2026-10-06 from the us-6.2.1
release's calibration_diagnostics.json, none of its 5,659 targets
mentions housing, HUD, vouchers, Section 8 or subsidized units in any field (housing is held out:
relationships.py, "§4: zero housing targets"). A later release that
targets these facts names its pin here.

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
FEED_UPDATED = "2026-10-06"
LANE_FEED_META = {
    "source": "HUD",
    "area": "Picture of Subsidized Households",
    "mode": 1,
    "country": "US",
}

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


_EXPECTED = {"hud_psh": 10398}


def ingest(db_path: Path) -> dict:
    facts, by_year = stage_hud_psh()
    counts = {"hud_psh": len(facts)}
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
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {
        **counts,
        "by_year": dict(sorted(by_year.items())),
        "ledger_path": str(LEDGER_PATH),
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
