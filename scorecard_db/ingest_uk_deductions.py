"""Ingest the UC-deductions FRR claim family (#39, staged per #21).

Reads sources/harvest-uk-deductions/frr/claims_staged.jsonl — a
re-harvest of issue #21's Fair Repayment Rate family from primary
sources (the original ~/scorecard-harvest/uk_deductions staging is
machine-local). Every staged row carries a verbatim quote and a page
locator, re-verified 2026-08-14; see VERIFICATION.md alongside.

Mapping, under the harvest fail-loud contract:
    - reform rows ride policy_ref {"policy": "uc_fair_repayment_rate"}
      (cap 25% -> 15% of the UC standard allowance, effective
      2025-04-30, carried as reform detail)
    - the PSNCR line lands as CASH_REQUIREMENT_CHANGE with
      conditions["fiscal_measure"]="psncr" — deliberately NOT
      revenue_change, per #21's PSNCR-never-PSNB rule
    - the pre-FRR households-with-deductions level is a baseline claim
    - everything is held_out; the DWP quarterly deductions outturn
      tables PE's parameters consume are calibration territory and are
      not staged here at all

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_deductions data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import REPO, finish
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

METRICS = {
    "cash_requirement_change": Metric.CASH_REQUIREMENT_CHANGE,
    "gainer_count": Metric.GAINER_COUNT,
    "average_annual_gain": Metric.AVERAGE_ANNUAL_GAIN,
    "participant_count": Metric.PARTICIPANT_COUNT,
}

UNITS = {
    "gbp": UnitConcept.GBP,
    "households": UnitConcept.HOUSEHOLDS,
}

FRR_REFORM = ReformRef(
    framework="policy_ref",
    reform={
        "policy": "uc_fair_repayment_rate",
        "change": "uc_deductions_cap_25pct_to_15pct_of_standard_allowance",
        "effective": "2025-04-30",
    },
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
        if row["reform_policy"] is None:
            reform = BASELINE
        elif row["reform_policy"] == "uc_fair_repayment_rate":
            reform = FRR_REFORM
        else:
            raise ValueError(f"uk_deductions: unknown reform {row['reform_policy']!r}")
        conditions = {
            "country": "UK",
            "geography": "GB",
            "fy": row["fy"],
            **row["conditions"],
        }
        scores.append(
            ExternalScore(
                source=row["source"],
                metric=METRICS[row["metric"]],
                unit_concept=UNITS[row["unit_concept"]],
                period=row["period"],
                time_basis=TimeBasis.FISCAL_YEAR,
                value=float(row["value"]),
                conditions=conditions,
                reform=reform,
                calibration_relationship=CalibrationRelationship.HELD_OUT,
                source_column=row["quote"],
                publication=row["publication"],
                value_kind="usd" if row["unit_concept"] == "gbp" else "count",
            )
        )
    return finish(scores, "uk_deductions")


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.close()
    return {"claims": n}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
