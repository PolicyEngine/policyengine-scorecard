"""Ingest the UC-deductions FRR claim family (#39, staged per #21).

Reads sources/harvest-uk-deductions/frr/claims_staged.jsonl — a
re-harvest of issue #21's Fair Repayment Rate family from primary
sources (the original ~/scorecard-harvest/uk_deductions staging is
machine-local). Every staged row carries a verbatim quote and a page
locator, re-verified 2026-08-14; see VERIFICATION.md alongside.

Mapping, under the harvest fail-loud contract:
    - reform rows ride policy_ref {"policy": "uc_fair_repayment_rate"}
      (cap 25% -> 15% of the UC standard allowance, effective
      2025-04-30, carried as reform detail) AGAINST the registered
      pre_frr_uc_deductions baseline world: the costing's own
      counterfactual is the 25%-cap law it replaced, not today's
      current law (which includes the FRR) — descriptor honesty the
      cross-baseline view guard depends on. conditions
      ["baseline_policy"] mirrors it for queryability.
    - the PSNCR line lands as CASH_REQUIREMENT_CHANGE with
      conditions["fiscal_measure"]="psncr" — deliberately NOT
      revenue_change, per #21's PSNCR-never-PSNB rule
    - the £420 average annual gain is a per-household statistic ->
      GBP_PER_HOUSEHOLD, never bare GBP (an average a query could sum)
    - the pre-FRR households-with-deductions level is a baseline claim
    - identity values route through the closed registry (uk_aliases);
      period must equal the fy END year (the live claim convention) —
      asserted per row, never trusted from staging
    - everything is held_out; the DWP quarterly deductions outturn
      tables PE's parameters consume are calibration territory and are
      not staged here at all

The write path mirrors ingest_uk_externals: one transaction replaces
this module's two sources wholesale AND runs the deliberate-
registration gate (#13) inside it — commit or nothing; the lane-feed
mirror is rewritten only after the commit.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_deductions data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish
from .uk_aliases import canon
from .models import (
    BASELINE,
    CalibrationRelationship,
    ExternalScore,
    Metric,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

STAGED = REPO / "sources" / "harvest-uk-deductions" / "frr" / "claims_staged.jsonl"
DEDUCTION_SOURCES = ("hm_treasury", "dwp")

KNOWN_FIELDS = frozenset(
    {
        "source",
        "metric",
        "unit_concept",
        "period",
        "fy",
        "value",
        "conditions",
        "reform_policy",
        "publication",
        "quote",
        "verified",
    }
)

# staged metric -> (Metric, expected staged unit, DB unit concept,
# value_kind). The staged unit label is validated against the expected
# one — a drifted re-stage fails loudly, never re-maps silently.
METRICS = {
    "cash_requirement_change": (
        Metric.CASH_REQUIREMENT_CHANGE,
        "gbp",
        UnitConcept.GBP,
        "gbp",
    ),
    "gainer_count": (
        Metric.GAINER_COUNT,
        "households",
        UnitConcept.HOUSEHOLDS,
        "count",
    ),
    "average_annual_gain": (
        Metric.AVERAGE_ANNUAL_GAIN,
        "gbp",
        UnitConcept.GBP_PER_HOUSEHOLD,
        "gbp",
    ),
    "participant_count": (
        Metric.PARTICIPANT_COUNT,
        "households",
        UnitConcept.HOUSEHOLDS,
        "count",
    ),
}

PRE_FRR_BASELINE = {"policy": "pre_frr_uc_deductions"}

FRR_REFORM = ReformRef(
    framework="policy_ref",
    reform={
        "policy": "uc_fair_repayment_rate",
        "change": "uc_deductions_cap_25pct_to_15pct_of_standard_allowance",
        "effective": "2025-04-30",
    },
    baseline=PRE_FRR_BASELINE,
)


def stage_scores() -> list[ExternalScore]:
    if not STAGED.exists():
        raise FileNotFoundError(f"staged claims missing: {STAGED}")
    scores = []
    for line in STAGED.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        unknown = set(row) - KNOWN_FIELDS
        if unknown:
            raise ValueError(
                f"uk_deductions: unhandled staged fields {sorted(unknown)}"
            )
        if row["source"] not in DEDUCTION_SOURCES:
            raise ValueError(f"uk_deductions: unknown source {row['source']!r}")
        # period keys the FY END year (the live claim-side convention;
        # models.py fy note) — asserted, never inherited from staging.
        end = int(row["fy"].split("-")[0]) + 1
        if row["period"] != end:
            raise ValueError(
                f"uk_deductions: period {row['period']} is not fy "
                f"{row['fy']}'s end year {end}"
            )
        if row["metric"] not in METRICS:
            raise ValueError(f"uk_deductions: unknown metric {row['metric']!r}")
        metric, staged_unit, unit, value_kind = METRICS[row["metric"]]
        canon(row["source"], "unit", row["unit_concept"])
        if row["unit_concept"] != staged_unit:
            raise ValueError(
                f"uk_deductions: {row['metric']} staged with unit "
                f"{row['unit_concept']!r}, expected {staged_unit!r}"
            )
        if row["reform_policy"] is None:
            reform = BASELINE
            mirror = {}
        elif row["reform_policy"] == "uc_fair_repayment_rate":
            reform = FRR_REFORM
            # baseline variants are load-bearing: mirrored in conditions
            # for queryability (models.py COLLATION worklist item 3)
            mirror = {"baseline_policy": PRE_FRR_BASELINE["policy"]}
        else:
            raise ValueError(f"uk_deductions: unknown reform {row['reform_policy']!r}")
        conditions = {
            "country": "UK",
            "geography": canon(row["source"], "geography", "GB"),
            "fy": row["fy"],
            **mirror,
            **row["conditions"],
        }
        if "program" in conditions:
            conditions["program"] = canon(
                row["source"], "program", conditions["program"]
            )
        if "subgroup" in conditions:
            conditions["subgroup"] = canon(
                row["source"], "subgroup", conditions["subgroup"]
            )
        scores.append(
            ExternalScore(
                source=row["source"],
                metric=metric,
                unit_concept=unit,
                period=row["period"],
                time_basis=TimeBasis.FISCAL_YEAR,
                value=float(row["value"]),
                conditions=conditions,
                reform=reform,
                calibration_relationship=CalibrationRelationship.HELD_OUT,
                source_column=row["quote"],
                publication=row["publication"],
                value_kind=value_kind,
            )
        )
    return finish(scores, "uk_deductions")


def ingest(db_path: Path) -> dict:
    """One transaction replaces this module's two sources wholesale and
    runs every persistence gate inside it (the ingest_uk_externals
    contract): delete, insert, the deliberate-registration gate (#13),
    the lane row — commit or nothing. The lane-feed mirror is rewritten
    only after the commit (idempotent merge keyed by lane id)."""
    scores = stage_scores()
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]
    placeholders = ",".join("?" * len(DEDUCTION_SOURCES))
    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            f"DELETE FROM external_scores WHERE source IN ({placeholders})",
            DEDUCTION_SOURCES,
        )
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        db.conn.execute(
            LANE_SQL,
            ("uk-deductions-frr", "ingested", f"{len(rows)} claims", "2026-08-19"),
        )
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        "2026-08-19",
        lanes={
            "uk-deductions-frr": {
                "source": "HMT + DWP",
                "area": "UC deductions (FRR)",
                "mode": 2,
            }
        },
    )
    db.close()
    return {"claims": len(rows)}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
