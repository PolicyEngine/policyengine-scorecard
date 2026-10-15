"""Probe for batch-3 item E2: EITC entitled tax units by flag, records vs weighted, CY2024.
Usage: .venv-pe/bin/python diagnosis/batch3/probes/eitc_records.py <out.json>"""

import json, sys
import numpy as np

YEAR = 2024


def main(out):
    import policyengine as pe

    sim = pe.us.managed_microsimulation()
    ones = sim.calculate("age", YEAR) >= -1
    p = lambda n: np.asarray(sim.calculate(n, YEAR, map_to="person").values)
    state = p("state_code_str").astype(str)
    head = np.asarray(sim.calculate("is_tax_unit_head", YEAR).values).astype(bool)
    lim = np.maximum(0, p("eitc_maximum") - p("eitc_reduction"))
    ent = (p("eitc_eligible") > 0) & (np.minimum(p("eitc_phased_in"), lim) > 0)
    flag = p("takes_up_eitc") > 0
    kids = p("eitc_child_count")
    bins = {"0": kids == 0, "1": kids == 1, "2": kids == 2, "3+": kids >= 3}
    res = {}
    for s in ("CT", "IA", "WI", "ND", "US"):
        g = np.ones(len(state), bool) if s == "US" else state == s
        for b, bm in bins.items():
            for fl, fm in (("on", flag), ("off", ~flag)):
                m = ent & head & g & bm & fm
                res[f"{s}|{b}|{fl}"] = {
                    "records": int(m.sum()),
                    "weighted": float(ones[m].sum()),
                }
    json.dump(res, open(out, "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main(sys.argv[1])
