"""Validate the bus fare cap GAP registry (#106).

The £2/£3 bus fare cap cannot be scored by the certified engine. This
file records that verdict and, more importantly, the evidence for it.

WHY THE EVIDENCE MATTERS MORE THAN THE VERDICT: this repo has published
two false engine gaps (#100, #101), both from a guessed parameter path
that failed to resolve and was read as proof of absence. A validator
cannot catch that class by resolving paths — a not_expressible entry
carries no path to resolve. So the claim has to be backed by an
exhaustive NAME SEARCH instead.

And the search has to cover VARIABLES as well as PARAMETERS. The first
pass at this very measure searched only the parameter tree, concluded
bus was absent from the model, and was wrong: ``bus_subsidy_spending``
is a variable, and a parameter-only search misses it. That near-miss is
why ``--probe`` below re-runs BOTH searches against a real engine and
refuses any drift.

The gap that survives is sharper than "PolicyEngine does not do buses":
bus subsidy is present as a household quantity, but as a PURE INPUT
with no formula and no parameter behind it, where rail has the
price/quantity split a reform needs.

Usage:
    python pipeline/validate_bus_fares_gap.py
    /path/to/peuk/bin/python pipeline/validate_bus_fares_gap.py --probe
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "data" / "uk" / "bus_fares_gap.json"

FORBIDDEN_VALUE_KEYS = ("value", "saving_gbp", "claims", "costing", "revenue_gbp")


def load(path=REG):
    return json.loads(Path(path).read_text())


def validate(reg):
    errors = []

    if reg.get("verdict") != "not_expressible":
        errors.append("this registry exists to record a gap verdict")

    # A gap verdict must be backed by a search, never by a guessed path.
    search = reg.get("name_search") or {}
    for key in ("parameter_pattern", "variable_pattern"):
        if not (search.get(key) or "").strip():
            errors.append(
                f"name_search.{key} missing — a gap claim needs a search, and a "
                "guessed path that fails to resolve proves nothing (#100, #101)"
            )
    # Specifically: searching parameters alone is what got this measure
    # wrong the first time.
    if "variable_hits" not in search:
        errors.append(
            "name_search.variable_hits missing — a parameter-only search misses "
            "bus_subsidy_spending, which is exactly how the first pass at this "
            "measure reached a false conclusion"
        )
    if "VARIABLES as well as PARAMETERS" not in (reg.get("search_rule") or ""):
        errors.append("search_rule must state that variables are searched too")

    # The verdict is only honest if it says what IS there. A gap
    # registry that omits the present-but-unusable machinery reads as a
    # broader claim than the evidence supports.
    have = reg.get("what_the_engine_does_have") or {}
    if "bus_subsidy_spending" not in have:
        errors.append(
            "the registry must record that bus_subsidy_spending EXISTS — omitting it "
            "overstates the gap"
        )
    else:
        bss = have["bus_subsidy_spending"]
        if bss.get("has_formula") is not False:
            errors.append(
                "bus_subsidy_spending.has_formula must be False — a pure input with "
                "no formula IS the gap; if it gained one the verdict changes"
            )

    if "missing FACTORISATION" not in (reg.get("the_gap") or ""):
        errors.append(
            "the_gap must name the missing factorisation, not a missing subject area"
        )
    if not (reg.get("upstream_item") or "").strip():
        errors.append(
            "not_expressible without an upstream item is a shrug — say what would "
            "close it"
        )

    # The nearest lever has to be named AND ruled out, or a future
    # reader will find it and assume nobody looked.
    lever = reg.get("nearest_lever_and_why_it_does_not_work") or {}
    if not lever.get("path") or not (lever.get("why_not") or "").strip():
        errors.append(
            "the nearest lever must be named and explicitly ruled out — otherwise a "
            "reader finds it and assumes it was missed"
        )

    if "stages NO value claims" not in (reg.get("registry_rule") or ""):
        errors.append("registry_rule must state that this file stages no value claims")
    blob = json.dumps(reg)
    for k in FORBIDDEN_VALUE_KEYS:
        if f'"{k}"' in blob:
            errors.append(
                f"{k!r} present — the evaluation figures belong to their originators "
                "(#86/#91); harvest them in their own lane"
            )

    if errors:
        raise ValueError(
            "bus fares gap registry invalid:\n  - " + "\n  - ".join(errors)
        )
    return reg["measure_key"]


def probe(reg):
    """Re-run BOTH searches against a real engine and refuse drift.

    If a bus parameter or a bus formula ever appears upstream, this
    fails — which is the point. A gap registry that cannot notice its
    own gap closing is a stale opinion.
    """
    import policyengine_uk

    system = policyengine_uk.CountryTaxBenefitSystem()
    search = reg["name_search"]

    hits = []

    def walk(node, prefix="", depth=0):
        if depth > 9:
            return
        for c in getattr(node, "children", {}) or {}:
            full = f"{prefix}.{c}" if prefix else c
            if re.search(search["parameter_pattern"], c, re.I) and not full.startswith(
                "baseline."
            ):
                hits.append(full)
            walk(node.children[c], full, depth + 1)

    walk(system.parameters)
    if sorted(hits) != sorted(search["parameter_hits"]):
        raise SystemExit(
            "parameter search drifted from the recorded reading:\n"
            f"  engine: {sorted(hits)}\n  recorded: {sorted(search['parameter_hits'])}"
        )

    live_vars = sorted(
        v for v in system.variables if re.search(search["variable_pattern"], v, re.I)
    )
    if live_vars != sorted(search["variable_hits"]):
        raise SystemExit(
            "variable search drifted from the recorded reading:\n"
            f"  engine: {live_vars}\n  recorded: {sorted(search['variable_hits'])}"
        )

    dft = list(system.parameters.children["gov"].children["dft"].children)
    if sorted(dft) != sorted(search["gov_dft_children"]):
        raise SystemExit(f"gov.dft children changed: {dft}")

    # The verdict's load-bearing fact: still a pure input.
    v = system.variables["bus_subsidy_spending"]
    if any(a.startswith("formula") for a in dir(type(v))):
        raise SystemExit(
            "bus_subsidy_spending now HAS a formula — the gap may have closed "
            "upstream; re-read this registry rather than trusting it"
        )

    return len(hits), len(live_vars)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args(argv)
    reg = load()
    key = validate(reg)
    print(f"bus fares gap registry valid: {key}")
    if args.probe:
        n_params, n_vars = probe(reg)
        print(f"  re-ran the name search: {n_params} parameters, {n_vars} variables")
        print("  bus_subsidy_spending is still a pure input — the gap stands")


if __name__ == "__main__":
    main(sys.argv[1:])
