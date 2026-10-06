"""Family ``cbo_free_joins`` (9 rows, original run_id campaign-20260802-us-joins).

Baseline-only CY2026 aggregates joined to CBO baseline-projection rows.
One simulation (current law, as-served take-up), period 2026.

Constructions, from each original row's ``pe_construction`` text:

* ``pass2 aggregate snap total_usd CY2026`` -> ``snap`` (SPM unit) summed,
  2026.
* ``year-grid snap part_pop US CY2026`` ("PE annual-ever persons in units
  with benefit>0") -> persons whose SPM unit has ``snap > 0`` in 2026
  (``calculate('snap', 2026, map_to='person') > 0``), weighted count.
* ``pass2 snap dollars / year-grid part_pop / 12`` -> the two above, /12.
* ``pass2 aggregate ssi total_usd CY2026`` -> ``ssi`` summed, 2026.
* ``year-grid ssi part_pop US CY2026`` -> persons with ``ssi > 0`` within the
  year-grid SSI universe. The year-grid (the Urban SotSN counterpart grid,
  ``pipeline/compute_counterparts.py``) measures SSI on Urban's adult
  concept: ``person_program('ssi', ..., universe=(age >= 18))``. So the
  count is adults 18+ with ``ssi > 0``. (The all-ages count is computed
  too and recorded in the run metadata.)
* ``pass2 ssi dollars / year-grid part_pop / 12`` -> the two above, /12.
* ``pass2 aggregate tanf total_usd CY2026`` -> ``tanf`` summed, 2026.
* ``eitc+refundable_ctc CY2026 (composite ...)`` -> ``eitc`` summed plus
  ``refundable_ctc`` summed, 2026 (two CBO rows, same value).
"""

from __future__ import annotations

import numpy as np
from common import emit_row, load_original, now_utc, provenance, run_job

STEM = "cbo_free_joins"
YEAR = 2026


def measures(sim) -> dict:
    v = {}
    v["snap_total"] = sim.calculate("snap", YEAR).sum()
    v["snap_part_pop"] = (sim.calculate("snap", YEAR, map_to="person") > 0).sum()
    ssi = sim.calculate("ssi", YEAR)
    age = np.asarray(sim.calculate("age", YEAR).values, dtype=float)
    part = ssi > 0
    v["ssi_total"] = ssi.sum()
    v["ssi_part_pop_adults"] = part[age >= 18].sum()
    v["ssi_part_pop_all_ages"] = part.sum()
    v["tanf_total"] = sim.calculate("tanf", YEAR).sum()
    v["eitc_total"] = sim.calculate("eitc", YEAR).sum()
    v["refundable_ctc_total"] = sim.calculate("refundable_ctc", YEAR).sum()
    return v


def _value(row: dict, m: dict) -> float:
    d = row["external_claim_match"]
    prog = d["conditions"]["program"]
    metric = d["metric"]
    if prog == "snap":
        return {
            "benefit_cost": m["snap_total"],
            "participant_count": m["snap_part_pop"],
            "average_monthly_benefit": m["snap_total"] / m["snap_part_pop"] / 12,
        }[metric]
    if prog == "ssi":
        return {
            "benefit_cost": m["ssi_total"],
            "participant_count": m["ssi_part_pop_adults"],
            "average_monthly_benefit": m["ssi_total"] / m["ssi_part_pop_adults"] / 12,
        }[metric]
    if prog == "tanf" and metric == "benefit_cost":
        return m["tanf_total"]
    if prog == "eitc_ctc_other_credits" and metric == "benefit_cost":
        return m["eitc_total"] + m["refundable_ctc_total"]
    raise KeyError(f"no construction for {d}")


def run() -> tuple[list[dict], dict]:
    originals = load_original(STEM)
    res = run_job(
        {"label": "cbo baseline CY2026", "measure": "cbo_free_joins:measures"}
    )
    prov = provenance([res])
    at = now_utc()
    rows = [emit_row(o, _value(o, res["values"]), prov, at) for o in originals]
    return rows, {"provenance": prov, "jobs": [res]}
