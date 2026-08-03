"""Ingest the OBR staged claims (2026-08-02 UK harvest).

Two families:

1. **Policy measures database** (24,304 rows, source_model
   hmt_scorecard_obr_database): every scorecard measure since 1970 ×
   fiscal years — reform scores. Each measure title becomes a policy_ref
   world (uk_obr_measure:<event>:<title-hash>) with the verbatim title in
   conditions["measure"]; scored against current law at announcement
   (null baseline — JCT parity), the event riding conditions.
   sign_convention is uniform positive_gain_to_exchequer.

2. **EFO supplementary tables** (1,254 rows, source_model
   obr_efo_forecast): Mar-2026 receipts levels (3.4 accrued / 3.8 cash)
   and threshold-freeze analysis (3.17 revenue re-estimates →
   policy_ref worlds; 3.18 taxpayer counts; 3.19 parameter levels —
   scenario rides conditions verbatim, basis "unstated" per the tables'
   own missing markers), plus Nov-2025 welfare spending (4.9/4.11 — the
   Mar-2026 expenditure tables are still in the fetch queue;
   conditions["data_vintage"] carries the split). Table id, 4.9
   welfare-cap section, and 4.11 parent line are reconstructed as
   conditions — the same labels recur across tables/sections.

Ledger routing: the 133 EFO outturn columns (2024-25 receipts /
expenditure outturn) are admin facts → returned for the Ledger staging
file, not external_scores.

calibration_relationship: forecast rows whose line matches a series
populace-UK literally consumes are reclassed consumed_as_target. The
consumed sets were read from policyengine-uk-data
targets/sources/obr.py THIS session (2026-08-02): income tax gross +
NICs classes from Table 3.4, VAT/fuel duties/CGT/SDLT from 3.9 (staged
here from the 3.8 cash-receipts summary — same head, table noted),
council tax from 4.1 (staged from 3.8), and the twelve Table 4.9 welfare
lines. Everything else stays held_out.
"""

from __future__ import annotations

import json
import re
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
    ledger_row,
    load_staged_uk,
    measure_slug,
    normalize_geography_uk,
    parse_fy,
)

_KNOWN_FIELDS = frozenset(
    {
        "source", "metric", "proposed_metric", "unit_concept",
        "proposed_unit", "normalization", "period", "time_basis",
        "conditions", "reform_hint", "calibration_relationship",
        "source_model", "source_column", "source_table", "value",
        "value_raw", "publication", "status",
    }
)

_MEASURE_CONDITIONS = {
    "geography": "geography",
    "fy": "fy",
    "fiscal_event": "fiscal_event",
    "tax_head": "tax_head",
    "spending_head": "spending_head",
    "impact_channel": "impact_channel",
    "basis": "basis",
    "costing_phase": "costing_phase",
    "sign_convention": "sign_convention",
}
_EFO_CONDITIONS = {
    "geography": "geography",
    "fy": "fy",
    "basis": "basis",
    "line_item": "line_item",
    "section": "section",
    "note": "note",
    "domain": "domain",
}

_METRICS = {
    "revenue_change": Metric.REVENUE_CHANGE,
    "benefit_cost": Metric.BENEFIT_COST,
    "exchequer_impact": Metric.EXCHEQUER_IMPACT,
    "revenue_level": Metric.REVENUE_LEVEL,
    "policy_parameter_level": Metric.POLICY_PARAMETER_LEVEL,
    "taxpayer_count": Metric.TAXPAYER_COUNT,
}

