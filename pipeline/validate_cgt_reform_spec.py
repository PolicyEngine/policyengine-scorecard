"""Validate the CGT alignment reform spec and its elasticity sweep (#97).

Aligning capital gains tax rates with income tax rates is the Budget's
flagship broad-based option, and PolicyEngine-UK expresses it in three
parameters. The interesting part is not the reform — it is the response.

WHAT THE ENGINE ACTUALLY DOES, verified rather than assumed:
``gov.simulation.capital_gains_responses.elasticity`` is ZERO from
2000-01-01, and ``capital_gains_behavioural_response`` short-circuits to
zero when it is. So a default PE-UK score of this measure is STATIC. The
engine does not hand you a behavioural number; it hands you the
machinery to compute one once YOU supply an elasticity.

That makes the elasticity an assumption THIS REPO makes, and the single
parameter the whole comparison turns on — published estimates of this
measure disagree mostly about the realisations response. So the lane
does not pick a value and publish a number. It sweeps, and this
validator refuses to mark a sweep point publishable until it carries a
named citation.

Usage:
    python pipeline/validate_cgt_reform_spec.py
    .venv-pe/bin/python pipeline/validate_cgt_reform_spec.py --resolve
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "data" / "uk" / "cgt_alignment_reform.json"


def load(path=SPEC):
    return json.loads(Path(path).read_text())


def validate(spec):
    errors = []

    if not spec.get("reform"):
        errors.append("no reform parameters")
    for path, v in (spec.get("reform") or {}).items():
        if not isinstance(v, (int, float)) or not 0 < v < 1:
            errors.append(f"{path}: a rate must be a fraction in (0, 1), got {v!r}")
        if path not in (spec.get("engine_baseline_2026") or {}):
            errors.append(f"{path}: no engine baseline recorded to check against")

    # The reform must actually BE a change; a spec that restates the
    # baseline would score zero and look like agreement.
    unchanged = [
        p
        for p, v in (spec.get("reform") or {}).items()
        if spec.get("engine_baseline_2026", {}).get(p) == v
    ]
    if unchanged:
        errors.append(
            f"reform restates the baseline for {unchanged} — it scores nothing"
        )

    sweep = spec.get("elasticity_sweep") or []
    if len(sweep) < 2:
        errors.append(
            "the sweep needs at least a static leg and one behavioural leg — "
            "a single point is a claim, not a range"
        )
    labels = [s.get("label") for s in sweep]
    if "static" not in labels:
        errors.append("no static leg: the wedge cannot be reported without one")
    for s in sweep:
        label = s.get("label", "?")
        if s.get("publishable"):
            if not (s.get("source") or "").strip():
                errors.append(
                    f"sweep '{label}': marked publishable with no source. An "
                    "elasticity without a citation is an opinion with a "
                    "decimal point"
                )
            if s.get("value") is None:
                errors.append(f"sweep '{label}': publishable but has no value")
        else:
            if not s.get("citation_required"):
                errors.append(
                    f"sweep '{label}': not publishable and not flagged as "
                    "needing a citation — say why it is held"
                )
            if not (s.get("note") or "").strip():
                errors.append(f"sweep '{label}': held without saying what it needs")

    # The static leg must never be presented as comparable to a
    # behavioural costing — that is #67's finding one level up.
    if "LIKE FOR LIKE" not in (spec.get("comparison_rule") or ""):
        errors.append("comparison_rule must state the like-for-like requirement")
    if errors:
        raise ValueError(
            f"spec invalid ({len(errors)} defects):\n  " + "\n  ".join(errors)
        )
    return spec


def publishable_legs(spec):
    return [s for s in spec["elasticity_sweep"] if s.get("publishable")]


def _resolve(node, path):
    for part in path.split("."):
        m = re.fullmatch(r"(.+)\[(\d+)\]", part)
        node = (
            getattr(node, m.group(1)).brackets[int(m.group(2))]
            if m
            else getattr(node, part)
        )
    return node


def resolve_against_engine(spec, year=2026):
    import importlib.metadata

    import policyengine_uk

    pin = spec["engine_pin"]["policyengine_uk"]
    installed = importlib.metadata.version("policyengine-uk")
    if installed != pin:
        raise SystemExit(f"policyengine-uk {installed} installed, pinned {pin}")
    params = policyengine_uk.CountryTaxBenefitSystem().parameters

    problems = []
    for path, recorded in spec["engine_baseline_2026"].items():
        try:
            live = float(_resolve(params, path)(f"{year}-06-01"))
        except AttributeError:
            problems.append(f"{path}: does not resolve")
            continue
        if abs(live - recorded) > 1e-12:
            problems.append(f"{path}: recorded {recorded}, engine {live}")

    # The finding this lane rests on: the response is OFF by default.
    try:
        e = float(_resolve(params, spec["elasticity_parameter"])(f"{year}-06-01"))
    except AttributeError:
        problems.append(f"{spec['elasticity_parameter']}: does not resolve")
        e = None
    if e is not None and e != spec["engine_default_elasticity"]:
        problems.append(
            f"engine default elasticity is now {e}, spec records "
            f"{spec['engine_default_elasticity']} — if the engine has switched "
            "the response on by default, the static/behavioural framing of "
            "this lane needs revisiting"
        )
    if problems:
        raise SystemExit(f"{len(problems)} mismatches:\n  " + "\n  ".join(problems))
    return len(spec["engine_baseline_2026"]) + 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--resolve", action="store_true")
    args = ap.parse_args(argv)
    spec = validate(load())
    pub = publishable_legs(spec)
    print(
        f"spec valid: {len(spec['reform'])} parameters, {len(spec['elasticity_sweep'])} sweep points"
    )
    print(f"  publishable legs: {[s['label'] for s in pub]}")
    held = [s["label"] for s in spec["elasticity_sweep"] if not s.get("publishable")]
    if held:
        print(f"  held pending citation: {held}")
    if args.resolve:
        n = resolve_against_engine(spec)
        print(f"  resolved {n} readings against the certified engine")
    return spec


if __name__ == "__main__":
    main(sys.argv[1:])
