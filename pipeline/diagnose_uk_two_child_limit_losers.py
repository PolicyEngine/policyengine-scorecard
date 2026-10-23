"""Which households lose when the two-child limit is removed, and through
which variables (lane uk-two-child-limit-poverty).

The certified-pair run found households whose HBAI income is lower in
current law than in the with-limit world. This script finds them in the
same two managed worlds and records, for each, its weight and members and
the change in every benefit-unit and household variable of the income and
claim chain that moves, so a note can say what happened rather than guess.

    PYTHONPATH=. .venv-pe6101/bin/python -m pipeline.diagnose_uk_two_child_limit_losers [year]

Writes results/uk/two_child_limit_poverty/diagnostics/losers_<year>.json.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

from pipeline import compute_uk_two_child_limit_poverty as compute

ROOT = Path(__file__).resolve().parent.parent
# variables whose change could make a household worse off, by entity
CANDIDATES = {
    "benunit": [
        "universal_credit",
        "uc_maximum_amount",
        "uc_child_element",
        "uc_housing_costs_element",
        "uc_income_reduction",
        "benefit_cap_reduction",
        "claims_universal_credit",
        "would_claim_uc",
        "claims_uc_at_legacy_closure",
        "legacy_benefits_closed",
        "child_tax_credit",
        "working_tax_credit",
        "housing_benefit",
        "income_support",
        "esa_income",
        "jsa_income",
        "pension_credit",
        "two_child_limit_payment",
        "scottish_child_payment",
        "council_tax_reduction",
    ],
    "household": [
        "household_net_income",
        "hbai_household_net_income",
        "household_benefits",
        "household_tax",
        "council_tax",
        "free_school_meals",
        "gov_spending",
        "gov_tax",
    ],
}


def main(argv: list[str]) -> int:
    year = int(argv[0]) if argv else 2029
    pair = compute.load_pair()
    compute.preflight_certified(pair)
    runtime = compute.RUNTIME_ROOT / pair["pair_id"]
    compute.materialize(pair, runtime)
    os.chdir(runtime)
    sims = {
        name: compute.build_certified(compute.WORLDS[name])
        for name in ("with_limit", "current_law")
    }
    hh = {
        n: np.asarray(s.calculate("hbai_household_net_income", year), dtype=float)
        for n, s in sims.items()
    }
    loss = hh["with_limit"] - hh["current_law"]
    idx = np.where(loss > 0.01)[0]
    base = sims["with_limit"]
    hid = np.asarray(base.calculate("household_id", year), dtype=int)
    weight = np.asarray(base.calculate("household_weight", year), dtype=float)
    bu_hh = np.asarray(base.calculate("household_id", year, map_to="benunit"), dtype=int)
    ages = np.asarray(base.calculate("age", year), dtype=float)
    person_hh = np.asarray(base.calculate("household_id", year, map_to="person"), dtype=int)
    country = np.asarray(base.calculate("country", year, decode_enums=True)).astype(str)
    out = []
    for i in idx:
        record = {
            "household_id": int(hid[i]),
            "weight": float(weight[i]),
            "country": country[i],
            "ages": sorted(ages[person_hh == hid[i]].tolist()),
            "hbai_income_loss_gbp_year": float(loss[i]),
            "changes": {},
        }
        for entity, names in CANDIDATES.items():
            for name in names:
                if name not in base.tax_benefit_system.variables:
                    continue
                vals = {
                    n: np.asarray(
                        s.calculate(name, year, decode_enums=False), dtype=float
                    )
                    for n, s in sims.items()
                }
                rows = np.where(bu_hh == hid[i])[0] if entity == "benunit" else [i]
                for r in rows:
                    a, b = vals["with_limit"][r], vals["current_law"][r]
                    if abs(a - b) > 0.005:
                        record["changes"][f"{name}[{entity} {int(r)}]"] = {
                            "with_limit": float(a),
                            "current_law": float(b),
                        }
        out.append(record)
    path = compute.OUTPUT_DIR / "diagnostics" / f"losers_{year}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "kind": "uk_two_child_limit_poverty_losers",
                "pair_id": pair["pair_id"],
                "year": year,
                "households": out,
                "weighted_households": float(weight[idx].sum()),
            },
            indent=1,
        )
        + "\n"
    )
    print(json.dumps(out, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
