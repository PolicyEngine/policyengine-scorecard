"""Ingest the HMRC staged claims (2026-08-02 UK harvest).

Ledger routing does the heavy lifting here: HMRC's outturn statistics —
SPI outturn tables, Child Benefit / tax credits / CGT / self-assessment
admin statistics, including provisional cells — are admin facts and go
to the Ledger staging file (1,855 rows). What enters external_scores is
HMRC-the-model speaking (987 rows):

- **Ready reckoner** (225): "Direct effects of illustrative tax changes"
  — each line is a policy world (policy_ref uk_hmrc_rr:<slug>) at
  FY 2026-27/2027-28/2028-29, behavioural per HMRC's methodology notes,
  sign per bulletin note 33 (verbatim in conditions/publication). These
  are the claims the campaign's reckoner runs join to (reform_hint is
  the join key, slugified identically on both sides).
- **SPI-based projections** (762): taxpayer counts, liabilities,
  income aggregates and average tax by band/age/sex, projected years.
  calibration: seed_source — policyengine-uk-data targets/sources/
  hmrc_spi.py consumes SPI 3.6/3.7 (2023-24) and
  utils/incomes_projection.py uprates from that same base (read
  2026-08-02), so PE's income distribution and HMRC's projections share
  the SPI seed; agreement is same-seed, not validation. Whole-population
  liability totals are additionally the same quantity class as the
  consumed obr/income_tax receipts target → consumed_as_target.
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
    normalize_geography_uk,
    parse_fy,
    slugify,
    uk_value_kind,
)

_KNOWN_FIELDS = frozenset(
    {
        "source", "metric", "proposed_metric", "unit_concept",
        "proposed_unit", "value", "value_raw", "value_kind", "period",
        "time_basis", "conditions", "reform", "reform_hint",
        "sign_convention", "unit_note", "row_note",
        "calibration_relationship", "source_model", "source_column",
        "publication", "status",
    }
)

_CONDITION_KEYS = {
    "geography": "geography",
    "fy": "fy",
    "basis": "basis",
    "tax": "tax",
    "band": "band",
    "income_range_lower": "income_range_lower",
    "tax_section": "tax_section",
    "direction_semantics": "direction_semantics",
    "age_group": "age_group",
    "sex": "sex",
}

_METRICS = {
    "revenue_change": Metric.REVENUE_CHANGE,
    "taxpayer_count": Metric.TAXPAYER_COUNT,
    "tax_liability": Metric.TAX_LIABILITY,
    "income_aggregate": Metric.INCOME_AGGREGATE,
    "average_tax_rate": Metric.AVERAGE_TAX_RATE,
    "average_tax_amount": Metric.AVERAGE_TAX_AMOUNT,
}

_SPI_SEED_BASIS = (
    "seed_source: policyengine-uk-data targets/sources/hmrc_spi.py "
    "consumes SPI Tables 3.6/3.7 (tax year 2023-24) and "
    "utils/incomes_projection.py uprates future years from the same "
    "parsed band table (read 2026-08-02) — PE's income distribution and "
    "HMRC's projection share the SPI seed"
)
_LIABILITY_TOTAL_BASIS = (
    "consumed_as_target: whole-population income-tax liability is the "
    "same quantity class as the obr/income_tax receipts forecast "
    "populace-UK consumes (targets/sources/obr.py, read 2026-08-02); "
    "band detail below the total stays seed_source (SPI-seeded)"
)
_TOTAL_BAND_MARKERS = frozenset({"all", "total", "all taxpayers"})


def stage() -> tuple[list[ExternalScore], list[dict]]:
    scores: list[ExternalScore] = []
    ledger: list[dict] = []
    for row in load_staged_uk("uk_hmrc"):
        unknown = set(row) - _KNOWN_FIELDS
        if unknown:
            raise ValueError(f"uk_hmrc: unhandled fields {sorted(unknown)}")
        basis = row["conditions"].get("basis")
        if basis in ("outturn", "provisional"):
            ledger.append(
                ledger_row(
                    "uk_hmrc", row,
                    f"HMRC {row['source_model']} {basis} statistics — "
                    "admin fact (ledger routing rule, Max 2026-08-02)",
                )
            )
            continue
        if basis != "projected":
            raise ValueError(f"uk_hmrc: unexpected basis {basis!r}")
        if row["reform"] != {"framework": "baseline"}:
            raise ValueError(f"uk_hmrc: unexpected reform {row['reform']}")

        conds_in = dict(row["conditions"])
        unknown_c = set(conds_in) - set(_CONDITION_KEYS)
        if unknown_c:
            raise ValueError(
                f"uk_hmrc: unmapped conditions {sorted(unknown_c)}"
            )
        geography, geo_note = normalize_geography_uk(conds_in.pop("geography"))
        period, fy_norm = parse_fy(conds_in.pop("fy"))
        conditions = {
            _CONDITION_KEYS[k]: v
            for k, v in conds_in.items()
            if v is not None
        }
        conditions["geography"] = geography
        if geo_note:
            conditions["geography_note"] = geo_note
        conditions["fy"] = fy_norm

        metric_name = row.get("metric") or row["proposed_metric"]
        metric = _METRICS[metric_name]
        is_rr = row["source_model"] == "hmrc"
        if is_rr:
            if not row.get("reform_hint"):
                raise ValueError("uk_hmrc: ready-reckoner row without hint")
            reform = policy_ref(f"uk_hmrc_rr:{slugify(row['reform_hint'])}")
            conditions["measure"] = row["reform_hint"]
        else:
            if row.get("reform_hint"):
                raise ValueError("uk_hmrc: unexpected reform_hint")
            reform = BASELINE

        if metric is Metric.TAXPAYER_COUNT:
            unit = UnitConcept.PERSONS
        elif metric is Metric.AVERAGE_TAX_RATE:
            unit = UnitConcept.SHARE
        elif metric is Metric.AVERAGE_TAX_AMOUNT:
            unit = UnitConcept.GBP_PER_PERSON
        else:
            unit = UnitConcept.GBP

        relationship = CalibrationRelationship(row["calibration_relationship"])
        publication = dict(row["publication"])
        for note in ("sign_convention", "unit_note", "row_note"):
            if row.get(note):
                publication[note] = row[note]
        if row["source_model"] == "hmrc_spi":
            band = (conditions.get("band") or "").lower()
            is_total = band in _TOTAL_BAND_MARKERS and not (
                conditions.get("age_group") or conditions.get("sex")
            )
            if metric is Metric.TAX_LIABILITY and is_total:
                relationship = CalibrationRelationship.CONSUMED_AS_TARGET
                publication["calibration_basis"] = _LIABILITY_TOTAL_BASIS
            else:
                relationship = CalibrationRelationship.SEED_SOURCE
                publication["calibration_basis"] = _SPI_SEED_BASIS

        scores.append(
            ExternalScore(
                source="hmrc",
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
                value_kind=uk_value_kind(row.get("value_kind"), unit.value),
                status=row.get("status", "ok"),
            )
        )
    return finish(scores, "uk_hmrc"), ledger


def ingest(db_path: Path) -> dict:
    scores, ledger = stage()
    rr = sum(1 for s in scores if s.source_model == "hmrc")
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
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "hmrc-personal-tax",
        "ingested",
        f"{rr} ready-reckoner claims (policy worlds per line, FY2026-27+, "
        "behavioural per HMRC notes — the campaign reckoner join surface) "
        f"+ {n - rr} SPI-based projections ({seeded} seed_source via the "
        f"shared SPI 2023-24 base, {consumed} whole-population liability "
        "totals consumed-class); "
        f"{len(ledger)} outturn/provisional admin rows routed to Ledger "
        "staging",
        "2026-08-02",
    )
    db.close()
    return {
        "scores": n,
        "ledger": len(ledger),
        "ready_reckoner": rr,
        "consumed": consumed,
        "seed_source": seeded,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
