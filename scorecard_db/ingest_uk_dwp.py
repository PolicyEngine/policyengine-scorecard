"""Ingest the DWP staged claims (2026-08-02 UK harvest).

Four families:

- **HBAI headline poverty** (dwp_hbai_frs, 1,040): rates and counts,
  FYE 1995–2025, relative & absolute × BHC & AHC, two editions (FYE-2025
  + the FYE-2024 admin-linked restatement pair — conditions["edition"]).
  Survey-outcome statistics, NOT admin outturn: they stay scorecard-side
  as permanent holdouts (poverty may never be a calibration target).
- **Income-related-benefit take-up estimates** (dwp_takeup_estimates,
  805): DWP's own eligibility-model estimates with lower/central/upper
  bounds. Pension Credit rows arrive seed_source — policyengine-uk
  gov/dwp/pension_credit/takeup.yaml cites this series (verified by the
  harvest agent); HB rows stay held_out, the live external comparator
  for PE-UK's takeup=1 assumption (policyengine-uk#1813).
- **Benefit expenditure & caseload (BECL)**, Spring-2026, OBR-consistent
  (dwp_becl, 204): outturn rows are admin facts → Ledger staging;
  forecast rows enter. Expenditure forecasts whose benefit is a Table
  4.9 line populace-UK literally consumes (targets/sources/obr.py, read
  this session) → consumed_as_target: state_pension, universal_credit,
  pension_credit, attendance_allowance, child_benefit. dla/pip stay
  held_out — populace consumes only their COMBINED 4.9 line, and BECL
  caseloads stay held_out — obr.py parses expenditure only.
- **UC admin release** (dwp_uc_admin, 5, point-in-time Feb-2026):
  consumed_as_target — targets/sources/dwp.py consumes UC claimant
  counts and the payment distribution from this same admin series
  (staged VERIFIED note, re-read this session).

Period is re-derived from the fy label (FYE end-year convention and the
'1999/00'→1900 staging defect both normalize to FY start year).
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import finish
from .models import (
    BASELINE,
    CalibrationRelationship,
    ExternalScore,
    Metric,
    TimeBasis,
    UnitConcept,
)
from .uk import (
    ledger_row,
    load_staged_uk,
    normalize_geography_uk,
    parse_fy,
    uk_value_kind,
)

_KNOWN_FIELDS = frozenset(
    {
        "source", "metric", "proposed_metric", "unit_concept",
        "proposed_unit", "value", "value_raw", "value_kind", "conversion",
        "period", "time_basis", "conditions", "reform",
        "calibration_relationship", "calibration_note", "series_note",
        "time_note", "geography_note", "unit_note",
        "source_model", "source_column", "publication", "status",
    }
)

_CONDITION_KEYS = {
    "geography": "geography",
    "fy": "fy",
    "edition": "edition",
    "subgroup": "subgroup",
    "income_concept": "income_concept",
    "poverty_measure": "poverty_measure",
    "poverty_line": "poverty_line",
    "poverty_line_anchor": "poverty_line_anchor",
    "equivalisation": "equivalisation",
    "benefit": "program",
    "entitlement_group": "entitlement_group",
    "bound": "bound",
    "takeup_basis": "takeup_basis",
    "basis": "basis",
    "data_vintage": "data_vintage",
    "component": "component",
    "family_type": "family_type",
    "age_group": "age_group",
    "month": "month",
    "geography_note": "geography_note",
}

_METRICS = {
    "poverty_rate": Metric.POVERTY_RATE,
    "poverty_count": Metric.POVERTY_COUNT,
    "participation_rate": Metric.PARTICIPATION_RATE,
    "participation_gap_count": Metric.PARTICIPATION_GAP_COUNT,
    "participant_count": Metric.PARTICIPANT_COUNT,
    "benefit_cost": Metric.BENEFIT_COST,
    "caseload": Metric.CASELOAD,
    "unclaimed_expenditure": Metric.UNCLAIMED_EXPENDITURE,
}

_UNITS = {
    "persons": UnitConcept.PERSONS,
    "families": UnitConcept.FAMILIES,
    "households": UnitConcept.HOUSEHOLDS,
    "children_under_18": UnitConcept.CHILDREN_UNDER_18,
    "adults_18plus": UnitConcept.ADULTS_18PLUS,
}

# BECL expenditure forecasts whose benefit is an exact Table 4.9 line
# populace-UK consumes (policyengine-uk-data targets/sources/obr.py,
# read 2026-08-02). BECL is published OBR-Spring-2026-consistent, so
# these series are the same quantity class as the consumed forecasts.
_BECL_CONSUMED = {
    "state_pension": "obr/state_pension",
    "universal_credit": "obr/universal_credit_in_cap + outside_cap",
    "pension_credit": "obr/pension_credit",
    "attendance_allowance": "obr/attendance_allowance",
    "child_benefit": "obr/child_benefit",
}
_BECL_CONSUMED_BASIS = (
    "BECL Spring-2026 is OBR-forecast-consistent and policyengine-uk-data "
    "targets/sources/obr.py consumes the matching EFO Table 4.9 "
    "expenditure line ({target}; read 2026-08-02) — same series class, so "
    "agreement is discipline, not validation"
)
_BECL_COMPONENT_HELDOUT_NOTE = (
    "held_out deliberately: populace-UK consumes only the COMBINED "
    "DLA+PIP Table 4.9 line; this BECL component split is not itself a "
    "target (partial discipline via the consumed aggregate, noted)"
)
_BECL_CASELOAD_NOTE = (
    "held_out deliberately: targets/sources/obr.py parses Table 4.9 "
    "expenditure only (read 2026-08-02) — BECL caseload forecasts are "
    "not consumed"
)


def stage() -> tuple[list[ExternalScore], list[dict]]:
    scores: list[ExternalScore] = []
    ledger: list[dict] = []
    for row in load_staged_uk("uk_dwp"):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_dwp: unhandled fields {sorted(unknown)}")
        if row["reform"] != {"framework": "baseline"}:
            raise ValueError(f"uk_dwp: unexpected reform {row['reform']}")
        conds_in = dict(row["conditions"])
        if (
            row["source_model"] == "dwp_becl"
            and conds_in.get("basis") == "outturn"
        ):
            ledger.append(
                ledger_row(
                    "uk_dwp", row,
                    "DWP BECL outturn — admin expenditure/caseload fact "
                    "(ledger routing rule, Max 2026-08-02)",
                )
            )
            continue

        unknown_c = set(conds_in) - set(_CONDITION_KEYS)
        if unknown_c:
            raise ValueError(f"uk_dwp: unmapped conditions {sorted(unknown_c)}")
        geography, geo_note = normalize_geography_uk(conds_in.pop("geography"))
        conditions = {
            _CONDITION_KEYS[k]: v
            for k, v in conds_in.items()
            if v is not None and k != "fy"
        }
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note
        if "fy" in conds_in:
            period, fy_norm = parse_fy(conds_in["fy"])
            conditions["fy"] = fy_norm
        else:
            if row["time_basis"] != "point_in_time":
                raise ValueError("uk_dwp: fy missing on non-point-in-time row")
            period = row["period"]

        metric_name = row.get("metric") or row["proposed_metric"]
        metric = _METRICS[metric_name]
        if metric in (Metric.POVERTY_RATE, Metric.PARTICIPATION_RATE):
            unit = UnitConcept.SHARE
        elif row.get("unit_concept"):
            unit = _UNITS[row["unit_concept"]]
        elif (row.get("proposed_unit") or row.get("value_kind")) in (
            "gbp", "currency_gbp",
        ):
            unit = UnitConcept.GBP
        else:
            raise ValueError(f"uk_dwp: no unit for {metric_name}")

        relationship = CalibrationRelationship(row["calibration_relationship"])
        publication = dict(row["publication"])
        if row.get("calibration_note"):
            publication["calibration_basis"] = row["calibration_note"]
        for note in ("series_note", "time_note", "unit_note"):
            if row.get(note):
                publication[note] = row[note]
        if row.get("geography_note"):
            # Verbatim devolution scope (DLA/PIP/AA England&Wales-only
            # from FY 2020/21) — identity-adjacent, keep on conditions.
            conditions["geography_note"] = row["geography_note"]
        if row.get("time_note"):
            # BECL Notes: caseloads are full-financial-year averages —
            # load-bearing vs point-in-time admin counts (UC 5.47M FY-avg
            # vs 7.2M Feb-2026), so it rides conditions.
            conditions["caseload_basis"] = "fy_average"

        if row["source_model"] == "dwp_becl":
            program = conditions.get("program")
            if metric is Metric.BENEFIT_COST and program in _BECL_CONSUMED:
                relationship = CalibrationRelationship.CONSUMED_AS_TARGET
                publication["calibration_basis"] = (
                    _BECL_CONSUMED_BASIS.format(
                        target=_BECL_CONSUMED[program]
                    )
                )
            elif metric is Metric.BENEFIT_COST and program in ("dla", "pip"):
                publication["calibration_basis"] = (
                    _BECL_COMPONENT_HELDOUT_NOTE
                )
            elif metric is Metric.CASELOAD:
                publication["calibration_basis"] = _BECL_CASELOAD_NOTE
        elif row["source_model"] == "dwp_uc_admin":
            # Staged VERIFIED note: targets/sources/dwp.py consumes this
            # same Feb-2026 admin series (re-read 2026-08-02).
            relationship = CalibrationRelationship.CONSUMED_AS_TARGET

        scores.append(
            ExternalScore(
                source="dwp",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=BASELINE,
                calibration_relationship=relationship,
                source_column=row.get("source_column"),
                publication=publication,
                value_kind=uk_value_kind(row.get("value_kind"), unit.value),
                status=row.get("status", "ok"),
            )
        )
    return finish(scores, "uk_dwp"), ledger


def ingest(db_path: Path) -> dict:
    scores, ledger = stage()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    by_model: dict[str, int] = {}
    for s in scores:
        by_model[s.source_model] = by_model.get(s.source_model, 0) + 1
    consumed = sum(
        1
        for s in scores
        if s.calibration_relationship
        is CalibrationRelationship.CONSUMED_AS_TARGET
    )
    seeded = sum(
        1
        for s in scores
        if s.calibration_relationship is CalibrationRelationship.SEED_SOURCE
    )
    db.set_lane(
        "hbai-poverty",
        "ingested",
        f"{by_model.get('dwp_hbai_frs', 0)} HBAI claims (FYE 1995-2025, "
        "relative+absolute × BHC+AHC, rates+counts; FYE-2025 + admin-"
        "linked FYE-2024 edition pair staged — the ~2pp methodology-gap "
        "diagnosis seed); permanent poverty holdout",
        "2026-08-02",
    )
    db.set_lane(
        "dwp-takeup",
        "ingested",
        f"{by_model.get('dwp_takeup_estimates', 0)} take-up claims with "
        f"bounds ({seeded} PC rows seed_source — pe-uk takeup.yaml cites "
        "this series; HB rows held_out vs PE takeup=1, "
        "policyengine-uk#1813); "
        f"{by_model.get('dwp_becl', 0)} BECL forecast rows "
        f"({consumed - by_model.get('dwp_uc_admin', 0)} expenditure lines "
        "consumed_as_target via OBR 4.9); "
        f"{len(ledger)} BECL outturn rows routed to Ledger staging",
        "2026-08-02",
    )
    db.close()
    return {
        "scores": n,
        "ledger": len(ledger),
        "consumed": consumed,
        "seed_source": seeded,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
