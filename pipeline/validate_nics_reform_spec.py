"""Validate the salary-sacrifice NI cap spec and its assumption sweep (#109).

The £2,000 cap on NI relief for salary-sacrificed pension contributions
is the Budget's largest NICs measure, and the certified engine already
carries it — ``gov.hmrc.national_insurance.salary_sacrifice_pension_cap``
is uncapped through 2028 and 2000 from 2029.

WHAT MAKES THIS LANE DIFFERENT FROM #97: there, the engine's default
asserted NO behaviour (a zero elasticity), so the static leg was
honest without qualification. Here the default asserts SOME behaviour,
and the two assumptions point opposite ways:

    salary_sacrifice_broad_base_haircut_rate   0.0016   ON
    employee_salary_sacrifice_reduction_rate   0        OFF

The haircut reduces employment income for ALL workers, not only
sacrificers, on the reasoning that employers spread the added NI cost
across the whole workforce. It is gated on the cap being finite, so it
activates exactly when the measure bites, and it cites a PolicyEngine
research page as its methodology. The employee response — people
reducing salary sacrifice once it is capped — is off.

So a default score of this measure carries a PolicyEngine incidence
assumption that is neither HMRC's nor OBR's. Published without
disclosure it would surface in a comparison as arithmetic
disagreement. This validator therefore enforces DISCLOSURE, not just
citation: a sweep leg that runs with the haircut on may be publishable,
but only while it is marked as requiring disclosure.

Usage:
    python pipeline/validate_nics_reform_spec.py
    /path/to/peuk/bin/python pipeline/validate_nics_reform_spec.py --resolve
"""

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "data" / "uk" / "nics_salary_sacrifice_reform.json"

HAIRCUT = "gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate"
EMPRESP = "gov.contrib.behavioral_responses.employee_salary_sacrifice_reduction_rate"
CAP = "gov.hmrc.national_insurance.salary_sacrifice_pension_cap"

FORBIDDEN_VALUE_KEYS = ("value", "revenue_gbp", "claims", "costing", "yield_gbp")


def load(path=SPEC):
    return json.loads(Path(path).read_text())


def validate(spec):
    errors = []

    # --- the measure has to actually bite in the recorded schedule ---
    ev = spec.get("baseline_evidence") or {}
    sched = ev.get("schedule") or {}
    if ev.get("path") != CAP:
        errors.append(f"baseline_evidence.path must be {CAP}")
    capped = {y: v for y, v in sched.items() if v is not None}
    uncapped = {y: v for y, v in sched.items() if v is None}
    if not capped or not uncapped:
        errors.append(
            "the schedule must show BOTH an uncapped period and a capped one — a "
            "schedule with only one shows no step and cannot evidence 'carried'"
        )
    else:
        # the step must go uncapped -> capped, never the reverse
        if max(uncapped) > min(capped):
            errors.append(
                f"the cap appears to LAPSE (uncapped at {max(uncapped)} after capped "
                f"at {min(capped)}) — the announced measure only ever switches on"
            )
    # v1 keyed the schedule by bare years and asserted a 01-01 dating
    # convention that does not exist. NI parameters are tax-year dated.
    for key in sched:
        if not key.endswith("-04-06"):
            errors.append(
                f"schedule key {key!r} is not a UK tax-year start — NI parameters are "
                "tax-year dated (the 01-01 'convention' v1 asserted was invented)"
            )
    if "checked_and_not_a_finding" in ev:
        errors.append(
            "checked_and_not_a_finding: v1 used this to excuse a dating it had not "
            "checked. An invented rationale is worse than the thing it excuses — "
            "record findings in corrections_log with how they were caught"
        )
    if not (ev.get("corrections_log") or []):
        errors.append("baseline_evidence.corrections_log missing")

    if spec.get("baseline_verdict") != "carried":
        errors.append(
            "baseline_verdict must be 'carried' when the schedule shows the step"
        )

    # --- the assumptions, and the asymmetry that is the whole finding ---
    ap = spec.get("assumption_parameters") or {}
    for path in (HAIRCUT, EMPRESP):
        if path not in ap:
            errors.append(
                f"{path}: not recorded — it is on by default and must be stated"
            )
    if HAIRCUT in ap and not ap[HAIRCUT].get("engine_default"):
        errors.append(
            f"{HAIRCUT}: recorded as zero/absent. If the engine default were zero this "
            "lane's finding would not exist — re-read the engine rather than the spec"
        )
    if EMPRESP in ap and ap[EMPRESP].get("engine_default") != 0:
        errors.append(
            f"{EMPRESP}: recorded as non-zero. The finding is the ASYMMETRY (employer "
            "cost-spreading on, employee response off); if this changed, restate it"
        )

    # --- disclosure, which is stronger than citation here ---
    sweep = spec.get("assumption_sweep") or []
    if not sweep:
        errors.append(
            "no assumption sweep — this lane does not publish a single number"
        )
    for leg in sweep:
        label = leg.get("label", "?")
        on = bool(leg.get("haircut_rate"))
        if on and not leg.get("disclosure_required"):
            errors.append(
                f"{label}: runs with the broad-base haircut ON but is not marked "
                "disclosure_required — that publishes a PolicyEngine incidence "
                "assumption as if it were arithmetic"
            )
        if not on and leg.get("disclosure_required"):
            errors.append(
                f"{label}: haircut is off, so disclosure_required overstates what the "
                "leg assumes"
            )
        # an unsourced assumption may not be published
        if leg.get("citation_required") and leg.get("publishable"):
            if not (leg.get("source") or "").strip():
                errors.append(
                    f"{label}: publishable with citation_required but no source — this "
                    "is the CGT rule (#97), and it applies to incidence too"
                )
        if leg.get("employee_reduction_rate") is None and leg.get("publishable"):
            errors.append(
                f"{label}: no employee response value chosen, so it cannot be publishable"
            )

    if not any(not leg.get("haircut_rate") and leg.get("publishable") for leg in sweep):
        errors.append(
            "no assumption-free leg is publishable — an official static costing has no "
            "comparable PE leg to be compared against"
        )

    if not (spec.get("divergence_axes") or []):
        errors.append("no divergence axes named — see #59")
    if "must state which sweep leg it is" not in (spec.get("comparison_rule") or ""):
        errors.append("comparison_rule must require the published leg to be identified")

    # --- the re-publication rule ---
    if "stages NO value claims" not in (spec.get("registry_rule") or ""):
        errors.append("registry_rule must state that this file stages no value claims")
    blob = json.dumps(spec)
    for k in FORBIDDEN_VALUE_KEYS:
        if f'"{k}"' in blob:
            errors.append(
                f"{k!r} present — IFS's assessment and the official costing belong to "
                "their originators (#86/#91); harvest them in their own lane"
            )

    if errors:
        raise ValueError("nics reform spec invalid:\n  - " + "\n  - ".join(errors))
    return len(sweep)


