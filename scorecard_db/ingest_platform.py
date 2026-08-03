"""Ingest the platform pipeline's full comparison grid into the database.

data/comparison.json (pipeline/build_comparison.py) carries the complete
subgroup × state PE grid — ~9.3k computed counterparts with the real status
taxonomy (comparable/constructed/concept_mismatch), machine-readable
constructions, and annotation ids — versus the interchange's 678 totals-only
rows. This module:

1. Reconstructs each row's claim_id EXACTLY as ingest_urban built it
   (conditions vocabulary must match byte-for-byte) and fails loudly on
   computed rows that do not resolve to an existing claim.
2. Adds PEResults with the platform statuses, constructions, and annotations.
3. Repairs claims' source_column provenance (the tidy CSV lost it).
4. Seeds the lanes table from data/lanes.json (the mission-control feed).

2026 projections are NOT ingested as pe_results: a claim describes one
period; a 2026 PE value attached to a 2023 claim would shadow the 2024
result in the latest-result view. Projections stay in the app layer until
projection claims get their own period-keyed rows.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .ingest_urban import FULLPART_REFORM, POP_UNIT, UNITS_UNIT
from .models import (
    BASELINE,
    CURRENT_LAW_DESCRIPTOR,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
    baseline_key,
)

# Platform-grid runs execute on the certified current-law world (fullpart
# rows force take-up flags on that same world) — record it per issue #13.
_CURRENT_LAW_KEY = baseline_key(CURRENT_LAW_DESCRIPTOR)

REPO = Path(__file__).resolve().parent.parent

# platform metric vocabulary -> (tidy program override, Metric)
_POVERTY_METRICS = {
    "poverty_rate": ("base", Metric.POVERTY_RATE),
    "poverty_rate_fullpart": ("fullpart", Metric.POVERTY_RATE),
    "poverty_rate_relative_change_fullpart": (
        "fullpart", Metric.POVERTY_RATE_CHANGE,
    ),
    "poverty_count_change_fullpart": (
        "fullpart", Metric.POVERTY_COUNT_CHANGE,
    ),
}
_PROGRAM_METRICS = {
    "eligible_count": Metric.ELIGIBLE_COUNT,
    "eligibility_rate": Metric.ELIGIBILITY_RATE,
    "participation_rate": Metric.PARTICIPATION_RATE,
    "participation_gap_count": Metric.PARTICIPATION_GAP_COUNT,
}
_POP_CONCEPTS = {
    "persons", "adults_18plus", "children_0thr4", "children_under_13",
    "children",
}


def _probe(row) -> ExternalScore | None:
    """Rebuild the ExternalScore identity for a platform row (value-free)."""
    program = row["program"]
    metric_name = row["metric"]
    if program == "spm_poverty":
        tidy_program, metric = _POVERTY_METRICS[metric_name]
        uc = UnitConcept.SHARE
        if metric == Metric.POVERTY_COUNT_CHANGE:
            uc = UnitConcept.PERSONS
        conditions = {"geography": row["geography"]}
        if row["subgroup"] != "total":
            conditions["subgroup"] = row["subgroup"]
        reform = FULLPART_REFORM if tidy_program == "fullpart" else BASELINE
        return ExternalScore(
            source="urban_sotsn",
            metric=metric,
            unit_concept=uc,
            period=2023,
            time_basis=TimeBasis.AVERAGE_MONTH,
            value=0,
            conditions=conditions,
            reform=reform,
        )

    metric = _PROGRAM_METRICS.get(metric_name)
    if metric is None:
        return None
    is_pop = row["unit_concept"] in _POP_CONCEPTS
    if metric in (Metric.ELIGIBILITY_RATE, Metric.PARTICIPATION_RATE):
        uc = UnitConcept.SHARE
    elif is_pop:
        uc = POP_UNIT.get(program, UnitConcept.PERSONS)
    else:
        uc = UNITS_UNIT.get(program)
        if uc is None:
            return None
    conditions = {"geography": row["geography"], "program": program}
    if metric in (Metric.ELIGIBILITY_RATE, Metric.PARTICIPATION_RATE):
        conditions["rate_unit"] = "pop" if is_pop else "units"
    sub = row["subgroup"]
    if row["variant"]:
        sub = f"{sub}_{row['variant']}"
    if sub != "total":
        conditions["subgroup"] = sub
    return ExternalScore(
        source="urban_sotsn",
        metric=metric,
        unit_concept=uc,
        period=2023,
        time_basis=TimeBasis.AVERAGE_MONTH,
        value=0,
        conditions=conditions,
        reform=BASELINE,
    )


def ingest(db_path: Path, comparison_json: Path | None = None,
           lanes_json: Path | None = None) -> dict:
    comparison_json = comparison_json or REPO / "data" / "comparison.json"
    lanes_json = lanes_json or REPO / "data" / "lanes.json"
    comp = json.loads(comparison_json.read_text())
    db = ScorecardDB(db_path)

    known = {
        r[0]
        for r in db.conn.execute("SELECT claim_id FROM external_scores")
    }
    bundle = comp.get("pe_bundle", {})
    results, unmatched, col_fixes = [], [], []
    for row in comp["rows"]:
        probe = _probe(row)
        if probe is None:
            continue
        cid = probe.claim_id()
        if cid not in known:
            if row.get("pe_value") is not None:
                unmatched.append(
                    (row["program"], row["metric"], row["geography"],
                     row["subgroup"], row["variant"])
                )
            continue
        if row.get("source_column"):
            col_fixes.append((row["source_column"], cid))
        if row.get("pe_value") is None:
            continue
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=row["pe_value"],
                status=ComparisonStatus(row["status"]),
                engine_version=bundle.get("model_version", "unknown"),
                data_bundle=bundle.get("certified_data_build_id", "unknown"),
                pe_construction=row.get("pe_construction") or "",
                run_id="platform-grid-2024",
                computed_at=f"{comp.get('built', '')}T12:00:00",
                annotations=row.get("annotations", []),
                baseline_key=_CURRENT_LAW_KEY,
            )
        )
    if unmatched:
        sample = unmatched[:8]
        raise SystemExit(
            f"{len(unmatched)} computed platform rows failed to resolve to "
            f"claims — conditions vocabulary drift. Sample: {sample}"
        )
    n = db.add_results(results)
    with db.conn:
        db.conn.executemany(
            "UPDATE external_scores SET source_column = ?"
            " WHERE claim_id = ? AND source_column IS NULL",
            col_fixes,
        )

    n_lanes = 0
    if lanes_json.exists():
        feed = json.loads(lanes_json.read_text())
        for lane in feed.get("lanes", []):
            db.set_lane(
                lane["id"], lane["stage"], lane.get("note", ""),
                lane.get("updated", ""),
            )
            n_lanes += 1
    cov = db.coverage()
    db.close()
    return {
        "results_added": n,
        "source_columns_repaired": len(col_fixes),
        "lanes_seeded": n_lanes,
        **cov,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
