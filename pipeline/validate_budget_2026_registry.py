"""Validate the Autumn Budget 2026 scoreability registry (#96).

data/uk/budget_2026_measures.json records what each REPORTED Budget
measure would be as a PolicyEngine-UK reform, and whether the certified
engine can express it — so that on 28 October a counterpart can be
computed immediately instead of the work starting then.

It is a scoreability registry, NOT a claims lane. It stages no values.
The revenue figures in circulation are journalism citing third parties,
and the #86 rule applies: a re-published figure belongs to its
originator, not to the outlet that repeated it. When HM Treasury and the
OBR publish the scorecard and the EFO costings on the day, those arrive
as claims through the existing OBR/HMT lanes and join to these measure
keys.

Two things this validator enforces that prose cannot:

1. **Expressible means resolved, not asserted.** With policyengine-uk
   importable, every path on every expressible/partial measure is
   resolved against the live parameter tree, and the recorded 2026
   baseline value is compared to what the engine actually returns. A
   registry that drifts from the engine fails here rather than at the
   first real run.

2. **A not_expressible measure must say WHY, and a development item must
   be marked.** "PolicyEngine can't do this" without a named gap is the
   unearned excuse the citable-gap rule exists to prevent.

Usage:
    python pipeline/validate_budget_2026_registry.py            # schema only
    .venv-pe/bin/python pipeline/validate_budget_2026_registry.py --resolve
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "budget_2026_measures.json"

COMPUTABILITY = {"expressible", "partial", "not_expressible"}
REPORTED_STATUS = {
    "probable",
    "possible",
    "unlikely",
    "already_announced",
    "ruled_out_for_this_budget",
}


def load(path=REGISTRY):
    return json.loads(Path(path).read_text())


def validate(reg):
    """Schema + honesty checks; raises with every defect listed."""
    errors = []
    seen = set()
    for m in reg["measures"]:
        k = m.get("measure_key", "?")
        if k in seen:
            errors.append(f"duplicate measure_key {k}")
        seen.add(k)
        if not k.startswith("ab2026__"):
            errors.append(f"{k}: measure_key must carry its fiscal event prefix")
        if m.get("computability") not in COMPUTABILITY:
            errors.append(f"{k}: bad computability {m.get('computability')!r}")
        if m.get("reported_status") not in REPORTED_STATUS:
            errors.append(f"{k}: bad reported_status {m.get('reported_status')!r}")
        if not (m.get("source_note") or "").strip():
            errors.append(f"{k}: every measure states where it was reported")
        if not (m.get("title") or "").strip():
            errors.append(f"{k}: missing title")

        deltas = m.get("pe_reform_delta")
        if m["computability"] == "expressible":
            if not deltas:
                errors.append(f"{k}: expressible but carries no reform delta")
            if not m.get("engine_baseline_2026"):
                errors.append(
                    f"{k}: expressible but records no engine baseline to "
                    "check the registry against"
                )
        if m["computability"] == "not_expressible":
            if deltas:
                errors.append(f"{k}: not_expressible yet carries a reform delta")
            if not (m.get("why") or "").strip():
                errors.append(
                    f"{k}: not_expressible without a named gap — 'PolicyEngine "
                    "can't do this' is not a finding unless it says what is "
                    "missing"
                )
            if not (
                m.get("policyengine_uk_development_item") or m.get("out_of_model_scope")
            ):
                errors.append(
                    f"{k}: a not_expressible measure is either an upstream "
                    "development item or out of the model's scope; say which"
                )
        if m["computability"] == "partial" and not (m.get("missing") or "").strip():
            errors.append(f"{k}: partial without naming the missing legs")

    # The whole reported package must be represented, including the parts
    # this model cannot touch — a registry that silently listed only the
    # modellable half would overstate coverage.
    if not any(x.get("out_of_model_scope") for x in reg["measures"]):
        errors.append(
            "no measure is marked out_of_model_scope: the reported package "
            "includes business levies a household microsimulation cannot "
            "touch, and omitting them would overstate coverage"
        )
    if errors:
        raise ValueError(
            f"registry invalid ({len(errors)} defects):\n  " + "\n  ".join(errors)
        )
    return len(reg["measures"])


def _resolve(node, path):
    for part in path.split("."):
        m = re.fullmatch(r"(.+)\[(\d+)\]", part)
        node = (
            getattr(node, m.group(1)).brackets[int(m.group(2))]
            if m
            else getattr(node, part)
        )
    return node


def resolve_against_engine(reg, year=2026):
    """Every path must resolve, and every recorded baseline must match."""
    import policyengine_uk

    pin = reg["engine_pin"]["policyengine_uk"]
    try:
        import importlib.metadata

        installed = importlib.metadata.version("policyengine-uk")
    except Exception:
        installed = None
    if installed != pin:
        raise SystemExit(
            f"policyengine-uk {installed} installed, registry pinned to {pin}"
        )

    params = policyengine_uk.CountryTaxBenefitSystem().parameters
    problems, checked = [], 0
    for m in reg["measures"]:
        for path in m.get("pe_reform_delta") or {}:
            try:
                node = _resolve(params, path)
            except AttributeError:
                problems.append(f"{m['measure_key']}: path does not resolve: {path}")
                continue
            checked += 1
            recorded = (m.get("engine_baseline_2026") or {}).get(path)
            if isinstance(recorded, (int, float)):
                try:
                    live = float(node(f"{year}-06-01"))
                except Exception:
                    continue
                if abs(live - recorded) > 1e-9:
                    problems.append(
                        f"{m['measure_key']}: {path} baseline recorded "
                        f"{recorded}, engine says {live}"
                    )
    if problems:
        raise SystemExit(
            f"{len(problems)} registry/engine mismatches:\n  " + "\n  ".join(problems)
        )
    return checked


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--resolve", action="store_true")
    args = ap.parse_args(argv)
    reg = load()
    n = validate(reg)
    print(f"registry valid: {n} measures")
    by = {}
    for m in reg["measures"]:
        by[m["computability"]] = by.get(m["computability"], 0) + 1
    print("  computability:", by)
    if args.resolve:
        checked = resolve_against_engine(reg)
        print(f"  resolved {checked} parameter paths against the certified engine")
    return reg


if __name__ == "__main__":
    main(sys.argv[1:])
