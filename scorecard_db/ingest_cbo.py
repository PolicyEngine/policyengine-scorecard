"""Ingest the CBO staged claims (2026-08-02 harvest).

February-2026 Budget and Economic Outlook supplemental workbooks (929
baseline rows: Medicaid/SSI/SNAP/UI/CHIP outlays+participation, the
330-row individual-income-tax AGI→liability walk) plus two single-year
rows from the P.L. 119-21 SNAP cost-estimate supplement (61367).

calibration_relationship is honored AS STAGED: 317 rows arrive
consumed_as_target, pre-verified by the harvest against
policyengine-us/parameters/calibration/gov/cbo/ (SSI sheet rows reproduce
the PE calibration yaml exactly).

The 61367 rows describe CBO's January-2025 baseline vintage — a different
baseline world than the February-2026 workbooks. Without a marker the
$227 avg-benefit row would collide with the Feb-2026 workbook's 2034 row
($219.86); both get conditions["data_vintage"]="january_2025_baseline".
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import finish, load_staged, policy_ref, require_fields
from .models import (
    BASELINE,
    CalibrationRelationship,
    ExternalScore,
    Metric,
    TimeBasis,
    UnitConcept,
)

METRICS = {
    "benefit_cost": Metric.BENEFIT_COST,
    "enrollment": Metric.ENROLLMENT,
    "participant_count": Metric.PARTICIPANT_COUNT,
    "revenue_change": Metric.REVENUE_CHANGE,
    "income_aggregate": Metric.INCOME_AGGREGATE,
    "deduction_aggregate": Metric.DEDUCTION_AGGREGATE,
    "tax_liability": Metric.TAX_LIABILITY,
    "return_count": Metric.RETURN_COUNT,
    "tax_credits_applied": Metric.TAX_CREDITS_APPLIED,
    "average_monthly_benefit": Metric.AVERAGE_MONTHLY_BENEFIT,
    "maximum_monthly_benefit": Metric.MAXIMUM_MONTHLY_BENEFIT,
    "average_weekly_benefit": Metric.AVERAGE_WEEKLY_BENEFIT,
    "first_payment_count": Metric.FIRST_PAYMENT_COUNT,
}

_KNOWN_FIELDS = frozenset(
    {
        "source", "unit_concept", "period", "time_basis", "value",
        "value_kind", "conditions", "reform", "calibration_relationship",
        "source_model", "source_column", "publication", "status", "metric",
        "proposed_metric", "reform_hint",
    }
)
# Staged condition key -> DB condition key ("note" rows are identity-
# bearing variants, e.g. at_baseline_funding, so they map to "variant").
_CONDITION_KEYS = {
    "geography": "geography",
    "program": "program",
    "component": "component",
    "concept": "concept",
    "tax": "tax",
    "timing": "timing",
    "subgroup": "subgroup",
    "funder": "funder",
    "revenue_category": "revenue_category",
    "note": "variant",
    "per": "per",
    "budget_concept": "budget_concept",
    "parameter": "parameter",
}

TFP_CAP_REFORM = policy_ref("pl119_21_snap_tfp_cap")
_COST_ESTIMATE_PDF = "61367-SNAP.pdf"


def stage_scores() -> list[ExternalScore]:
    scores = []
    for row in load_staged("cbo"):
        require_fields(row, _KNOWN_FIELDS, "cbo")
        staged_conds = dict(row["conditions"])
        is_reform = staged_conds.pop("reform_hint", None) is not None
        unknown = set(staged_conds) - set(_CONDITION_KEYS)
        if unknown:
            raise ValueError(f"cbo: unmapped conditions {sorted(unknown)}")

        if is_reform:
            if row["source_model"] != "cbo_cost_estimate":
                raise ValueError("cbo: reform row without cost-estimate model")
            reform = TFP_CAP_REFORM
        else:
            if row["reform"] != {"framework": "baseline"}:
                raise ValueError(f"cbo: unexpected reform {row['reform']}")
            reform = BASELINE

        conditions = {
            _CONDITION_KEYS[k]: v for k, v in staged_conds.items()
        }
        if row["publication"].get("workbook") == _COST_ESTIMATE_PDF:
            conditions["data_vintage"] = "january_2025_baseline"

        metric_name = row.get("metric") or row["proposed_metric"]
        scores.append(
            ExternalScore(
                source="cbo",
                source_model=row["source_model"],
                metric=METRICS[metric_name],
                unit_concept=UnitConcept(row["unit_concept"]),
                period=row["period"],
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=reform,
                calibration_relationship=CalibrationRelationship(
                    row["calibration_relationship"]
                ),
                source_column=row["source_column"],
                publication=row["publication"],
                value_kind=row["value_kind"],
                status=row["status"],
            )
        )
    return finish(scores, "cbo")


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    baseline_rows = sum(1 for s in scores if s.reform is BASELINE)
    consumed = sum(
        1
        for s in scores
        if s.calibration_relationship
        is CalibrationRelationship.CONSUMED_AS_TARGET
    )
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "cbo-baseline",
        "ingested",
        f"{baseline_rows} Feb-2026 outlook claims (Medicaid/SSI/SNAP/UI/"
        f"CHIP + 330-row IIT walk); {consumed} consumed_as_target "
        "(pre-verified vs pe-us calibration/gov/cbo); June-2026 spending "
        "refresh + 4 more artifacts pending browser fetch",
        "2026-08-02",
    )
    db.set_lane(
        "cbo-cost-estimates",
        "ingested",
        f"{n - baseline_rows} single-year claims from the PL 119-21 SNAP "
        "supplement (61367, Jan-2025 baseline vintage); OBBBA cost-"
        "estimate PDFs are period-ranged verbatim pointers pending "
        "period-window staging",
        "2026-08-02",
    )
    db.close()
    return {"scores": n, "consumed_as_target": consumed}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
