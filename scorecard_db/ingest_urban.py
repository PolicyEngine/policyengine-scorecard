"""Ingest the Urban SotSN comparison files into the Scorecard database.

Demonstrates the reform-keyed design end to end:
- `base` block rows -> BASELINE reform
- `fullpart` rows   -> the all-programs 100%-take-up reform
- per-program solo counterfactuals -> per-program take-up reforms

PE results carry engine/bundle provenance from the comparison metadata.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .db import ScorecardDB
from .models import (
    BASELINE,
    CalibrationRelationship,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

COMPARISON_DIR = Path.home() / "populace-sotsn-takeup" / "comparison"

PUBLICATION = {
    "title": "State of the Safety Net data tool",
    "url": (
        "https://apps.urban.org/features/"
        "state-of-the-safety-net-data-tool/"
    ),
    "date": "2026-03-03",
    "vintage": "2023",
}

# All take-up gates forced True — the published "full participation" world.
FULLPART_REFORM = ReformRef(
    framework="policyengine_us",
    reform={"gov.simulation.take_up.all_flags": {"2024-01-01.2026-12-31": True}},
)


def solo_reform(program: str) -> ReformRef:
    return ReformRef(
        framework="policyengine_us",
        reform={
            f"gov.simulation.take_up.{program}": {
                "2024-01-01.2026-12-31": True
            }
        },
    )


# Urban's count metrics carry the unit inside the metric name (elig_pop /
# elig_units); rate and gap rows carry it in the unit column. Resolve the
# published unit concept per program.
POP_UNIT = {
    "snap": UnitConcept.PERSONS,
    "ssi": UnitConcept.ADULTS_18PLUS,
    "tanf": UnitConcept.PERSONS,
    "wic": UnitConcept.CHILDREN_0THR4,
    "ccdf": UnitConcept.PERSONS,
    "base": UnitConcept.PERSONS,
    "fullpart": UnitConcept.PERSONS,
}
UNITS_UNIT = {
    "eitc": UnitConcept.TAX_UNITS,
    "ctc_refund": UnitConcept.TAX_UNITS,
    "housing": UnitConcept.HOUSEHOLDS,
    "liheap": UnitConcept.HOUSEHOLDS,
    "tanf": UnitConcept.FAMILIES,
}


def _count_unit(program: str, unit_col: str) -> UnitConcept:
    if unit_col == "units" or program in (
        "eitc",
        "ctc_refund",
        "housing",
        "liheap",
    ):
        return UNITS_UNIT[program]
    return POP_UNIT[program]


def _metric_for(metric: str, unit: str, program: str):
    unit = unit or ""
    if metric == "elig_pop":
        return Metric.ELIGIBLE_COUNT, POP_UNIT[program]
    if metric in ("elig_units", "elig_hhs"):
        return Metric.ELIGIBLE_COUNT, UNITS_UNIT[program]
    if metric == "elig_rate":
        return Metric.ELIGIBILITY_RATE, UnitConcept.SHARE
    if metric == "part_rate":
        return Metric.PARTICIPATION_RATE, UnitConcept.SHARE
    if metric == "part_gap":
        return Metric.PARTICIPATION_GAP_COUNT, _count_unit(program, unit)
    if metric == "spm_pov_rate_100":
        return Metric.POVERTY_RATE, UnitConcept.SHARE
    if metric == "spm_pov_rate_change_100":
        return Metric.POVERTY_RATE_CHANGE, UnitConcept.SHARE
    if metric == "spm_pov_num_change_100":
        return Metric.POVERTY_COUNT_CHANGE, UnitConcept.PERSONS
    raise ValueError(f"unmapped urban metric: {metric}/{unit}")  # fail loud


def urban_scores(tidy_csv: Path) -> list[ExternalScore]:
    scores = []
    for r in csv.DictReader(open(tidy_csv)):
        program = r["program"]
        metric, uc = _metric_for(r["metric"], r["unit"], program)
        reform = FULLPART_REFORM if program == "fullpart" else BASELINE
        conditions = {"geography": r["geography"]}
        if program not in ("base", "fullpart"):
            conditions["program"] = program
        if r["metric"].endswith("_rate") and (r.get("unit") or ""):
            conditions["rate_unit"] = r["unit"]
        if r["breakdown"] not in ("total", ""):
            conditions["subgroup"] = r["breakdown"]
        if program == "fullpart" and r["breakdown"] == "child":
            conditions["subgroup"] = "child"
        suppressed = r["value"] in ("", "None")
        scores.append(
            ExternalScore(
                source="urban_sotsn",
                source_model="attis",
                metric=metric,
                unit_concept=uc,
                period=int(r["year"]),
                time_basis=TimeBasis.AVERAGE_MONTH,
                value=None if suppressed else float(r["value"]),
                conditions=conditions,
                reform=reform,
                calibration_relationship=CalibrationRelationship.HELD_OUT,
                source_column=r.get("raw") or None,
                publication=PUBLICATION,
                value_kind=r["value_kind"] if not suppressed else "count",
                status="suppressed" if suppressed else "ok",
            )
        )
    return scores


def pe_results_from_comparison(
    comparison_csv: Path, scores_by_key: dict, meta: dict
) -> list[PEResult]:
    results = []
    for r in csv.DictReader(open(comparison_csv)):
        if r.get("pe_value") in ("", None):
            continue
        program = r["program"]
        try:
            metric, uc = _metric_for(r["metric"], r["unit"], program)
        except (ValueError, KeyError):
            continue
        reform = FULLPART_REFORM if program == "fullpart" else BASELINE
        conditions = {"geography": r["geography"]}
        if program not in ("base", "fullpart"):
            conditions["program"] = program
        if r["metric"].endswith("_rate") and (r.get("unit") or ""):
            conditions["rate_unit"] = r["unit"]
        probe = ExternalScore(
            source="urban_sotsn",
            metric=metric,
            unit_concept=uc,
            period=2023,
            time_basis=TimeBasis.AVERAGE_MONTH,
            value=0,
            conditions=conditions,
            reform=reform,
        )
        cid = probe.claim_id()
        if cid not in scores_by_key:
            continue
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=float(r["pe_value"]),
                status=ComparisonStatus.CONSTRUCTED
                if r.get("concept_note")
                else ComparisonStatus.COMPARABLE,
                engine_version=meta["engine_version"],
                data_bundle=meta["data_bundle"],
                pe_construction=r.get("concept_note", ""),
                run_id=meta.get("run_id", ""),
                computed_at=meta.get("computed_at", ""),
            )
        )
    return results


def ingest(db_path: Path, comparison_dir: Path = COMPARISON_DIR) -> dict:
    db = ScorecardDB(db_path)
    scores = urban_scores(comparison_dir / "urban_tidy.csv")
    n_scores = db.upsert_scores(scores)
    scores_by_key = {s.claim_id(): s for s in scores}

    meta_file = comparison_dir / "pe_baseline_meta.json"
    bundle = json.loads(meta_file.read_text())["bundle"]
    meta = {
        "engine_version": bundle["model_version"],
        "data_bundle": bundle["certified_data_build_id"],
        "run_id": "sotsn-first-cut",
        "computed_at": "2026-08-01T00:00:00",
    }
    results = pe_results_from_comparison(
        comparison_dir / "comparison.csv", scores_by_key, meta
    )
    n_results = db.add_results(results)
    db.set_lane(
        "urban_sotsn/safety-net", "computed",
        f"{n_results} PE results over {n_scores} claims",
        meta["computed_at"],
    )
    cov = db.coverage()
    db.close()
    return {"scores": n_scores, "results": n_results, **cov}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
