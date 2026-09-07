"""Ingest Low Pay Commission minimum-wage coverage and bite (#88).

PolicyEngine-UK carries a minimum-wage implementation — `minimum_wage`,
`minimum_wage_category`, and the whole `gov.hmrc.minimum_wage` parameter
tree — and until now nothing on the scorecard validated any of it. There
was no external claim about the minimum wage anywhere in the UK
population.

119 claims from the Low Pay Commission Report 2025 data annexes
(sources/lpc-minimum-wage/adapter.py explains what is read and what is
deliberately not):

    minimum_wage_bite            66  per cent of median hourly pay
    minimum_wage_coverage        13  jobs at or below the rate
    minimum_wage_coverage_rate   40  per cent of jobs

Two things this lane introduces on purpose:

1. **A JOBS unit concept.** Coverage counts jobs. One person can hold two
   and one household several, so a job count is not interchangeable with
   any population unit already here, and ASHE — the survey behind it —
   is an employer survey OF JOBS. Mapping it onto `persons` because that
   unit existed would have misstated what the number is; `uk_aliases`
   records `lpc:jobs` DISTINCT from both `dwp_hbai:persons` and
   `uk_hmrc:individuals`.

2. **The bite denominator, on the claim.** Bite is the rate over ASHE's
   median hourly wage of full-time workers. The certified PE-UK world is
   FRS-based, so a PE-vs-LPC bite gap is a SURVEY-POPULATION difference
   before it is an engine question. That axis rides in
   `conditions["denominator"]` so a later comparison reads it off the row
   instead of rediscovering it — and cannot report an engine defect
   without sizing it first.

Same contract as ingest_uk_externals: fail loudly on any unmapped
metric, unknown identity value or unhandled adapter field; values arrive
in raw units and are NEVER re-derived; calibration_relationship is
decided in relationships.py.

    PYTHONPATH=. python -m scorecard_db.ingest_lpc_minimum_wage data/scorecard.db
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

ADAPTER_SOURCE = "lpc-minimum-wage"
SOURCE = "lpc"
LANE_ID = "lpc-minimum-wage"
LANE_UPDATED = "2026-08-24"
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "Low Pay Commission",
    "area": "minimum wage coverage and bite",
    "mode": 1,
    "country": "UK",
}

PUBLICATION = {
    "title": "Low Pay Commission Report 2025 — data annexes",
    "url": "https://www.gov.uk/government/publications/low-pay-commission-report-2025",
    "date": "2026-02-02",
    "country": "UK",
}

# metric -> (Metric, expected adapter unit, UnitConcept, value_kind).
# Validate-then-map: the staged unit label must be the one the metric
# carries, or the row is a mislabeled quantity and must not land.
_METRICS = {
    "minimum_wage_bite": (
        Metric.MINIMUM_WAGE_BITE,
        "percent",
        UnitConcept.PERCENT,
        "percent",
    ),
    "minimum_wage_coverage": (
        Metric.MINIMUM_WAGE_COVERAGE,
        "jobs",
        UnitConcept.JOBS,
        "count",
    ),
    "minimum_wage_coverage_rate": (
        Metric.MINIMUM_WAGE_COVERAGE_RATE,
        "percent",
        UnitConcept.PERCENT,
        "percent",
    ),
}

_KNOWN_FIELDS = frozenset(
    {
        "country",
        "denominator",
        "edition",
        "geography",
        "metric",
        "period",
        "rate_scope",
        "source",
        "source_column",
        "status",
        "subgroup",
        "unit_concept",
        "value",
    }
)


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run sources/lpc-minimum-wage/adapter.py first"
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
        metric, expected_unit, unit, value_kind = _METRICS[row["metric"]]
        staged_unit = canon(SOURCE, "unit", row["unit_concept"])
        if staged_unit != expected_unit:
            raise ValueError(
                f"{SOURCE}: {row['metric']} staged unit {staged_unit!r} != "
                f"{expected_unit!r} — fix the label, never map past it"
            )
        cond = {
            "country": "UK",
            "geography": canon(SOURCE, "geography", row["geography"]),
            "program": canon(SOURCE, "program", "minimum_wage"),
            "subgroup": canon(SOURCE, "subgroup", row["subgroup"]),
            # WHICH rate the statistic is about: the adult rate, an
            # age-band rate, or all NMW/NLW rates together. Three
            # different questions, and a claim that did not say which
            # would be uninterpretable.
            "rate_scope": canon(SOURCE, "rate_scope", row["rate_scope"]),
            "edition": row["edition"],
        }
        if row.get("denominator"):
            # the survey-population axis, on the claim
            cond["denominator"] = row["denominator"]
        elif metric is Metric.MINIMUM_WAGE_BITE:
            raise ValueError(
                f"{SOURCE}: a bite claim without its denominator is "
                "uninterpretable — the ASHE median is what it is a per cent of"
            )
        scores.append(
            ExternalScore(
                source=SOURCE,
                metric=metric,
                unit_concept=unit,
                period=int(row["period"]),
                # ASHE April reference year, carried as a calendar year
                time_basis=TimeBasis.ANNUAL,
                value=float(row["value"]),
                conditions=cond,
                calibration_relationship=uk_relationship(SOURCE, metric)[0],
                source_model="lpc_ashe",
                source_column=row["source_column"],
                publication=PUBLICATION,
                value_kind=value_kind,
                status=row["status"],
            )
        )
        counts[row["metric"]] = counts.get(row["metric"], 0) + 1
    return finish(scores, SOURCE), counts


_EXPECTED = {
    "minimum_wage_bite": 66,
    "minimum_wage_coverage": 13,
    "minimum_wage_coverage_rate": 40,
}


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
            f"{len(rows)} claims — the first external validation of PE-UK's "
            "minimum-wage machinery (coverage in JOBS, bite vs the ASHE median)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {"claims": len(rows), "by_metric": dict(sorted(counts.items()))}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
