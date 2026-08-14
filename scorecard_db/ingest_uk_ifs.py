"""Ingest the IFS TAXBEN staged claims (2026-08-02 UK harvest).

268 rows: absolute-AHC child-poverty series and the Green-Budget-2025
benefit-options block (13 options × poverty/cost/distribution metrics),
Autumn-Budget-2025 package analysis, and threshold-freeze revenue rows.

The options block is scored against a named non-current-law baseline —
"current tax-benefit system with two-child limit and family premium
removal fully rolled out" (steady state) — which becomes the registered
baseline world ifs_2cl_fp_removal_rolled_out on the ReformRef (issue
#13: baseline variants are load-bearing, never conditions-only; the
steady-state horizon additionally rides conditions["horizon"]). IFS
TAXBEN is deliberately full-take-up (entitlements basis) — the
assumptions-registry axis on every UK poverty comparison.

Poverty metrics stay permanent holdouts; everything is held_out as
staged (no populace-UK consumption of IFS outputs).
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import finish, with_baseline_condition
from .models import (
    BASELINE,
    CalibrationRelationship,
    ExternalScore,
    Metric,
    ReformRef,
    TimeBasis,
    UnitConcept,
)
from .uk import (
    load_staged_uk,
    normalize_geography_uk,
    parse_fy,
    slugify,
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
        "normalization",
        "parse_confidence",
        "sign_convention",
        "geography_note",
        "period",
        "time_basis",
        "conditions",
        "reform_hint",
        "calibration_relationship",
        "source_model",
        "source_column",
        "source_table",
        "publication",
    }
)

_CONDITION_KEYS = {
    "geography": "geography",
    "fy": "fy",
    "income_concept": "income_concept",
    "population": "subgroup",
    "poverty_measure": "poverty_measure",
    "poverty_line": "poverty_line",
    "data_vintage": "data_vintage",
    "baseline": None,  # handled: becomes the ReformRef baseline world
    "time_note": None,  # handled: steady-state horizon marker
    "income_group": "income_group",
    "income_axis": "income_axis",
    "share_denominator": "share_denominator",
    "tax_category": "tax_category",
    "counterfactual": "counterfactual",
    "policy": "policy_note",
    "program": "program",
    # provenance notes -> publication
    "method_note": None,
    "scope_note": None,
    "costing_basis": None,
    "row_source_note": None,
    "description_verbatim": "description",
    "uncertainty_verbatim": None,
    "attribution_note": None,
}
_PUBLICATION_NOTES = (
    "method_note",
    "scope_note",
    "costing_basis",
    "row_source_note",
    "uncertainty_verbatim",
    "attribution_note",
)

_METRICS = {
    "poverty_rate": (Metric.POVERTY_RATE, UnitConcept.SHARE),
    "poverty_rate_change": (
        Metric.POVERTY_RATE_CHANGE,
        UnitConcept.PERCENTAGE_POINTS,
    ),
    "revenue_change": (Metric.REVENUE_CHANGE, UnitConcept.GBP),
    "benefit_spending_change": (
        Metric.EXPENDITURE_CHANGE,
        UnitConcept.GBP,
    ),
    "share_of_spending_to_group": (
        Metric.SHARE_OF_SPENDING_TO_GROUP,
        UnitConcept.PERCENT,
    ),
    "avg_change_household_net_income": (
        Metric.AVG_CHANGE_HOUSEHOLD_NET_INCOME,
        UnitConcept.GBP_PER_YEAR,
    ),
    "cost_per_child_lifted_out_of_poverty": (
        Metric.COST_PER_CHILD_LIFTED_OUT_OF_POVERTY,
        UnitConcept.GBP,
    ),
    "taxpayer_count_change": (
        Metric.TAXPAYER_COUNT_CHANGE,
        UnitConcept.PERSONS,
    ),
    "families_affected_count": (
        Metric.FAMILIES_AFFECTED_COUNT,
        UnitConcept.FAMILIES,
    ),
}
_COUNT_UNITS = {
    "children_under_18": UnitConcept.CHILDREN_UNDER_18,
    "persons": UnitConcept.PERSONS,
}

# The Green-Budget options baseline (verbatim staged condition value).
STEADY_STATE_BASELINE = {"policy": "ifs_2cl_fp_removal_rolled_out"}
_STEADY_STATE_VERBATIM = (
    "current tax-benefit system with two-child limit and family premium "
    "removal fully rolled out"
)


def stage() -> tuple[list[ExternalScore], list[dict]]:
    scores: list[ExternalScore] = []
    for row in load_staged_uk("uk_ifs"):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_ifs: unhandled fields {sorted(unknown)}")
        conds_in = dict(row["conditions"])
        unknown_c = set(conds_in) - set(_CONDITION_KEYS)
        if unknown_c:
            raise ValueError(f"uk_ifs: unmapped conditions {sorted(unknown_c)}")

        geography, geo_note = normalize_geography_uk(conds_in.pop("geography"))
        conditions = {}
        for k, v in conds_in.items():
            target = _CONDITION_KEYS[k]
            if target and v is not None and k != "fy":
                conditions[target] = v
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note
        if "fy" in conds_in:
            period, fy_norm = parse_fy(conds_in["fy"])
            conditions["fy"] = fy_norm
        else:
            period = row["period"]  # calendar-year series rows

        baseline_verbatim = conds_in.get("baseline")
        if baseline_verbatim is not None:
            if baseline_verbatim != _STEADY_STATE_VERBATIM:
                raise ValueError(f"uk_ifs: unregistered baseline {baseline_verbatim!r}")
            conditions["horizon"] = "steady_state"

        hint = row.get("reform_hint")
        if hint:
            reform = ReformRef(
                framework="policy_ref",
                reform={"policy": f"uk_ifs:{slugify(hint)}"},
                baseline=(STEADY_STATE_BASELINE if baseline_verbatim else None),
            )
            conditions["measure"] = hint
            conditions = with_baseline_condition(conditions, reform)
        elif baseline_verbatim:
            # Level claim of the steady-state world itself.
            reform = ReformRef(
                framework="policy_ref", reform=dict(STEADY_STATE_BASELINE)
            )
        else:
            reform = BASELINE

        metric_name = row.get("metric") or row["proposed_metric"]
        if metric_name == "poverty_count_change":
            metric = Metric.POVERTY_COUNT_CHANGE
            unit = _COUNT_UNITS[row["unit_concept"]]
        else:
            metric, unit = _METRICS[metric_name]
        if metric is Metric.SHARE_OF_SPENDING_TO_GROUP:
            # The recipient group lives only in the column header
            # ("Of which transfers to households with children in
            # poverty" / "…poorest 40% not in poverty" / "…richest 60%")
            # — identity-bearing, so it becomes a condition verbatim.
            conditions["recipient_group"] = row["source_column"]

        publication = dict(row["publication"])
        if row.get("source_table"):
            publication.setdefault("table", row["source_table"])
        for note in ("normalization", "sign_convention", "geography_note"):
            if row.get(note):
                publication[note] = row[note]
        for k in _PUBLICATION_NOTES:
            if conds_in.get(k):
                publication[k] = conds_in[k]

        scores.append(
            ExternalScore(
                source="ifs",
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
                value_kind=(
                    "gbp"
                    if unit
                    in (
                        UnitConcept.GBP,
                        UnitConcept.GBP_PER_YEAR,
                    )
                    else "share"
                    if unit
                    in (
                        UnitConcept.SHARE,
                        UnitConcept.PERCENT,
                        UnitConcept.PERCENTAGE_POINTS,
                    )
                    else "count"
                ),
            )
        )
    return finish(scores, "uk_ifs"), []


def ingest(db_path: Path) -> dict:
    scores, _ = stage()
    reform_rows = sum(1 for s in scores if s.reform is not BASELINE)
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "ifs-taxben",
        "ingested",
        f"{n} TAXBEN claims: absolute-AHC child-poverty series, "
        f"Green-Budget-2025 options block ({reform_rows} reform-keyed "
        "rows incl. the −540k steady-state two-child-limit leg of the "
        "pentagon), threshold-freeze revenue rows; options baseline = "
        "registered ifs_2cl_fp_removal_rolled_out world; TAXBEN is "
        "entitlements-basis (full take-up) — registry axis on every "
        "poverty comparison",
        "2026-08-02",
    )
    db.close()
    return {"scores": n, "reform_rows": reform_rows}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
