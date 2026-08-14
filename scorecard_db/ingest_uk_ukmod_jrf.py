"""Ingest the UKMOD + JRF staged claims (2026-08-02 UK harvest).

Two sources share one staging file (and this adapter); each row's
staged ``source`` (ukmod | jrf) is preserved.

**UKMOD** (CeMPA):
- Country Report 2023-2030 Section-4 validation block: caseloads,
  expenditure, tax revenue, distribution (4.7) and poverty (4.8) with
  UKMOD-simulated / official-estimate / input-data / HBAI columns side
  by side — conditions["series"] distinguishes sides. Official cells
  are second-hand DWP/HMRC/OBR citations and deliberately stay
  scorecard-side under source ukmod (the block's value IS the
  side-by-side; first-hand admin outturns live in the Ledger via the
  DWP/HMRC lanes, not here).
- CeMPA WP 3/26 Autumn-Budget-2025 package assessment: scenario
  base/reform/change rows — the package is one policy_ref world
  (uk_autumn_budget_2025_package_cempa) scored against pre-package
  current law at announcement.

**JRF**: UK Poverty 2026 workbook series (unrounded headline AHC
poverty, persistent poverty, thresholds, medians) — permanent poverty
holdouts. The 88 MIS weekly-budget cells are deliberately DROPPED
(tallied): MIS budget standards are focus-group budgets, not
tax/benefit-model outputs PE can check; they stay recoverable in the
vendored staging.

Gotchas encoded here: income_concept is load-bearing (UKMOD validation
poverty = BHC, JRF headline = AHC); staged value_kind "currency_gbp"
normalizes to gbp; JRF's basis weekly|annual is an AMOUNT basis and is
remapped to conditions["amount_basis"] (basis keeps its UK
outturn/forecast semantics); 3-year-average persistent-poverty windows
become period_start/period_end with window_kind=annual_average.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import finish, merge_republications, policy_ref
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
        "normalization",
        "parse_confidence",
        "period",
        "time_basis",
        "conditions",
        "reform",
        "reform_hint",
        "calibration_relationship",
        "source_model",
        "source_column",
        "source_table",
        "publication",
        "status",
        "official_sources_note",
    }
)

_CONDITION_KEYS = {
    "geography": "geography",
    "fy": "fy",
    "series": "series",
    "program": "program",
    "forecast_note": None,  # table-level note -> publication
    "income_concept": "income_concept",
    "ukmod_variable": "ukmod_variable",
    "subgroup": "subgroup",
    "count_unit": "count_unit",
    "poverty_line": "poverty_line",
    "scenario": "scenario",
    "income_definition": "income_definition",
    "equivalisation": "equivalisation",
    "unit_of_analysis": "unit_of_analysis",
    "coverage_note": None,  # series-level note -> publication
    "quintile": "quintile",
    "household_type": "household_type",
    "budget_component": "budget_component",
    "priced": "priced",
    "poverty_line_type": "poverty_line_type",
    "family_type": "family_type",
    "threshold": "threshold",
    "income_concept_note": None,  # -> publication
    "basis": "amount_basis",  # JRF weekly|annual — NOT outturn/forecast
    "poverty_depth": "poverty_depth",
    "measure": "poverty_duration_measure",
    "period_window": None,  # handled -> period_start/period_end
    "subgroup_axis": "subgroup_axis",
    "child_definition": "child_definition",
}
_PUBLICATION_NOTES = ("forecast_note", "coverage_note", "income_concept_note")

# staged metric -> (Metric, unit chooser key)
_METRICS = {
    "poverty_rate": Metric.POVERTY_RATE,
    "poverty_count": Metric.POVERTY_COUNT,
    "poverty_count_change": Metric.POVERTY_COUNT_CHANGE,
    "persistent_poverty_rate": Metric.PERSISTENT_POVERTY_RATE,
    "benefit_cost": Metric.BENEFIT_COST,
    "caseload": Metric.CASELOAD,
    "revenue_change": Metric.REVENUE_CHANGE,
    "tax_revenue": Metric.REVENUE_LEVEL,
    "taxpayer_count": Metric.TAXPAYER_COUNT,
    "government_revenue": Metric.REVENUE_LEVEL,
    "government_expenditure": Metric.EXPENDITURE_LEVEL,
    "expenditure_change": Metric.EXPENDITURE_CHANGE,
    "net_fiscal_impact": Metric.EXCHEQUER_IMPACT,
    "net_fiscal_impact_per_capita": Metric.EXCHEQUER_IMPACT,
    "median_equivalised_disposable_income": Metric.MEDIAN_INCOME,
    "mean_equivalised_disposable_income": Metric.MEAN_INCOME,
    "median_income": Metric.MEDIAN_INCOME,
    "income_share": Metric.INCOME_SHARE,
    "gini_coefficient": Metric.GINI_COEFFICIENT,
    "gini_coefficient_change": Metric.GINI_COEFFICIENT_CHANGE,
    "s80_s20_ratio": Metric.S80_S20_RATIO,
    "s80_s20_ratio_change": Metric.S80_S20_RATIO_CHANGE,
    "poverty_threshold": Metric.POVERTY_THRESHOLD,
}

_UNIT_BY_PROPOSED = {
    "gbp": UnitConcept.GBP,
    "gbp_per_week": UnitConcept.GBP_PER_WEEK,
    "gbp_per_month": UnitConcept.GBP_PER_MONTH,
    "gbp_per_year": UnitConcept.GBP_PER_YEAR,
    "gbp_per_person": UnitConcept.GBP_PER_PERSON,
    "gini_0_1": UnitConcept.INDEX_0_1,
    "gini_points_0_100": UnitConcept.INDEX_POINTS_0_100,
    "ratio": UnitConcept.RATIO,
}
_UNIT_BY_STAGED = {
    "persons": UnitConcept.PERSONS,
    "families": UnitConcept.FAMILIES,
    "households": UnitConcept.HOUSEHOLDS,
}

AB2025_PACKAGE = policy_ref("uk_autumn_budget_2025_package_cempa")

DROPPED_METRICS = frozenset({"minimum_income_standard_budget"})


def _unit_for(row: dict, metric: Metric) -> UnitConcept:
    if metric in (
        Metric.POVERTY_RATE,
        Metric.PERSISTENT_POVERTY_RATE,
        Metric.INCOME_SHARE,
    ):
        return UnitConcept.SHARE
    if row.get("unit_concept"):
        return _UNIT_BY_STAGED[row["unit_concept"]]
    proposed = row.get("proposed_unit")
    if proposed:
        unit = _UNIT_BY_PROPOSED[proposed]
        # JRF threshold/median tables publish bare-gbp cells whose
        # weekly/annual basis rides the staged basis flag.
        if unit is UnitConcept.GBP and row["conditions"].get("basis"):
            return {
                "weekly": UnitConcept.GBP_PER_WEEK,
                "annual": UnitConcept.GBP_PER_YEAR,
            }[row["conditions"]["basis"]]
        return unit
    if row.get("value_kind") in ("currency_gbp", "gbp"):
        return UnitConcept.GBP
    raise ValueError(f"uk_ukmod_jrf: no unit for row {row['source_column']!r}")


def stage() -> tuple[list[ExternalScore], list[dict], int]:
    scores: list[ExternalScore] = []
    dropped = 0
    for row in load_staged_uk("uk_ukmod_jrf"):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_ukmod_jrf: unhandled fields {sorted(unknown)}")
        metric_name = row.get("metric") or row["proposed_metric"]
        if metric_name in DROPPED_METRICS:
            dropped += 1
            continue
        conds_in = dict(row["conditions"])
        unknown_c = set(conds_in) - set(_CONDITION_KEYS)
        if unknown_c:
            raise ValueError(f"uk_ukmod_jrf: unmapped conditions {sorted(unknown_c)}")

        geography, geo_note = normalize_geography_uk(conds_in.pop("geography"))
        conditions = {}
        for k, v in conds_in.items():
            target = _CONDITION_KEYS[k]
            if target and v is not None and k != "fy":
                conditions[target] = v
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note

        period_start = period_end = None
        window_label = conds_in.get("period_window")
        if window_label:
            period_start, period_end, fy_norm = parse_fy_window(
                window_label.split(" (")[0]
            )
            period = period_end
            conditions["fy"] = fy_norm
            conditions["window_kind"] = "annual_average"
        else:
            period, fy_norm = parse_fy(conds_in["fy"])
            conditions["fy"] = fy_norm

        scenario = conds_in.get("scenario")
        if row.get("reform") is not None:
            if row["reform"] != {"framework": "baseline"}:
                raise ValueError(f"uk_ukmod_jrf: unexpected reform {row['reform']}")
            if scenario is not None:
                raise ValueError("uk_ukmod_jrf: baseline-reform row carries scenario")
            reform = BASELINE
        else:
            # CeMPA WP 3/26 package block: scenario base/reform/change.
            if scenario == "baseline":
                reform = BASELINE
            elif scenario in ("reform", "reform_minus_baseline"):
                reform = AB2025_PACKAGE
                conditions["measure"] = row["reform_hint"]
            else:
                raise ValueError(f"uk_ukmod_jrf: reform-block scenario {scenario!r}")

        metric = _METRICS[metric_name]
        unit = _unit_for(row, metric)
        if metric_name == "net_fiscal_impact_per_capita":
            unit = UnitConcept.GBP_PER_PERSON

        publication = dict(row["publication"])
        if row.get("source_table"):
            publication.setdefault("table", row["source_table"])
        if row.get("normalization"):
            publication["normalization"] = row["normalization"]
        if row.get("official_sources_note"):
            publication["official_sources_note"] = row["official_sources_note"]
        for k in _PUBLICATION_NOTES:
            if conds_in.get(k):
                publication[k] = conds_in[k]

        scores.append(
            ExternalScore(
                source=row["source"],
                source_model=row.get("source_model"),
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

    # JRF republishes the same statistic across workbook sheets (rounded
    # overview vs unrounded headline series): one claim, two artifacts —
    # keep the higher-precision cell, require rounding-consistency, and
    # record the twin under publication["also_published"].
    def _decimals(s: ExternalScore) -> int:
        text = repr(s.value)
        return len(text.split(".")[1]) if "." in text else 0

    scores = merge_republications(
        scores,
        "uk_ukmod_jrf",
        precision=_decimals,
        tolerance=lambda coarse: 0.5 * 10 ** -_decimals(coarse) + 1e-12,
    )
    return finish(scores, "uk_ukmod_jrf"), [], dropped


def ingest(db_path: Path) -> dict:
    scores, _, dropped = stage()
    ukmod = sum(1 for s in scores if s.source == "ukmod")
    jrf = sum(1 for s in scores if s.source == "jrf")
    reform_rows = sum(1 for s in scores if s.reform is AB2025_PACKAGE)
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "ukmod-stats",
        "ingested",
        f"{ukmod} UKMOD claims — Country Report 2023-2030 validation "
        "block (simulated/official/input-data/HBAI series side by side; "
        "take-up priors frozen since 2021 per their own §4.3 warning) + "
        f"CeMPA 3/26 AB2025 package assessment ({reform_rows} "
        f"reform-keyed rows); {jrf} JRF claims (unrounded AHC headline "
        f"series, persistent poverty, MIS-adjacent thresholds); {dropped} "
        "MIS weekly-budget cells deliberately dropped (focus-group budget "
        "standards, not model-checkable — recoverable in vendored "
        "staging)",
        "2026-08-02",
    )
    db.close()
    return {
        "scores": n,
        "ukmod": ukmod,
        "jrf": jrf,
        "reform_rows": reform_rows,
        "dropped_mis": dropped,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
