"""Validate the 2026 regulated rail fares freeze spec (#105).

The freeze is ALREADY IN the certified baseline, so the scored object is
the counterfactual: what fares would have done under prior law. The
engine ships both legs — ``gov.dft.rail.fare_index`` and
``gov.dft.rail.prior_law_fare_index`` — which is unusual and is the
reason this lane is cheap. #13 and #67 both had to construct an indexed
counterfactual by hand; here it is a parameter.

WHAT THIS FILE REFUSES:

1. A counterfactual that is not a change. If prior-law equals the
   frozen index in some year, that year scores nothing and would read
   as agreement. Checked per year, not once.
2. A counterfactual pointing the wrong way. Prior law must be ABOVE
   the freeze — fares rising faster is the whole measure. A spec with
   the legs swapped would score a fare CUT and still look plausible.
3. Value claims. DfT's saving figures belong to DfT (the #86/#91
   re-publication rule); they are harvested in their own lane from
   primary documents, never copied from reporting into a spec.
4. Guessed parameter paths. --resolve reads every path and every head
   variable out of a real engine. This repo has published two false
   engine gaps from paths that were never resolved (#100, #101); a
   spec that cannot resolve is not a finding.

Usage:
    python pipeline/validate_rail_fares_spec.py
    /path/to/peuk/bin/python pipeline/validate_rail_fares_spec.py --resolve
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "data" / "uk" / "rail_fares_reform.json"

# Keys that would mean this file had started staging somebody else's
# numbers. The lane is a specification, not a claims source.
FORBIDDEN_VALUE_KEYS = ("value", "saving_gbp", "claims", "costing", "revenue_gbp")


def load(path=SPEC):
    return json.loads(Path(path).read_text())


def validate(spec):
    errors = []

    cf = spec.get("counterfactual") or {}
    if not cf:
        errors.append("no counterfactual mapping")
    readings = spec.get("engine_readings") or {}
    years = spec.get("years") or []
    if not years:
        errors.append("no years")

    for target, source in cf.items():
        for y in years:
            r = readings.get(str(y))
            if not r:
                errors.append(f"{y}: no engine readings recorded")
                continue
            if target not in r or source not in r:
                errors.append(f"{y}: readings missing {target} or {source}")
                continue
            frozen, prior = r[target], r[source]
            # (1) a counterfactual that is not a change scores nothing
            if frozen == prior:
                errors.append(
                    f"{y}: prior law equals the frozen index ({frozen}) — that year "
                    "scores nothing and would read as agreement"
                )
            # (2) direction: prior law must be ABOVE the freeze
            elif prior < frozen:
                errors.append(
                    f"{y}: prior law ({prior}) is BELOW the frozen index ({frozen}) — "
                    "the legs are swapped; this would score a fare cut"
                )

    if not (spec.get("head_variables") or []):
        errors.append("no head variables — nothing to read the effect off")

    # (3) the re-publication rule
    if "stages NO value claims" not in (spec.get("registry_rule") or ""):
        errors.append("registry_rule must state that this file stages no value claims")
    blob = json.dumps(spec)
    for k in FORBIDDEN_VALUE_KEYS:
        if f'"{k}"' in blob:
            errors.append(
                f"{k!r} present — DfT's figures belong to DfT (#86/#91); harvest them "
                "in their own lane from primary documents, never here"
            )

    # The scope mismatch is the thing most likely to be mistaken for an
    # engine divergence, so it must be named up front (#59), not later.
    scope = spec.get("scope_conditions") or {}
    for required in ("regulated_share_note", "entity_mismatch"):
        if not (scope.get(required) or "").strip():
            errors.append(
                f"scope_conditions.{required} is required — an unnamed scope gap gets "
                "attributed to the engine"
            )

    if errors:
        raise ValueError("rail fares spec invalid:\n  - " + "\n  - ".join(errors))
    return len(years)


def resolve(spec):
    """Read every path and head variable out of a REAL engine."""
    import policyengine_uk

    system = policyengine_uk.CountryTaxBenefitSystem()

    def get(path):
        node = system.parameters
        for part in path.split("."):
            node = node.children[part]
        return node

    checked = 0
    for target, source in (spec.get("counterfactual") or {}).items():
        for path in (target, source):
            node = get(path)
            for y in spec["years"]:
                live = float(node(f"{y}-01-01"))
                recorded = spec["engine_readings"][str(y)][path]
                if live != recorded:
                    raise SystemExit(
                        f"{path} at {y}: engine says {live}, spec records {recorded}"
                    )
                checked += 1

    missing = [v for v in spec["head_variables"] if v not in system.variables]
    if missing:
        raise SystemExit(f"head variables absent from the engine: {missing}")

    return checked, len(spec["head_variables"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true")
    args = ap.parse_args(argv)
    spec = load()
    n = validate(spec)
    print(f"rail fares spec valid: {n} years")
    if args.resolve:
        readings, heads = resolve(spec)
        print(f"  resolved {readings} parameter readings against the certified engine")
        print(f"  confirmed {heads} head variables exist")


if __name__ == "__main__":
    main(sys.argv[1:])
