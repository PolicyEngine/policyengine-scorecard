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

Publication 61367's period-window numbers (lane cbo-cost-estimates) come
from sources/cbo-pl119-21 (data/externals/cbo-pl119-21.json), not from the
harvest: the decile distribution of the whole law (2026-2034 annual
averages, Figures 1-2 data) and the SNAP supplement's section 10102-10105
statements. Every 61367 reform claim, the harvest's TFP-cap row included,
is scored against the explicit baseline cbo_january_2025_baseline: CBO
published after enactment, so the law in force was no longer its
counterfactual.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import (
    REPO,
    finish,
    load_staged,
    parse_window,
    policy_ref,
    require_fields,
    with_baseline_condition,
)
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
        "source",
        "unit_concept",
        "period",
        "time_basis",
        "value",
        "value_kind",
        "conditions",
        "reform",
        "calibration_relationship",
        "source_model",
        "source_column",
        "publication",
        "status",
        "metric",
        "proposed_metric",
        "reform_hint",
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

CBO_JAN_2025 = {"policy": "cbo_january_2025_baseline"}
TFP_CAP_REFORM = policy_ref("pl119_21_snap_tfp_cap", baseline=CBO_JAN_2025)
_COST_ESTIMATE_PDF = "61367-SNAP.pdf"

PL119_21_EXTRACT = REPO / "data" / "externals" / "cbo-pl119-21.json"
# The whole law: the slug PWBM's enacted-law rows also use.
ENACTED_REFORM = policy_ref("obbba_enacted_pl119_21", baseline=CBO_JAN_2025)
# Each SNAP section "as if implemented on its own" (supplement p. 1).
SECTION_REFORMS = {
    "10102": policy_ref("pl119_21_snap_work_requirements", baseline=CBO_JAN_2025),
    "10103": policy_ref("pl119_21_snap_sua_energy_assistance", baseline=CBO_JAN_2025),
    "10104": policy_ref("pl119_21_snap_internet_expenses", baseline=CBO_JAN_2025),
    "10105": policy_ref("pl119_21_snap_state_matching_funds", baseline=CBO_JAN_2025),
}
# Deciles rank households by income after transfers and taxes, adjusted
# for household size (letter note 7).
_DECILE_AXIS = "income_after_transfers_and_taxes_size_adjusted_decile"
_PUBLICATIONS = {
    "distribution": {
        "title": "Distributional Effects of Public Law 119-21 (letter to "
        "Ranking Member Boyle, Leader Jeffries, Ranking Member Merkley and "
        "Leader Schumer)",
        "url": "https://www.cbo.gov/system/files/2025-08/61367-data.xlsx",
        "publication_url": "https://www.cbo.gov/publication/61367",
        "date": "2025-08-11",
        "vintage": "vs January 2025 baseline",
        "workbook": "61367-data.xlsx",
        "price_basis": "2025 dollars, adjusted with the PCE price index",
    },
    "snap": {
        "title": "Estimated Effects of Public Law 119-21 on Participation "
        "and Benefits Under SNAP (supplemental information)",
        "url": "https://www.cbo.gov/system/files/2025-08/61367-SNAP.pdf",
        "publication_url": "https://www.cbo.gov/publication/61367",
        "date": "2025-08-11",
        "vintage": "vs January 2025 baseline",
        "workbook": _COST_ESTIMATE_PDF,
        "independence": "each section as if implemented on its own; no "
        "interactions among provisions",
    },
}
_VALUE_KINDS = {
    "usd_per_household": "usd",
    "percent": "percent",
    "persons": "count",
    "children": "count",
    "usd": "usd",
    "share": "share",
}
_SOURCE_MODELS = {
    "distribution": "cbo_distributional_analysis",
    "snap": "cbo_cost_estimate",
}


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

        conditions = {_CONDITION_KEYS[k]: v for k, v in staged_conds.items()}
        if row["publication"].get("workbook") == _COST_ESTIMATE_PDF:
            conditions["data_vintage"] = "january_2025_baseline"
        with_baseline_condition(conditions, reform)

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


def stage_pl119_21() -> list[ExternalScore]:
    """Publication 61367's period-window claims from the adapter's extract.
    Every row's fields are consumed explicitly; an unknown family, section
    or unit raises."""
    scores = []
    for row in json.loads(PL119_21_EXTRACT.read_text()):
        family = row["family"]
        conditions = {"geography": row["geography"]}
        if family == "distribution":
            reform = ENACTED_REFORM
            conditions.update(
                income_axis=_DECILE_AXIS,
                income_concept="after_tax_and_transfer_income",
            )
        elif family == "snap":
            reform = SECTION_REFORMS[row["section"]]
            conditions["program"] = row["program"]
        else:
            raise ValueError(f"cbo-pl119-21: unknown family {family!r}")
        conditions.update(row["conditions"])
        conditions["window_kind"] = row["window_kind"]
        with_baseline_condition(conditions, reform)
        start, end = parse_window(row["period"])
        scores.append(
            ExternalScore(
                source="cbo",
                source_model=_SOURCE_MODELS[family],
                metric=Metric(row["metric"]),
                unit_concept=UnitConcept(row["unit_concept"]),
                period=end,
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=reform,
                calibration_relationship=CalibrationRelationship.HELD_OUT,
                source_column=row["source_column"],
                publication=_PUBLICATIONS[family],
                value_kind=_VALUE_KINDS[row["unit_concept"]],
                status=row["status"],
                period_start=start,
                period_end=end,
            )
        )
    return scores


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    windows = stage_pl119_21()
    baseline_rows = sum(1 for s in scores if s.reform is BASELINE)
    consumed = sum(
        1
        for s in scores
        if s.calibration_relationship is CalibrationRelationship.CONSUMED_AS_TARGET
    )
    db = ScorecardDB(db_path)
    n = db.upsert_scores(finish(scores + windows, "cbo"))
    db.set_lane(
        "cbo-baseline",
        "ingested",
        f"{baseline_rows} Feb-2026 outlook claims (Medicaid/SSI/SNAP/UI/"
        f"CHIP + 330-row IIT walk); {consumed} consumed_as_target "
        "(pre-verified vs pe-us calibration/gov/cbo); June-2026 spending "
        "refresh + 4 more artifacts pending browser fetch",
        "2026-08-02",
    )
    distribution = sum(1 for s in windows if s.reform is ENACTED_REFORM)
    db.set_lane(
        "cbo-cost-estimates",
        "ingested",
        f"{len(scores) - baseline_rows} single-year claim (TFP cap, 2034) "
        f"and {len(windows)} period-window claims from publication 61367 "
        f"({distribution} decile-distribution cells, 2026-34 annual "
        f"averages; {len(windows) - distribution} SNAP section 10102-10105 "
        "statements), all vs CBO's January 2025 baseline; the other OBBBA "
        "PDFs are set aside with reasons in sources/cbo-pl119-21/"
        "source.json; no PE counterparts yet (they need the January-2025 "
        "world run over each window)",
        "2026-10-15",
    )
    db.close()
    return {"scores": n, "consumed_as_target": consumed}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
