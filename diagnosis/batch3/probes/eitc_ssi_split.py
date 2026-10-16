"""Probe for batch-3 items E2 (Connecticut EITC) and A3 (SSI
couples), as-served us-6.2.1 world, CY2024.

E2: per State x qualifying-children bin, weighted tax units (heads) that are
entitled to the EITC (rebuilt from the formula's parts, the
irs_eitc_participation construction), and of those the take-up-flag-off ones.

A3: adults in joint SSI claims (ssi_claim_is_joint) and the two individual
categories, average month: persons with a payment due (ssi_if_takes_up > 0),
paid (ssi > 0), take-up flag, reported SSI (ssi_reported > 0), and reported
SSI above 12 x the 2024 couple FBR per person (an implausible SSI amount).

Usage: .venv-pe/bin/python diagnosis/batch3/probes/eitc_ssi_split.py <out.json>
"""

import json
import sys

import numpy as np

YEAR = 2024
MONTHS = [f"{YEAR}-{m:02d}" for m in range(1, 13)]


def main(out: str) -> None:
    import policyengine as pe

    sim = pe.us.managed_microsimulation()
    bundle = {k: str(v) for k, v in getattr(sim, "policyengine_bundle", {}).items()}
    ones = sim.calculate("age", YEAR) >= -1

    def person(name, period=YEAR):
        return np.asarray(sim.calculate(name, period, map_to="person").values)

    result = {"bundle": bundle}

    # --- E2 ---------------------------------------------------------------
    state = person("state_code_str").astype(str)
    head = np.asarray(sim.calculate("is_tax_unit_head", YEAR).values).astype(bool)
    limitation = np.maximum(0, person("eitc_maximum") - person("eitc_reduction"))
    entitled = (person("eitc_eligible") > 0) & (
        np.minimum(person("eitc_phased_in"), limitation) > 0
    )
    flag = person("takes_up_eitc") > 0
    kids = person("eitc_child_count")
    bins = {"0": kids == 0, "1": kids == 1, "2": kids == 2, "3+": kids >= 3}
    eitc = {}
    for s in sorted(set(state)) + ["US"]:
        g = np.ones(len(state), bool) if s == "US" else state == s
        for b, bm in bins.items():
            m = entitled & head & g & bm
            eitc[f"{s}|{b}"] = {
                "entitled": float(ones[m].sum()),
                "flag_off": float(ones[m & ~flag].sum()),
            }
    result["eitc"] = eitc

    # --- A3 ---------------------------------------------------------------
    age = person("age")
    adult = age >= 18
    joint = np.asarray(sim.calculate("ssi_claim_is_joint", YEAR).values).astype(bool)
    takes_up = np.asarray(
        sim.calculate("takes_up_ssi_if_eligible", YEAR).values
    ).astype(bool)
    reported = np.asarray(sim.calculate("ssi_reported", YEAR).values)
    fbr_couple = float(
        sim.tax_benefit_system.parameters(f"{YEAR}-01-01").gov.ssa.ssi.amount.couple
    )
    cats = {
        "couples": adult & joint,
        "aged": adult & ~joint & (age >= 65),
        "disabled": adult & ~joint & (age < 65),
    }
    ssi = {"fbr_couple_monthly": fbr_couple}
    for cat in cats:
        ssi[cat] = {
            k: 0.0
            for k in (
                "payable",
                "paid",
                "payable_flag",
                "payable_reported",
                "payable_reported_above_couple_fbr",
                "paid_reported",
                "paid_unreported",
            )
        }
    for m in MONTHS:
        payable = np.asarray(sim.calculate("ssi_if_takes_up", m).values) > 0
        paid = np.asarray(sim.calculate("ssi", m).values) > 0
        rep = reported > 0
        high = reported > 12 * fbr_couple
        for cat, mask in cats.items():
            base = payable & mask
            add = {
                "payable": base,
                "paid": paid & mask,
                "payable_flag": base & takes_up,
                "payable_reported": base & rep,
                "payable_reported_above_couple_fbr": base & high,
                "paid_reported": paid & mask & rep,
                "paid_unreported": paid & mask & ~rep,
            }
            for k, v in add.items():
                ssi[cat][k] += float(ones[v].sum()) / len(MONTHS)
    result["ssi"] = ssi
    json.dump(result, open(out, "w"), indent=1)
    print("done", bundle.get("bundle_id"))


if __name__ == "__main__":
    main(sys.argv[1])