# Consumed line matching (read from policyengine-uk-data
# targets/sources/obr.py this session). Receipts heads are matched on
# revenue_level line_items in the 3.4/3.8 staged tables; welfare lines on
# 4.9 benefit_cost line_items after stripping trailing footnote digits.
_CONSUMED_RECEIPTS = {
    "Income tax (gross of tax credits)": "obr/income_tax (Table 3.4)",
    "National insurance contributions": "obr/ni (Table 3.9 cash head)",
    "Value added tax": "obr/vat (Table 3.9 cash head)",
    "Fuel duties": "obr/fuel_duties (Table 3.9 cash head)",
    "Capital gains tax": "obr/capital_gains_tax (Table 3.9 cash head)",
    "Stamp duty land tax": "obr/sdlt (Table 3.9 cash head)",
    "Council tax": "obr council-tax lines (Table 4.1)",
    "Class 1 Employee NICs": "obr NICs class parse (Table 3.4)",
    "Class 1 Employer NICs": "obr NICs class parse (Table 3.4)",
    "Class 4 and Class 2 Self employed NICs":
        "obr NICs class parse (Table 3.4)",
    "Class 2 and Class 4 Self employed NICs":
        "obr NICs class parse (Table 3.4)",
}
_CONSUMED_WELFARE = {
    # (label after footnote-stripping, 4.9 section) -> target. pe-uk-data
    # matches labels in workbook order; UC appears in BOTH sections and
    # feeds two distinct targets.
    ("Housing benefit (not on JSA)", "welfare_cap"): "obr/housing_benefit",
    (
        "Disability living allowance and personal independence payments",
        "welfare_cap",
    ): "obr/pip (combined DLA+PIP line)",
    ("Incapacity benefits", "welfare_cap"): "obr/esa",
    ("Attendance allowance", "welfare_cap"): "obr/attendance_allowance",
    ("Pension credit", "welfare_cap"): "obr/pension_credit",
    ("Carer's allowance", "welfare_cap"): "obr/carers_allowance",
    ("Statutory maternity pay", "welfare_cap"):
        "obr/statutory_maternity_pay",
    ("Winter fuel payment", "welfare_cap"): "obr/winter_fuel_allowance",
    ("Universal credit", "welfare_cap"): "obr/universal_credit_in_cap",
    ("Child benefit", "welfare_cap"): "obr/child_benefit",
    ("Universal credit", "outside_welfare_cap"):
        "obr/universal_credit_outside_cap",
    ("State pension", "outside_welfare_cap"): "obr/state_pension",
    ("Jobseeker's allowance", "outside_welfare_cap"):
        "obr/jobseekers_allowance",
}
_CONSUMED_BASIS = (
    "policyengine-uk-data targets/sources/obr.py parses this EFO series "
    "into {target} (read 2026-08-02){vintage}; agreement is discipline, "
    "not validation"
)
_WELFARE_VINTAGE_CAVEAT = (
    " — populace consumes the Mar-2026 EFO successor of this series; the "
    "staged 4.9 vintage is Nov-2025 (Mar-2026 expenditure tables pending "
    "fetch), same series one vintage earlier"
)


def _strip_footnote(label: str) -> str:
    return re.sub(r"\d+$", "", label.strip()).strip()


def _consumed_target(row: dict, section: str | None) -> str | None:
    """Target name when populace-UK consumes this EFO line, else None."""
    if row["source_model"] != "obr_efo_forecast":
        return None
    line = _strip_footnote(row["conditions"].get("line_item", ""))
    table = (row.get("source_table") or "").split(":")[0]
    metric = row.get("metric") or row.get("proposed_metric")
    if metric == "revenue_level" and table in ("3.4", "3.8"):
        return _CONSUMED_RECEIPTS.get(line)
    if metric == "benefit_cost" and table == "4.9":
        return _CONSUMED_WELFARE.get((line, section))
    return None


_EFO_VINTAGES = {
    "March 2026": "march_2026_efo",
    "November 2025": "november_2025_efo",
}


def _efo_vintage(row: dict) -> str:
    title = row["publication"].get("title", "")
    for needle, slug in _EFO_VINTAGES.items():
        if needle in title:
            return slug
    raise ValueError(f"uk_obr: unrecognized EFO vintage in {title!r}")


