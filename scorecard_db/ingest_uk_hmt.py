"""Ingest the HMT staged claims (2026-08-02 UK harvest).

- **Scorecard costings** (1,218, hmt_costing_obr_certified): every
  measure line of AB2024 Table 5.1, Budget 2025 Table 4.1 and SS2025
  Table 3.1 — OBR-certified exchequer impacts. Each measure title is a
  policy_ref world (uk_hmt:<event>:<title-hash>) scored against current
  law at announcement; row_type (measure|total|of_which), scorecard_line
  and Tax/Spend head ride conditions verbatim. Metric is
  exchequer_impact, NOT revenue_change — the footnote classifies lines
  by LARGEST impact, so Tax/Spend heads mix (deliberate mapping,
  COLLATION UK worklist item 1). Suppressed cells ("*", negligible)
  stage as status=suppressed.
- **Distributional analysis** (150, hmt_distributional_analysis_igotm):
  Annex Table 2.C median gross income by decile × household composition
  — baseline level claims with the full IGOTM income-concept string
  (equivalised, BHC, modified-OECD) verbatim in conditions.
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
    ledger_row,
    load_staged_uk,
    measure_slug,
    normalize_geography_uk,
    parse_fy,
)

_KNOWN_FIELDS = frozenset(
    {
        "source",
        "proposed_metric",
        "proposed_unit",
        "value",
        "value_raw",
        "conversion",
        "metric_note",
        "parse_confidence",
        "sign_note",
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
        "name_note",
        "suppression_note",
    }
)

_CONDITION_KEYS = {
    "geography": "geography",
    "fiscal_event": "fiscal_event",
    "fiscal_year": "fy",
    "row_type": "row_type",
    "section": "section",
    "scorecard_line": "scorecard_line",
    "head": "head",
    "decile": "decile",
    "household_composition": "household_composition",
    "income_concept": "income_concept",
    "decile_definition": "decile_definition",
    "equivalisation": "equivalisation",
}

_METRICS = {
    "exchequer_impact": Metric.EXCHEQUER_IMPACT,
    "median_gross_income": Metric.MEDIAN_INCOME,
}


def stage() -> tuple[list[ExternalScore], list[dict]]:
    scores: list[ExternalScore] = []
    ledger: list[dict] = []
    for row in load_staged_uk("uk_hmt"):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_hmt: unhandled fields {sorted(unknown)}")
        if row["parse_confidence"] != "high":
            raise ValueError(
                f"uk_hmt: non-high parse confidence needs review: "
                f"{row['parse_confidence']!r}"
            )
        conds_in = dict(row["conditions"])
        unknown_c = set(conds_in) - set(_CONDITION_KEYS)
        if unknown_c:
            raise ValueError(f"uk_hmt: unmapped conditions {sorted(unknown_c)}")

        geography, geo_note = normalize_geography_uk(conds_in.pop("geography"))
        period, fy_norm = parse_fy(conds_in.pop("fiscal_year"))
        conditions = {
            _CONDITION_KEYS[k]: v for k, v in conds_in.items() if v is not None
        }
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note
        conditions["fy"] = fy_norm

        metric = _METRICS[row["proposed_metric"]]
        is_costing = row["source_model"] == "hmt_costing_obr_certified"
        if is_costing:
            hint = row["reform_hint"]
            if not hint:
                raise ValueError("uk_hmt: costing row without reform_hint")
            if "reform" in row:
                raise ValueError("uk_hmt: costing row carries reform field")
            reform = policy_ref(measure_slug("uk_hmt", conds_in["fiscal_event"], hint))
            conditions["measure"] = hint
            unit = UnitConcept.GBP
            value_kind = "gbp"
        else:
            if row.get("reform", {"framework": "baseline"}) != {
                "framework": "baseline"
            }:
                raise ValueError(f"uk_hmt: unexpected reform {row['reform']}")
            reform = BASELINE
            unit = UnitConcept.GBP_PER_HOUSEHOLD
            value_kind = "gbp"

        publication = dict(row["publication"])
        if row.get("source_table"):
            publication.setdefault("table", row["source_table"])
        for note in ("sign_note", "metric_note", "name_note", "suppression_note"):
            if row.get(note):
                publication[note] = row[note]

        scores.append(
            ExternalScore(
                source="hmt",
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
                value_kind=value_kind,
                status=row.get("status", "ok"),
            )
        )
    return finish(scores, "uk_hmt"), ledger


def ingest(db_path: Path) -> dict:
    scores, ledger = stage()
    costings = sum(1 for s in scores if s.source_model == "hmt_costing_obr_certified")
    suppressed = sum(1 for s in scores if s.status == "suppressed")
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "hmt-costings",
        "ingested",
        f"{costings} OBR-certified scorecard costings (AB2024 5.1 / "
        "B2025 4.1 / SS2025 3.1; exchequer_impact — Tax/Spend heads mix "
        f"by design; {suppressed} suppressed cells verbatim) + "
        f"{n - costings} IGOTM decile medians (annex 2.C); B2025 "
        "two-child measure title embeds the government's 450k-children "
        "poverty claim — pentagon leg",
        "2026-08-02",
    )
    db.close()
    return {"scores": n, "ledger": len(ledger), "costings": costings}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
