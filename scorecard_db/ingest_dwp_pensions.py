"""Ingest DWP workplace pension participation (#98).

PolicyEngine-UK models pensions — contributions, their relief, the age
limit, the salary-sacrifice interaction — and until now not one of the
15,858 UK external claims said anything about pensions. This is the
external side: 1,377 participation rates by earnings band, age band and
region, split public/private/overall, 2009-2025.

Two things ride on every claim because leaving them in a methodology
note would make the rows uninterpretable:

  denominator   The rate is a share of employees ELIGIBLE for automatic
                enrolment — an earnings-trigger and age-range definition
                that has moved over the series. A participation rate
                whose denominator is unstated says nothing.
  survey_axis   DWP derives these from ONS ASHE, an employer survey of
                jobs; the certified PE-UK world is FRS-based. A
                PE-vs-DWP gap is a survey-population difference before
                it is an engine question — the same axis the LPC lane
                (#88) carries.

Geography is GB, not UK: ASHE excludes Northern Ireland, and the
registry keeps the two apart for the same reason #91 keeps IFS's
coverage-restricted analyses apart.

    PYTHONPATH=. python -m scorecard_db.ingest_dwp_pensions data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, require_fields
from .models import ExternalScore, Metric, TimeBasis, UnitConcept
from .relationships import uk_relationship
from .uk_aliases import canon

EXTERNALS = REPO / "data" / "externals"

ADAPTER_SOURCE = "dwp-pension-participation"
SOURCE = "dwp_pensions"
LANE_ID = "dwp-pension-participation"
LANE_UPDATED = "2026-08-25"
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "DWP",
    "area": "workplace pension participation",
    "mode": 1,
    "country": "UK",
}

PUBLICATION = {
    "title": "DWP Workplace pension participation and savings trends: 2009 to 2025",
    "url": (
        "https://www.gov.uk/government/statistics/"
        "workplace-pension-participation-and-savings-trends-2009-to-2025"
    ),
    "date": "2026-07-30",
    "country": "UK",
}

_KNOWN_FIELDS = frozenset(
    {
        "axis",
        "country",
        "denominator",
        "edition",
        "geography",
        "metric",
        "period",
        "program",
        "sector",
        "source",
        "source_column",
        "status",
        "subgroup",
        "survey_axis",
        "unit_concept",
        "value",
    }
)

_METRICS = {
    "participation_rate": (Metric.PARTICIPATION_RATE, UnitConcept.SHARE, "share")
}
# the adapter's axis name -> the uk_aliases axis its values are closed on
_AXES = {"earnings_band": "earnings_band", "age_band": "age_band", "region": "region"}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run sources/dwp-pension-participation/adapter.py first"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
        if row["source"] != ADAPTER_SOURCE:
            raise ValueError(f"{SOURCE}: row source {row['source']!r} is wrong")
        if row["country"] != "UK":
            raise ValueError(f"{SOURCE}: row country {row['country']!r} is not 'UK'")
    return rows


def stage() -> tuple[list[ExternalScore], dict]:
    scores: list[ExternalScore] = []
    counts: dict[str, int] = {}
    for row in _load():
        metric, unit, value_kind = _METRICS[row["metric"]]
        canon(SOURCE, "unit", row["unit_concept"])
        axis = row["axis"]
        if axis not in _AXES:
            raise ValueError(f"{SOURCE}: unregistered axis {axis!r}")
        value = float(row["value"])
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{SOURCE}: participation rate {value} is not a share — the "
                "publication gives fractions, and a percent slipping in here "
                "would be a hundredfold error nobody could see downstream"
            )
        cond = {
            "country": "UK",
            # GB, not UK: ASHE excludes Northern Ireland
            "geography": canon(SOURCE, "geography", row["geography"]),
            "program": canon(SOURCE, "program", row["program"]),
            "sector": canon(SOURCE, "sector", row["sector"]),
            # which axis this row cuts on, so an earnings band and an age
            # band never collide on one subgroup key
            "axis": axis,
            "subgroup": canon(SOURCE, _AXES[axis], row["subgroup"]),
            # the two facts that make the row interpretable at all
            "denominator": row["denominator"],
            "survey_axis": row["survey_axis"],
            "edition": row["edition"],
        }
        scores.append(
            ExternalScore(
                source=SOURCE,
                metric=metric,
                unit_concept=unit,
                period=int(row["period"]),
                # ASHE April reference year, carried as a calendar year
                time_basis=TimeBasis.ANNUAL,
                value=value,
                conditions=cond,
                calibration_relationship=uk_relationship(SOURCE, metric)[0],
                source_model="dwp_ashe",
                source_column=row["source_column"],
                publication=PUBLICATION,
                value_kind=value_kind,
                status=row["status"],
            )
        )
        counts[axis] = counts.get(axis, 0) + 1
    return finish(scores, SOURCE), counts


_EXPECTED = {"earnings_band": 357, "age_band": 459, "region": 561}


def ingest(db_path: Path) -> dict:
    scores, counts = stage()
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        detail = (
            f"{len(rows)} claims — the first external validation of any "
            "pensions quantity in the UK scorecard (participation among "
            "auto-enrolment ELIGIBLE employees, GB, ASHE-derived)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {"claims": len(rows), "by_axis": dict(sorted(counts.items()))}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
