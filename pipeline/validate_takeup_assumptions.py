"""Validate the take-up ASSUMPTION registry (#130).

Every other lane in this repo compares OUTPUTS. This one compares
ASSUMPTIONS: what PolicyEngine-UK and UKMOD each assume about benefit
take-up, read from the certified engine on one side and from UKMOD's
published Table 3.4 on the other.

WHY THAT IS A SCORECARD OBJECT. PolicyEngine assumes FULL take-up
(1.0) for Housing Benefit, Income Support, Child Tax Credit and
Working Tax Credit. UKMOD applies published DWP/HMRC non-take-up for
the same benefits, as low as 0.32 for WTC with no children and 0.57
for working-age Housing Benefit in work. Where a model assumes full
take-up it produces an ENTITLEMENT count, while the administrative
figure it would be scored against is a RECEIPT count. Comparing those
measures non-take-up and attributes it to the engine — the exact class
of unattributed divergence #59's axis registry exists to prevent.

WHAT THIS FILE REFUSES:

1. Value claims. The rates originate with DWP and HMRC (#86/#91);
   UKMOD's table is a transcription plus its own mid-point choices.
   Recorded as comparison context with the originator named, never as
   something to score against.
2. A conclusion about output error. Calibration and reported-recipient
   anchoring may bring PolicyEngine's outputs closer than the bare
   parameter implies. Establishing output error needs #76.
3. An unnamed divergence axis. If a full-take-up parameter is present,
   the entitlement-vs-receipt axis must be named.
4. A pin that is not the certified engine's.

Usage:
    python pipeline/validate_takeup_assumptions.py
    /path/to/peuk/bin/python pipeline/validate_takeup_assumptions.py --resolve
"""

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "takeup_assumptions.json"

FORBIDDEN_VALUE_KEYS = ("value", "claims", "caseload", "expenditure_gbp")


def load(path=REGISTRY):
    return json.loads(Path(path).read_text())


def full_take_up_parameters(reg):
    return {
        p: e
        for p, e in reg["policyengine_assumptions"].items()
        if e["assumes_full_take_up"]
    }


def validate(reg):
    errors = []

    pe = reg.get("policyengine_assumptions") or {}
    if not pe:
        errors.append("no PolicyEngine assumptions recorded")
    for path, e in pe.items():
        if not isinstance(e.get("value_2026"), (int, float)):
            errors.append(f"{path}: no value read from the engine")
        elif not 0 < e["value_2026"] <= 1:
            errors.append(f"{path}: take-up {e['value_2026']} is not a rate in (0, 1]")
        if not e.get("schedule"):
            errors.append(
                f"{path}: no schedule recorded — a single value hides how OLD "
                "the assumption is, which is half the finding"
            )
        if e.get("assumes_full_take_up") != (e.get("value_2026") == 1.0):
            errors.append(f"{path}: assumes_full_take_up disagrees with the value")

    # The whole point: a full-take-up assumption changes what the model
    # is producing, so the axis must be named.
    if full_take_up_parameters(reg) and "ENTITLEMENT" not in (
        reg.get("divergence_axis") or ""
    ):
        errors.append(
            "full take-up is assumed somewhere, but divergence_axis does not "
            "name the entitlement-vs-receipt difference — an unnamed axis gets "
            "attributed to the engine (#59)"
        )

    uk = reg.get("ukmod_assumptions") or {}
    if not uk.get("originating_sources"):
        errors.append(
            "ukmod_assumptions must name the ORIGINATING sources — the rates "
            "are DWP's and HMRC's, not UKMOD's (#86/#91)"
        )
    if "SECOND-HAND" not in (uk.get("transcription_note") or ""):
        errors.append(
            "ukmod_assumptions must state that it is a second-hand transcription"
        )
    if "ASSUMED AGGREGATE RATE" not in (uk.get("mechanism_note") or ""):
        errors.append(
            "the mechanism difference must be stated: UKMOD applies household-"
            "level per-benefit take-up, PolicyEngine uses national scalars, so "
            "only the assumed aggregate rate is comparable"
        )

    if "does NOT claim" not in (reg.get("not_a_conclusion") or ""):
        errors.append(
            "not_a_conclusion is required — a parameter difference is not an "
            "output error, and this registry must not be read as claiming one"
        )

    if "stages NO value claims" not in (reg.get("registry_rule") or ""):
        errors.append("registry_rule must state that this file stages no value claims")
    blob = json.dumps(reg)
    for k in FORBIDDEN_VALUE_KEYS:
        if f'"{k}"' in blob:
            errors.append(
                f"{k!r} present — take-up RATES are assumptions, not scoreable "
                "values; the underlying figures belong to DWP and HMRC"
            )

    if errors:
        raise ValueError(
            "takeup assumption registry invalid:\n  - " + "\n  - ".join(errors)
        )
    return len(pe)


def resolve(reg):
    """Re-read every parameter out of a real engine and refuse drift."""
    import policyengine_uk

    installed = importlib.metadata.version("policyengine-uk")
    pinned = reg["engine_pin"]["policyengine_uk"]
    if installed != pinned:
        raise SystemExit(
            f"engine pin mismatch: registry pins {pinned}, installed is "
            f"{installed}. These are assumptions read FROM an engine; reading "
            "them from a different one proves nothing about the pinned world."
        )

    params = policyengine_uk.CountryTaxBenefitSystem().parameters

    def get(path):
        node = params
        for part in path.split("."):
            node = node.children[part]
        return node

    for path, e in reg["policyengine_assumptions"].items():
        live = float(get(path)("2026-01-01"))
        if live != e["value_2026"]:
            raise SystemExit(
                f"{path}: engine says {live}, registry records {e['value_2026']}"
            )
    return len(reg["policyengine_assumptions"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true")
    args = ap.parse_args(argv)
    reg = load()
    n = validate(reg)
    full = full_take_up_parameters(reg)
    print(f"takeup assumption registry valid: {n} PolicyEngine parameters")
    print(
        f"  assuming FULL take-up: {len(full)} — {sorted(e['benefit'] for e in full.values())}"
    )
    if args.resolve:
        print(f"  re-read {resolve(reg)} parameters from the certified engine")


if __name__ == "__main__":
    main(sys.argv[1:])