def resolve(spec):
    """Read the cap schedule and both assumption defaults out of a REAL engine."""
    import math

    import policyengine_uk

    system = policyengine_uk.CountryTaxBenefitSystem()

    def get(path):
        node = system.parameters
        for part in path.split("."):
            node = node.children[part]
        return node

    # The recorded pin must be the engine actually in front of us. v1
    # hardcoded a version copied from a sibling spec while the readings
    # came from a later engine — a literal pin is not provenance.
    installed = importlib.metadata.version("policyengine-uk")
    pinned = spec["engine_pin"]["policyengine_uk"]
    if installed != pinned:
        raise SystemExit(
            f"engine pin mismatch: spec pins {pinned}, installed is {installed}. "
            "Re-resolve against the installed engine and update the pin — do not "
            "edit the pin by hand to match."
        )

    cap = get(CAP)
    # Keys are the SOURCE's own tax-year dates. Reading at 01-01 would
    # still return the capped value (the parameter has period: year, so
    # core expands it to calendar instants) — which is exactly how v1's
    # false dating note survived --resolve. Read where the source steps.
    for date, recorded in (spec["baseline_evidence"]["schedule"]).items():
        live = float(cap(date))
        live_json = None if math.isinf(live) else live
        if live_json != recorded:
            raise SystemExit(
                f"{CAP} at {date}: engine says {live_json}, spec records {recorded}"
            )

    for path, entry in (spec.get("assumption_parameters") or {}).items():
        live = float(get(path)(f"{spec['years'][0]}-01-01"))
        if live != entry["engine_default"]:
            raise SystemExit(
                f"{path}: engine default is {live}, spec records "
                f"{entry['engine_default']} — the finding rests on this number"
            )

    missing = [v for v in spec["head_variables"] if v not in system.variables]
    if missing:
        raise SystemExit(f"head variables absent from the engine: {missing}")

    return len(spec["baseline_evidence"]["schedule"]), len(spec["head_variables"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true")
    args = ap.parse_args(argv)
    spec = load()
    n = validate(spec)
    print(f"nics reform spec valid: {n} sweep legs")
    if args.resolve:
        years, heads = resolve(spec)
        print(f"  resolved the cap across {years} years against the certified engine")
        print(f"  confirmed both assumption defaults and {heads} head variables")


if __name__ == "__main__":
    main(sys.argv[1:])
