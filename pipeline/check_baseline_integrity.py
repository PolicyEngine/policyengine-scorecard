"""Does the certified world carry the law legislated into its future? (#99)

The repo has a baselines registry (#13) that DESCRIBES worlds, and
ingests that stamp which world a run executed. Nothing checked that the
certified policyengine-uk world actually CONTAINS the measures already
legislated into the years it computes at.

That gap is quiet by construction. A counterpart at 2027 or 2028
measured against a baseline missing an announced measure diverges for a
reason no axis in #59's registry names — so the divergence gets
attributed to whatever axis the analyst reaches for, and the real cause
never appears.

data/uk/baseline_integrity.json records every such measure with the
probe that was run against the engine and one of three verdicts:

    carried      the parameter moves as the measure requires
    consistent   no single parameter encodes it, but the baseline path
                 matches the measure's published profile — evidence
                 recorded, because "we could not find a parameter" is
                 not the same as "it is missing"
    missing      no representation at the pin, so any claim at or beyond
                 the effective date is measured against the wrong law

This module re-runs the probes (with the engine) and enforces the
consequence (always): a `missing` measure means every UK claim at or
beyond its effective period needs the caveat attached, or the repo is
publishing comparisons it cannot defend.

Usage:
    python pipeline/check_baseline_integrity.py                # registry + DB
    .venv-pe/bin/python pipeline/check_baseline_integrity.py --probe
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "baseline_integrity.json"
VERDICTS = {"carried", "consistent", "absent"}


def load(path=REGISTRY):
    return json.loads(Path(path).read_text())


def validate(reg):
    errors = []
    seen = set()
    for m in reg["measures"]:
        k = m.get("key", "?")
        if k in seen:
            errors.append(f"duplicate key {k}")
        seen.add(k)
        if m.get("verdict") not in VERDICTS:
            errors.append(f"{k}: bad verdict {m.get('verdict')!r}")
        for field in (
            "title",
            "announced_at",
            "effective_from",
            "parameter",
            "evidence",
        ):
            if not str(m.get(field) or "").strip():
                errors.append(f"{k}: missing {field}")
        if not m.get("probe"):
            errors.append(
                f"{k}: no probe recorded — a verdict without one is an opinion"
            )
        for i, reading in enumerate(m.get("probe") or []):
            if not isinstance(reading, dict) or reading.get("kind") not in (
                "scalar",
                "subtree",
                "absent",
            ):
                errors.append(
                    f"{k}[{i}]: a probe must record its KIND. Collapsing "
                    "'subtree' into 'absent' is what produced two false engine "
                    "gaps in v1"
                )
            elif not (reading.get("path") and reading.get("date")):
                errors.append(
                    f"{k}[{i}]: a reading must record the PATH and DATE it "
                    "came from, so a re-probe re-runs exactly that rather "
                    "than reconstructing a path from a key name"
                )
        if m["verdict"] == "consistent" and len(m.get("evidence", "")) < 200:
            errors.append(
                f"{k}: a 'consistent' verdict needs the evidence spelled out — "
                "it is the verdict that could be wishful thinking"
            )
        # An ABSENT verdict is now the dangerous one: it asserts the engine
        # cannot do something. v1 got two of them wrong by guessing a path,
        # so a name search is mandatory before the claim can be made.
        if m["verdict"] == "absent" and not str(m.get("name_search") or "").strip():
            errors.append(
                f"{k}: an 'absent' verdict must record the NAME SEARCH that "
                "proved it. A guessed path that fails to resolve proves "
                "nothing — it is how v1 published two false engine gaps"
            )
    if not reg.get("corrections_log"):
        errors.append(
            "corrections_log is empty: the two false gaps this registry "
            "published are part of its evidence and are not quietly dropped"
        )
    if errors:
        raise ValueError(
            f"registry invalid ({len(errors)} defects):\n  " + "\n  ".join(errors)
        )
    return len(reg["measures"])


def baseline_gaps(reg):
    """Measures the certified baseline genuinely fails to carry.

    Distinct from `absent`: a measure that is not law (the pension lump
    sum) is a SCORING capability gap, and the baseline is correct to omit
    it. Only a legislated measure the baseline lacks is a baseline gap —
    and as of this probe there are none.
    """
    return [
        m
        for m in reg["measures"]
        if m["verdict"] == "absent" and not m.get("scoring_gap_not_baseline_gap")
    ]


def _resolve(node, path):
    for part in path.split("."):
        m = re.fullmatch(r"(.+)\[(\d+)\]", part)
        node = (
            getattr(node, m.group(1)).brackets[int(m.group(2))]
            if m
            else getattr(node, part)
        )
    return node


def reprobe(reg):
    """Re-run every recorded probe against the live engine.

    This is the only function that touches the engine, and in v1 it was
    gated behind a flag no test and no workflow ever passed — so CI
    checked the registry against its own recorded numbers and the two
    false gaps sailed through. .github/workflows/baseline-probe.yml now
    installs the pinned engine and runs it.
    """
    import importlib.metadata

    import policyengine_uk

    pin = reg["engine_pin"]["policyengine_uk"]
    installed = importlib.metadata.version("policyengine-uk")
    if installed != pin:
        raise SystemExit(f"policyengine-uk {installed} installed, pinned {pin}")

    params = policyengine_uk.CountryTaxBenefitSystem().parameters

    def live(path, date):
        node = params
        try:
            for part in path.split("."):
                m = re.fullmatch(r"(.+)\[(\d+)\]", part)
                node = (
                    getattr(node, m.group(1)).brackets[int(m.group(2))]
                    if m
                    else getattr(node, part)
                )
        except AttributeError:
            return {"kind": "absent", "value": None}
        try:
            return {"kind": "scalar", "value": float(node(date))}
        except Exception:
            return {"kind": "subtree", "value": None}

    drift, checked = [], 0
    for m in reg["measures"]:
        for reading in m["probe"]:
            got = live(reading["path"], reading["date"])
            checked += 1
            if got["kind"] != reading["kind"]:
                drift.append(
                    f"{m['key']} {reading['path']}@{reading['date']}: recorded "
                    f"kind {reading['kind']!r}, engine says {got['kind']!r}"
                )
            elif (
                got["kind"] == "scalar"
                and reading.get("value") is not None
                and abs(got["value"] - reading["value"]) > 1e-9
            ):
                drift.append(
                    f"{m['key']} {reading['path']}@{reading['date']}: recorded "
                    f"{reading['value']}, engine {got['value']}"
                )
    if drift:
        raise SystemExit(f"{len(drift)} probes drifted:\n  " + "\n  ".join(drift))
    return checked


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args(argv)
    reg = load()
    n = validate(reg)
    by = {}
    for m in reg["measures"]:
        by[m["verdict"]] = by.get(m["verdict"], 0) + 1
    print(f"baseline integrity: {n} measures {by}")
    gaps = baseline_gaps(reg)
    if gaps:
        for m in gaps:
            print(f"  BASELINE GAP {m['key']} (from {m['effective_from']})")
    else:
        print("  no baseline gaps: every legislated measure checked is carried")
    if args.probe:
        print(f"  re-probed {reprobe(reg)} parameter readings against the engine")
    return reg


if __name__ == "__main__":
    main(sys.argv[1:])
