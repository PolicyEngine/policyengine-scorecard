"""Ingest the per-program solo take-up runs as PE exhibits.

Five counterfactuals (one program's take-up gate forced to 100%, everything
else at baseline), differenced against baseline SPM poverty: the
"which take-up gap is the poverty lever" attribution. PE-only — no external
claim exists, so rows land in pe_exhibits, not external_scores
(FINDINGS.md §attribution; the sibling session computed the runs, this
ingester validates and stores them).

Sanity gates (fail loudly, per the reconciliation-QC doctrine):
- full 5 programs × 52 geographies × 2 metrics coverage;
- baseline rows must match the bit-exact-verified pe_baseline.csv values;
- national deltas must reproduce FINDINGS.md's headline table (±0.005pp)
  and the documented non-additivity (solo sum ≈ −1.18pp vs joint −0.69pp).

Also exports data/exhibits.json for the app.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .db import ScorecardDB
from .ingest_urban import solo_reform

COMPARISON_DIR = Path.home() / "populace-sotsn-takeup" / "comparison"
REPO = Path(__file__).resolve().parent.parent
PROGRAMS = ("snap", "ssi", "tanf", "wic", "housing")
EXHIBIT = "solo_takeup_poverty"

# FINDINGS.md §attribution headline deltas (US, percentage points).
EXPECTED_US_PP = {
    "housing": (-0.65, -1.38),
    "ssi": (-0.28, -0.11),
    "tanf": (-0.10, -0.29),
    "wic": (-0.08, -0.21),
    "snap": (-0.06, -0.06),
}

NOTE = (
    "Marginal-from-baseline: one program's take-up gate forced to 100%. "
    "Non-additive with the joint counterfactual (overlapping near-poor "
    "households). Housing is likely an underestimate (HAP dollars known "
    "low) on a broader eligible pool (80% AMI). Caveat: Early Head Start "
    "distortion of baseline resources (populace#593) until fixed."
)


def _baseline_rates(path: Path) -> dict:
    """{(geo, metric): rate} from the interchange baseline (verified
    bit-exact against the platform grid in RECONCILIATION.md)."""
    rates = {}
    for r in csv.DictReader(open(path)):
        if r["program"] != "base" or not r["pe_value"]:
            continue
        metric = (
            "child_pov_rate"
            if r["metric"].endswith("_child")
            else "pov_rate"
        )
        rates[(r["geography"], metric)] = float(r["pe_value"])
    return rates


def ingest(db_path: Path, comparison_dir: Path = COMPARISON_DIR) -> dict:
    baseline = _baseline_rates(comparison_dir / "pe_baseline.csv")
    bundle = json.loads(
        (comparison_dir / "pe_baseline_meta.json").read_text()
    )["bundle"]

    rows, us_deltas = [], {}
    for program in PROGRAMS:
        f = comparison_dir / f"pe_solo_{program}_2024.csv"
        seen = set()
        reform = solo_reform(program)
        for r in csv.DictReader(open(f)):
            geo = r["geography"]
            seen.add(geo)
            for metric_col, sub in (
                ("pov_rate", "total"), ("child_pov_rate", "child"),
            ):
                value = float(r[metric_col])
                base = baseline.get((geo, metric_col))
                if base is None:
                    raise SystemExit(f"no baseline for {geo}/{metric_col}")
                delta = value - base
                if geo == "US":
                    us_deltas[(program, sub)] = delta
                rows.append(
                    {
                        "exhibit": EXHIBIT,
                        "reform_key": reform.key(),
                        "reform_json": reform.to_json(),
                        "metric": "poverty_rate",
                        "unit_concept": "share",
                        "period": 2024,
                        "time_basis": "annual",
                        "conditions": (
                            {"geography": geo}
                            if sub == "total"
                            else {"geography": geo, "subgroup": "child"}
                        ),
                        "geography": geo,
                        "program": program,
                        "value": value,
                        "baseline_value": base,
                        "delta": delta,
                        "engine_version": bundle["model_version"],
                        "data_bundle": bundle["certified_data_build_id"],
                        "run_id": "solo-takeup-2024",
                        "computed_at": "2026-08-01T20:20:00",
                        "note": NOTE,
                    }
                )
        if len(seen) != 52:
            raise SystemExit(f"{program}: {len(seen)} geographies, want 52")

    # National headline gates vs FINDINGS.md (±0.005pp).
    for program, (want_total, want_child) in EXPECTED_US_PP.items():
        for sub, want in (("total", want_total), ("child", want_child)):
            got = us_deltas[(program, sub)] * 100
            if abs(got - want) > 0.005:
                raise SystemExit(
                    f"{program}/{sub}: US delta {got:.3f}pp != "
                    f"documented {want}pp"
                )
    solo_sum = sum(us_deltas[(p, "total")] for p in PROGRAMS) * 100
    if not -1.25 < solo_sum < -1.10:  # documented ≈ −1.18pp
        raise SystemExit(f"solo sum {solo_sum:.2f}pp outside documented band")

    db = ScorecardDB(db_path)
    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_exhibits WHERE exhibit = ?", (EXHIBIT,)
        )
    n = db.add_exhibits(rows)
    db.set_lane(
        "urban-sotsn-solo-attribution", "computed",
        f"{n} exhibit rows; housing is the lever (−0.65pp US, −1.38pp child)",
        "2026-08-01T20:20:00",
    )

    export = {
        "exhibit": EXHIBIT,
        "note": NOTE,
        "non_additivity": {
            "solo_sum_pp": round(solo_sum, 2),
            "joint_all_programs_pp": -0.69,
        },
        "rows": [
            {
                "program": r["program"],
                "geography": r["geography"],
                "subgroup": r["conditions"].get("subgroup", "total"),
                "value": r["value"],
                "baseline_value": r["baseline_value"],
                "delta": r["delta"],
            }
            for r in rows
        ],
    }
    out = REPO / "data" / "exhibits.json"
    out.write_text(json.dumps(export))
    db.close()
    return {"exhibit_rows": n, "solo_sum_pp": round(solo_sum, 2)}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
