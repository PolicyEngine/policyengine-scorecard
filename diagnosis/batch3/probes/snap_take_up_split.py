"""Probe for batch-3 item F3 (Iowa/Wisconsin SNAP).

One world per invocation (memory): `federal` forces is_tanf_non_cash_eligible
False for every month of 2024 (the fns_snap_rates construction); `baseline`
is the as-served world. Per State, average-month weighted persons (not
is_snap_excluded_member) in eligible SPM units, split by the populace anchor
(spm_unit_snap > 0, the reported ASEC subsidy) and by the take-up flag.

Usage: .venv-pe/bin/python diagnosis/batch3/probes/snap_take_up_split.py <federal|baseline> <out.json>
"""

import json
import sys

import numpy as np

YEAR = 2024
MONTHS = [f"{YEAR}-{m:02d}" for m in range(1, 13)]


def main(world: str, out: str) -> None:
    import policyengine as pe

    sim = pe.us.managed_microsimulation()
    bundle = {k: str(v) for k, v in getattr(sim, "policyengine_bundle", {}).items()}
    if world == "federal":
        var = sim.tax_benefit_system.variables["is_tanf_non_cash_eligible"]
        n = sim.populations[var.entity.key].count
        for m in MONTHS:
            sim.set_input("is_tanf_non_cash_eligible", m, np.zeros(n, dtype=bool))
    state = np.asarray(
        sim.calculate("state_code_str", YEAR, map_to="person").values
    ).astype(str)
    ones = sim.calculate("age", YEAR) >= -1
    flag = (
        np.asarray(
            sim.calculate("takes_up_snap_if_eligible", YEAR, map_to="person").values
        )
        > 0
    )
    anchor = (
        np.asarray(sim.calculate("spm_unit_snap", YEAR, map_to="person").values) > 0
    )
    unit_anchor = np.asarray(sim.calculate("spm_unit_snap", YEAR).values) > 0
    acc = {}
    for m in MONTHS:
        member = ~np.asarray(sim.calculate("is_snap_excluded_member", m).values).astype(
            bool
        )
        elig = (
            np.asarray(sim.calculate("is_snap_eligible", m, map_to="person").values) > 0
        )
        base = elig & member
        for s in sorted(set(state)) + ["US"]:
            g = np.ones(len(state), bool) if s == "US" else state == s
            cells = {
                "eligible": base & g,
                "eligible_anchored": base & anchor & g,
                "eligible_flagged": base & flag & g,
                "eligible_unanchored_flagged": base & ~anchor & flag & g,
                "anchored_not_flagged": base & anchor & ~flag & g,
            }
            for k, mask in cells.items():
                acc.setdefault(s, {}).setdefault(k, 0.0)
                acc[s][k] += float(ones[mask].sum()) / len(MONTHS)
    json.dump(
        {
            "world": world,
            "bundle": bundle,
            "units_anchored_share": float(unit_anchor.mean()),
            "states": acc,
        },
        open(out, "w"),
        indent=1,
    )
    print("done", world, bundle.get("bundle_id"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
