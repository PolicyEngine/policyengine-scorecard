"""Validate the take-up ASSUMPTION registry (#130).

Every other lane in this repo compares OUTPUTS. This one compares
ASSUMPTIONS: what PolicyEngine-UK and UKMOD each assume about benefit
take-up, read from the certified engine on one side and from UKMOD's
published Table 3.4 on the other.

WHAT V1 GOT WRONG, AND WHY IT MATTERS HERE. v1 reported that
PolicyEngine "assumes full take-up" for Housing Benefit, Income
Support, Child Tax Credit and Working Tax Credit, and set those 1.0
values against UKMOD's 0.32-0.96. That was wrong and unfair. All four
are CLOSED legacy benefits, and the engine's own parameter description
says so: "By definition, this is 100%, because only current claimants
are eligible (no new claims)." The value is a cohort artifact of the
denominator, not a modelling choice. v1 read the values without
reading the descriptions sitting beside them.

WHAT SURVIVES, AND IS A SCORECARD OBJECT. Three parameters are genuine
assumed rates on OPEN programmes: Universal Credit 0.55, Pension
Credit 0.70, income-based JSA 0.56. Universal Credit is the
substantive one — 0.55 against the 0.80 the Resolution Foundation
states for the shared Landman/PERU engine and the 0.82 recorded for
that engine in the Scottish Government's appendix. Those ARE
like-for-like, and the spread is 25-27 points on the largest
working-age benefit.

WHAT THIS FILE REFUSES:

1. Value claims. The rates originate with DWP and HMRC (#86/#91);
   UKMOD's table is a transcription plus its own mid-point choices.
   Recorded as comparison context with the originator named, never as
   something to score against.
2. A conclusion about output error. Calibration and reported-recipient
   anchoring may bring PolicyEngine's outputs closer than the bare
   parameter implies. Establishing output error needs #76.
3. A comparison across denominators. A closed-cohort parameter counts
   participation among EXISTING CLAIMANTS; an open-programme rate
   counts take-up among everyone ENTITLED. Crossing that line measures
   a difference in population, not behaviour.
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


def closed_cohort_parameters(reg):
    """Parameters at 1.0 because the programme is closed to new claims."""
    return {
        p: e for p, e in reg["policyengine_assumptions"].items() if e["closed_cohort"]
    }


def comparable_parameters(reg):
    """The ones that are genuine assumed rates on open programmes."""
    return {
        p: e
        for p, e in reg["policyengine_assumptions"].items()
        if e["comparable_to_an_open_programme_rate"]
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
        # A 1.0 must be EXPLAINED from the engine, not asserted by us.
        if e.get("value_2026") == 1.0:
            if not e.get("closed_cohort"):
                errors.append(
                    f"{path}: reads 1.0 but is not marked closed_cohort. Either "
                    "it is a closed programme and the rationale belongs here, or "
                    "it really is a full-take-up assumption and that is a much "
                    "bigger claim than this registry should make quietly"
                )
            if "no new claims" not in (e.get("engine_description") or ""):
                errors.append(
                    f"{path}: closed_cohort asserted without the engine's own "
                    "words. v1's error was reading values without reading the "
                    "descriptions beside them — quote the description"
                )
            if "BY CONSTRUCTION" not in (e.get("why_one") or ""):
                errors.append(f"{path}: why_one must say the 1.0 is definitional")
        if e.get("comparable_to_an_open_programme_rate") == e.get("closed_cohort"):
            errors.append(f"{path}: comparability disagrees with closed_cohort")

    if closed_cohort_parameters(reg) and "EXISTING CLAIMANTS" not in (
        reg.get("divergence_axis") or ""
    ):
        errors.append(
            "closed-cohort parameters are present, but divergence_axis does not "
            "name the denominator difference that makes them incomparable (#59)"
        )
    if "may NOT be compared" not in (reg.get("comparability_rule") or ""):
        errors.append(
            "comparability_rule must forbid comparing a closed-cohort parameter "
            "with an open-programme rate — that comparison is what #131 caught"
        )
    if "NARROWED after review" not in (reg.get("the_finding") or ""):
        errors.append(
            "the_finding must record that v1 overstated this, and how it was "
            "caught — a registry that quietly narrows its own claim is worse "
            "than one that never made it"
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
    closed = closed_cohort_parameters(reg)
    comparable = comparable_parameters(reg)
    print(f"takeup assumption registry valid: {n} PolicyEngine parameters")
    print(
        f"  closed cohort (1.0 by construction, NOT comparable): {len(closed)} — "
        f"{sorted(e['benefit'] for e in closed.values())}"
    )
    print(
        f"  genuine open-programme rates: {len(comparable)} — "
        f"{sorted(e['benefit'] for e in comparable.values())}"
    )
    if args.resolve:
        print(f"  re-read {resolve(reg)} parameters from the certified engine")


if __name__ == "__main__":
    main(sys.argv[1:])
