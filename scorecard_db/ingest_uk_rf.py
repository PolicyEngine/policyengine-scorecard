"""Ingest the Resolution Foundation staged claims (2026-08-02 UK harvest).

71 rows, the third UK microsim lineage (IPPR Tax Benefit Model on
FRS/HBAI 2023-24): Living Standards Outlook 2026 income-growth and
poverty projections (incl. the −420k-children two-child-limit leg of
the pentagon), the Stairway-to-headroom Budget-2025 decile block, the
April-2026 uprating parameter set (pure policyengine-uk parameter
checks — the campaign's uprating_check joins here), and UC-rebalancing
analysis.

Mapping notes:
- Staged metric names map onto the shared vocabulary; where a staged
  name is absorbed into a broader Metric, conditions["source_metric"]
  keeps the original name (traceability + collision-proofing).
- Rows RF flags as citations of government figures (HMT scorecard, DWP
  IA) keep note verbatim in publication — they are RF's published
  citations, cross-checkable against the first-hand uk_hmt lane.
- The single inflation-rate-gap row (energy-price-cap scenario, a price
  -index claim with no tax/benefit content) is deliberately dropped and
  tallied.
- reform_hint rows become policy_ref worlds (uk_rf:<slug>); several
  hints carry the RF-verified policyengine-uk parameter mapping in the
  hint text verbatim.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import finish, policy_ref
from .models import (
    BASELINE,
    CalibrationRelationship,
    ExternalScore,
    Metric,
    TimeBasis,
    UnitConcept,
)
from .uk import (
    load_staged_uk,
    normalize_geography_uk,
    parse_fy,
    parse_fy_window,
    slugify,
    uk_value_kind,
)

_KNOWN_FIELDS = frozenset(
    {
        "source",
        "metric",
        "proposed_metric",
        "unit_concept",
        "proposed_unit",
        "value",
        "value_raw",
        "value_kind",
        "note",
        "local_artifact",
        "attribution",
        "period",
        "time_basis",
        "conditions",
        "reform_hint",
        "calibration_relationship",
        "source_model",
        "source_column",
        "publication",
        "status",
    }
)

_CONDITION_KEYS = {
    "geography": "geography",
    "fy": "fy",
    "income_concept": "income_concept",
    "equivalisation": "equivalisation",
    "unit_population": "unit_population",
    "scenario": "scenario",
    "growth_window": "growth_window",
    "benefit": "program",
    "income_group": "income_group",
    "poverty_line": "poverty_line",
    "impact_year": "impact_year",
    "measure_set": "measure_set",
    "income_measure": "income_measure",
    "price_base": "price_base",
    "uprating_event": "uprating_event",
    "component": "component",
    "change_window": "change_window",
    "measure": "measure_note",
    "percentile": "percentile",
}

# staged metric -> (Metric, unit, keep source_metric condition?)
_METRICS = {
    "poverty_rate": (Metric.POVERTY_RATE, UnitConcept.SHARE, False),
    "poverty_rate_change": (
        Metric.POVERTY_RATE_CHANGE,
        UnitConcept.SHARE,
        False,
    ),
    "poverty_count": (
        Metric.POVERTY_COUNT,
        UnitConcept.CHILDREN_UNDER_18,
        False,
    ),
    "poverty_count_change": (
        Metric.POVERTY_COUNT_CHANGE,
        UnitConcept.CHILDREN_UNDER_18,
        False,
    ),
    "revenue_change": (Metric.REVENUE_CHANGE, UnitConcept.GBP, False),
    "real_income_growth_pct": (
        Metric.REAL_INCOME_GROWTH,
        UnitConcept.SHARE,
        False,
    ),
    "real_income_growth_pct_pa": (
        Metric.REAL_INCOME_GROWTH,
        UnitConcept.SHARE,
        True,
    ),
    "benefit_uprating_pct": (
        Metric.BENEFIT_UPRATING,
        UnitConcept.SHARE,
        False,
    ),
    "avg_income_change": (
        Metric.AVG_CHANGE_HOUSEHOLD_NET_INCOME,
        UnitConcept.GBP_PER_HOUSEHOLD,
        False,
    ),
    "avg_gain_per_benefiting_family": (
        Metric.AVG_CHANGE_HOUSEHOLD_NET_INCOME,
        UnitConcept.GBP_PER_FAMILY,
        True,
    ),
    "avg_gain_per_unit": (
        Metric.AVG_CHANGE_HOUSEHOLD_NET_INCOME,
        UnitConcept.GBP_PER_FAMILY,
        True,
    ),
    "reform_fiscal_cost": (
        Metric.EXCHEQUER_IMPACT,
        UnitConcept.GBP,
        True,
    ),
    "share_gaining": (Metric.SHARE_GAINING, UnitConcept.SHARE, False),
    "share_losing": (Metric.SHARE_LOSING, UnitConcept.SHARE, False),
    "benefiting_family_count": (
        Metric.FAMILIES_AFFECTED_COUNT,
        UnitConcept.FAMILIES,
        True,
    ),
    "benefit_rate_weekly": (
        Metric.POLICY_PARAMETER_LEVEL,
        UnitConcept.GBP_PER_WEEK,
        True,
    ),
    "benefit_rate_gap_weekly": (
        Metric.POLICY_PARAMETER_LEVEL,
        UnitConcept.GBP_PER_WEEK,
        True,
    ),
    "real_value_change_pct": (
        Metric.POLICY_PARAMETER_LEVEL,
        UnitConcept.SHARE,
        True,
    ),
}

DROPPED_METRICS = frozenset({"inflation_rate_gap_pp"})


def stage() -> tuple[list[ExternalScore], list[dict], int]:
    scores: list[ExternalScore] = []
    dropped = 0
    for row in load_staged_uk("uk_resolution_foundation"):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_rf: unhandled fields {sorted(unknown)}")
        metric_name = row.get("metric") or row["proposed_metric"]
        if metric_name in DROPPED_METRICS:
            dropped += 1
            continue
        conds_in = dict(row["conditions"])
        unknown_c = set(conds_in) - set(_CONDITION_KEYS)
        if unknown_c:
            raise ValueError(f"uk_rf: unmapped conditions {sorted(unknown_c)}")

        geography, geo_note = normalize_geography_uk(conds_in.pop("geography"))
        conditions = {
            _CONDITION_KEYS[k]: v
            for k, v in conds_in.items()
            if v is not None and k != "fy"
        }
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note

        period_start = period_end = None
        fy_label = conds_in["fy"]
        if "to" in fy_label:
            period_start, period_end, fy_norm = parse_fy_window(fy_label)
            period = period_end
            conditions["fy"] = fy_norm
            conditions["window_kind"] = "total"
        else:
            period, fy_norm = parse_fy(fy_label)
            conditions["fy"] = fy_norm

        metric, unit, keep_name = _METRICS[metric_name]
        if keep_name:
            conditions["source_metric"] = metric_name
        if row.get("attribution"):
            # RF quoting a government figure is a different claim than
            # RF's own model estimate of the same statistic (the −420k
            # RF vs −450k govt two-child pair) — identity-bearing.
            conditions["attribution"] = row["attribution"]

        hint = row.get("reform_hint")
        if hint:
            reform = policy_ref(f"uk_rf:{slugify(hint)}")
            conditions["measure"] = hint
        else:
            reform = BASELINE

        publication = dict(row["publication"])
        for note in ("note", "local_artifact"):
            if row.get(note):
                publication[note] = row[note]

        scores.append(
            ExternalScore(
                source="resolution_foundation",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=reform,
                calibration_relationship=CalibrationRelationship(
                    row["calibration_relationship"]
                ),
                source_column=row.get("source_column"),
                publication=publication,
                value_kind=uk_value_kind(row.get("value_kind"), unit.value),
                status=row.get("status", "ok"),
                period_start=period_start,
                period_end=period_end,
            )
        )
    return finish(scores, "uk_rf"), [], dropped


def ingest(db_path: Path) -> dict:
    scores, _, dropped = stage()
    reform_rows = sum(1 for s in scores if s.reform is not BASELINE)
    uprating = sum(1 for s in scores if s.metric is Metric.BENEFIT_UPRATING)
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "rf-outlook",
        "ingested",
        f"{n} Resolution Foundation claims (IPPR Tax Benefit Model on "
        "FRS/HBAI 2023-24): LSO 2026 poverty projections incl. the −420k "
        "two-child pentagon leg, Budget-2025 decile block, April-2026 "
        f"uprating set ({uprating} parameter-check rows — campaign "
        f"uprating_check joins here); {reform_rows} reform-keyed rows; "
        f"{dropped} price-index-only row dropped (out of tax/benefit "
        "scope, tallied)",
        "2026-08-02",
    )
    db.close()
    return {"scores": n, "reform_rows": reform_rows, "dropped": dropped}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