def _derive_49_sections(rows: list[dict]) -> dict[int, str]:
    """Reconstruct Table 4.9's welfare-cap / outside-cap sections (the
    staging dropped the marker; the same subtotal labels recur in both).
    Workbook order is preserved: the section flips after each section
    total."""
    sections: dict[int, str] = {}
    current, prev_line = "welfare_cap", None
    boundary = {
        "Total welfare cap": "outside_welfare_cap",
        "Total welfare outside the welfare cap": "total",
    }
    for i, row in enumerate(rows):
        if row.get("source_model") != "obr_efo_forecast":
            continue
        if not (row.get("source_table") or "").startswith("4.9"):
            continue
        line = row["conditions"]["line_item"]
        if line != prev_line and prev_line in boundary:
            current = boundary[prev_line]
        sections[i] = current
        prev_line = line
    return sections


_411_GROUPS = frozenset({"Children", "Working-age", "Pensioner"})


def _derive_411_parents(rows: list[dict]) -> dict[int, str]:
    """Table 4.11 nests Children/Working-age/Pensioner group rows under
    each spending category (Disability spending, DLA, PIP, totals, …);
    the staging kept only the group label, so the same label recurs under
    several parents. Workbook order is preserved: a group row's parent is
    the nearest preceding non-group line."""
    parents: dict[int, str] = {}
    parent = None
    for i, row in enumerate(rows):
        if row.get("source_model") != "obr_efo_forecast":
            continue
        if not (row.get("source_table") or "").startswith("4.11"):
            continue
        line = row["conditions"]["line_item"]
        if line in _411_GROUPS:
            if parent is None:
                raise ValueError("uk_obr: 4.11 group row before any parent")
            parents[i] = parent
        else:
            parent = line
    return parents


def _component_runs(rows: list[dict]) -> dict[int, int]:
    """The measures database scores one titled measure as several
    component series — usually one per tax/spending head, sometimes two
    under the same abbreviated head (Budget 2015 #2's non-dom measure has
    two 'Stamp duty' components). The staging preserves workbook order:
    each component is one consecutive run of increasing fiscal years, so
    a year reset inside an unchanged (event, title, head) marks the next
    component. The measure title stays the reform world (the database's
    own unit of identity); the component seq is a conditions axis.
    Returns staged-row-index -> component seq (1-based) per that key."""
    seq: dict[int, int] = {}
    runs_seen: dict[tuple, int] = {}
    prev_key, prev_start = None, None
    for i, row in enumerate(rows):
        if row["source_model"] != "hmt_scorecard_obr_database":
            continue
        c = row["conditions"]
        key = (
            c["fiscal_event"],
            row["reform_hint"],
            c.get("tax_head") or c.get("spending_head"),
        )
        start, _ = parse_fy(c["fy"])
        new_run = key != prev_key or (
            prev_start is not None and start <= prev_start
        )
        if new_run:
            runs_seen[key] = runs_seen.get(key, 0) + 1
        seq[i] = runs_seen[key]
        prev_key, prev_start = key, start
    return seq


