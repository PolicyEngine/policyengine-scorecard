"""Who is worse off when the two-child limit goes, and through which
variables (lane uk-two-child-limit-poverty).

The certified-pair run counts, for every world and year it computes, the
households whose HBAI income is lower than in the with-limit world and the
benefit units whose Universal Credit is lower. Removing a limit should make
no one worse off, so this script finds them in the same managed worlds and
records, over them, how many there are and how every benefit-unit and
household variable of the income and claim chain moved, so a note can say
what happened rather than guess. It writes counts and weighted totals only,
never a household's own values: this repository is public and the microdata
is not.

    PYTHONPATH=. <the pair's venv>/bin/python -m pipeline.diagnose_uk_two_child_limit_losers \\
        [--pair <pair id>] [--dataset-file <certified bytes>]

Writes results/uk/two_child_limit_poverty/diagnostics/losers.json.
"""

from __future__ import annotations

import argparse
import json
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


def at(sim, name: str, year: int, entity: str) -> np.ndarray:
    return np.asarray(
        sim.calculate(name, year, map_to=entity, decode_enums=False), dtype=float
    )


def tally(mask: np.ndarray, weight: np.ndarray) -> dict:
    return {"sample": int(mask.sum()), "weight": float(weight[mask].sum())}


def moved(sims: dict, names: list[str], year: int, entity: str, mask, weight):
    """Each variable, at `entity`, that differs between the worlds anywhere in
    `mask`: how many of the masked units it moved in, and its weighted totals
    over all of them in each world."""
    out = {}
    if not mask.any():
        return out
    w = weight[mask]
    for name in names:
        v = {n: at(s, name, year, entity)[mask] for n, s in sims.items()}
        change = np.abs(v["world"] - v["with_limit"]) > 0.005
        if change.any():
            out[name] = {
                **tally(change, w),
                "with_limit_weighted_total": float(w @ v["with_limit"]),
                "world_weighted_total": float(w @ v["world"]),
            }
    return dict(sorted(out.items()))


def case(sims: dict, year: int, household_names: list, benunit_names: list) -> dict:
    base = sims["with_limit"]
    hweight = at(base, "household_weight", year, "household")
    bweight = at(base, "benunit_weight", year, "benunit")
    # the compute's own tests (compute.gainers): a penny is float noise for
    # HBAI income; Universal Credit counts any fall
    d = {
        n: at(s, "hbai_household_net_income", year, "household")
        for n, s in sims.items()
    }
    loss = d["with_limit"] - d["world"]
    falls = loss > 0.01
    uc = {n: at(s, "universal_credit", year, "benunit") for n, s in sims.items()}
    uc_fall = uc["with_limit"] - uc["world"]
    out = {
        "hbai_income_falls": {
            **tally(falls, hweight),
            "weighted_loss_gbp": float(hweight[falls] @ loss[falls]),
            "by_variable": moved(
                sims, household_names, year, "household", falls, hweight
            ),
        },
        "benunits_uc_falls": {
            **tally(uc_fall > 0, bweight),
            "largest_fall_gbp_year": float(uc_fall.max(initial=0.0)),
            "over_a_penny": tally(uc_fall > 0.01, bweight),
            "by_variable": moved(
                sims, benunit_names, year, "benunit", uc_fall > 0.01, bweight
            ),
        },
    }
    if falls.any():
        u = {
            n: at(s, "universal_credit", year, "household")[falls]
            for n, s in sims.items()
        }
        t = {
            n: at(s, "tax_free_childcare", year, "household")[falls]
            for n, s in sims.items()
        }
        w = hweight[falls]
        starts = (u["with_limit"] == 0) & (u["world"] > 0)
        ends = (t["with_limit"] > 0) & (t["world"] == 0)
        # the measured mechanism: a Universal Credit award begins, and
        # Tax-Free Childcare, which a UC award disqualifies, ends
        out["hbai_income_falls"]["mechanism"] = {
            "universal_credit_starts": tally(starts, w),
            "tax_free_childcare_ends": tally(ends, w),
            "both": tally(starts & ends, w),
        }
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pair", default=compute.DEFAULT_PAIR)
    ap.add_argument("--dataset-file", type=Path)
    args = ap.parse_args(argv)
    # the compute's own preflight: the pair's wheels, dataset and bundle
    record, pre = compute.preflight_pair(args.pair, args.dataset_file)
    from policyengine_uk.variables.household.income.household_benefits import (
        HOUSEHOLD_BENEFIT_VARIABLES,
    )

    base = compute.build_certified(compute.WORLDS["with_limit"])
    compute.check_runtime(base, "with_limit", pre)
    variables = base.tax_benefit_system.variables
    household_names = [
        n
        for n in dict.fromkeys(
            [
                *CANDIDATES["benunit"],
                *CANDIDATES["household"],
                *HOUSEHOLD_BENEFIT_VARIABLES,
            ]
        )
        if n in variables
    ]
    benunit_names = [n for n in CANDIDATES["benunit"] if n in variables]
    cases = {}
    for name, years in compute.CERTIFIED_YEARS.items():
        if name == "with_limit":
            continue
        world = compute.build_certified(compute.WORLDS[name])
        compute.check_runtime(world, name, pre)
        for year in years:
            cases[f"{name} {year}"] = case(
                {"with_limit": base, "world": world},
                year,
                household_names,
                benunit_names,
            )
            print(name, year, json.dumps(cases[f"{name} {year}"])[:400], flush=True)
        del world
    path = compute.OUTPUT_DIR / "diagnostics" / "losers.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "kind": "uk_two_child_limit_poverty_losers",
        "pair_id": record["variant_id"],
        "cases": cases,
    }
    path.write_text(json.dumps(summary, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