def stage() -> tuple[list[ExternalScore], list[dict]]:
    scores: list[ExternalScore] = []
    ledger: list[dict] = []
    staged_rows = load_staged_uk("uk_obr")
    component = _component_runs(staged_rows)
    sections49 = _derive_49_sections(staged_rows)
    parents411 = _derive_411_parents(staged_rows)
    for i, row in enumerate(staged_rows):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_obr: unhandled fields {sorted(unknown)}")
        conds_in = dict(row["conditions"])
        basis = conds_in.get("basis")
        if basis == "outturn":
            derived = {}
            if i in sections49:
                derived["section"] = sections49[i]
            if i in parents411:
                derived["parent_line"] = parents411[i]
            ledger.append(
                ledger_row(
                    "uk_obr", row,
                    "OBR EFO outturn column — admin receipts/expenditure "
                    "fact (ledger routing rule, Max 2026-08-02)",
                    derived=derived or None,
                )
            )
            continue

        is_measure = row["source_model"] == "hmt_scorecard_obr_database"
        key_map = _MEASURE_CONDITIONS if is_measure else _EFO_CONDITIONS
        unknown_c = set(conds_in) - set(key_map)
        if unknown_c:
            raise ValueError(f"uk_obr: unmapped conditions {sorted(unknown_c)}")

        period, fy_norm = parse_fy(conds_in["fy"])
        geography, geo_note = normalize_geography_uk(conds_in["geography"])
        conditions = {
            key_map[k]: v
            for k, v in conds_in.items()
            if v is not None and k not in ("fy", "geography")
        }
        conditions["fy"] = fy_norm
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note
        if not is_measure:
            # EFO table id is identity-bearing: the same head appears in
            # 3.4 (accrued IT/NICs detail) and 3.8 (cash current
            # receipts) with different values. So are the reconstructed
            # 4.9 sections (the same subtotal labels recur in the
            # welfare-cap and outside-cap blocks) and the EFO vintage
            # (receipts staged from Mar-2026, expenditure from Nov-2025).
            conditions["table"] = (row["source_table"] or "").split(":")[0]
            if i in sections49:
                conditions["section"] = sections49[i]
            if i in parents411:
                conditions["parent_line"] = parents411[i]
            conditions["data_vintage"] = _efo_vintage(row)

        metric_name = row.get("metric") or row.get("proposed_metric")
        metric = _METRICS[metric_name]
        hint = row.get("reform_hint")
        if is_measure:
            if not hint:
                raise ValueError("uk_obr: measures row without reform_hint")
            reform = policy_ref(
                measure_slug(
                    "uk_obr_measure", conds_in["fiscal_event"], hint
                )
            )
            conditions["measure"] = hint
            if component[i] > 1:
                conditions["component_seq"] = str(component[i])
        elif hint and metric is Metric.REVENUE_CHANGE:
            # 3.17: latest re-estimates of previously announced personal
            # tax measures — reform worlds keyed by title at the EFO
            # re-estimate vintage.
            reform = policy_ref(
                measure_slug("uk_obr_measure", "efo_march_2026", hint)
            )
            conditions["measure"] = hint
        else:
            if hint:
                raise ValueError(
                    f"uk_obr: unexpected reform_hint on {metric_name} row"
                )
            reform = BASELINE

        unit = (
            UnitConcept.PERSONS
            if metric is Metric.TAXPAYER_COUNT
            else UnitConcept.GBP
        )
        target = _consumed_target(row, sections49.get(i))
        relationship = (
            CalibrationRelationship.CONSUMED_AS_TARGET
            if target
            else CalibrationRelationship(row["calibration_relationship"])
        )
        publication = dict(row["publication"])
        if row.get("source_table"):
            publication.setdefault("table", row["source_table"])
        if target:
            publication["calibration_basis"] = _CONSUMED_BASIS.format(
                target=target,
                vintage=(
                    _WELFARE_VINTAGE_CAVEAT
                    if conditions.get("table") == "4.9"
                    else ""
                ),
            )

        scores.append(
            ExternalScore(
                source="obr",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=reform,
                calibration_relationship=relationship,
                source_column=row.get("source_column"),
                publication=publication,
                value_kind="count" if unit is UnitConcept.PERSONS else "gbp",
                status=row.get("status", "ok"),
            )
        )
    return finish(scores, "uk_obr"), ledger


def ingest(db_path: Path) -> dict:
    scores, ledger = stage()
    measures = sum(
        1 for s in scores if s.source_model == "hmt_scorecard_obr_database"
    )
    consumed = sum(
        1
        for s in scores
        if s.calibration_relationship
        is CalibrationRelationship.CONSUMED_AS_TARGET
    )
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "obr-measures",
        "ingested",
        f"{measures} policy-measures-database claims (84 fiscal events "
        "since 1970, reform-keyed per measure title, "
        "positive_gain_to_exchequer verbatim)",
        "2026-08-02",
    )
    db.set_lane(
        "obr-welfare",
        "ingested",
        f"{n - measures} EFO Mar-2026 claims (receipts 3.4/3.8, welfare "
        f"4.9/4.11, threshold analysis 3.17-3.19); {consumed} "
        "consumed_as_target (exact pe-uk-data target lines, "
        "targets/sources/obr.py); "
        f"{len(ledger)} outturn rows routed to Ledger staging",
        "2026-08-02",
    )
    db.close()
    return {"scores": n, "ledger": len(ledger), "consumed": consumed}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
