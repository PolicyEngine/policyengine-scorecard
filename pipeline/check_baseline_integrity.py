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
VERDICTS = {"carried", "consistent", "missing"}


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
        # A `consistent` verdict is the one that could hide a defect, so it
        # carries the heaviest evidence requirement.
        if m["verdict"] == "consistent" and len(m.get("evidence", "")) < 200:
            errors.append(
                f"{k}: a 'consistent' verdict needs the evidence spelled out — "
                "it is the verdict that could be wishful thinking"
            )
        if m["verdict"] == "missing":
            if not m.get("affected_from_period"):
                errors.append(f"{k}: missing verdict without affected_from_period")
            if not str(m.get("consequence") or "").strip():
                errors.append(
                    f"{k}: a missing measure must say WHICH claims it affects; "
                    "an unlocated gap cannot be caveated"
                )
    if errors:
        raise ValueError(
            f"registry invalid ({len(errors)} defects):\n  " + "\n  ".join(errors)
        )
    return len(reg["measures"])


def affected_claims(reg, db_path=None):
    """UK claims at or beyond a missing measure's effective period.

    This is an EXPOSURE ENVELOPE, not a defect count. A claim inside it
    is computed at a horizon where the certified world is missing law
    that exists; whether that actually moves the claim depends on the
    quantity — a council-tax surcharge does not touch a taxpayer count.
    The envelope is what has to be triaged, and the point is that it is
    currently neither triaged nor visible.
    """
    db_path = db_path or ROOT / "data" / "scorecard.db"
    if not Path(db_path).exists():
        return None
    import sqlite3

    conn = sqlite3.connect(db_path)
    out = {}
    for m in reg["measures"]:
        if m["verdict"] != "missing":
            continue
        n = conn.execute(
            "SELECT COUNT(*) FROM external_scores"
            " WHERE IFNULL(json_extract(conditions,'$.country'),'US')='UK'"
            "   AND period >= ?",
            (m["affected_from_period"],),
        ).fetchone()[0]
        out[m["key"]] = {"from_period": m["affected_from_period"], "uk_claims": n}
    conn.close()
    return out


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

    A registry that says `missing` about a parameter that now resolves is
    good news that must not go unnoticed — the caveat should come off.
    A registry that says `carried` about one that no longer does is a
    regression.
    """
    import importlib.metadata

    import policyengine_uk

    pin = reg["engine_pin"]["policyengine_uk"]
    installed = importlib.metadata.version("policyengine-uk")
    if installed != pin:
        raise SystemExit(f"policyengine-uk {installed} installed, pinned {pin}")

    params = policyengine_uk.CountryTaxBenefitSystem().parameters
    drift = []
    for m in reg["measures"]:
        for year, recorded in m["probe"].items():
            try:
                live = float(_resolve(params, m["parameter"])(f"{year}-06-01"))
            except Exception:
                live = None
            if recorded is None and live is not None:
                drift.append(
                    f"{m['key']} @{year}: recorded MISSING but now resolves to "
                    f"{live} — the caveat may be removable"
                )
            elif recorded is not None and live is None:
                drift.append(
                    f"{m['key']} @{year}: recorded {recorded} but no longer "
                    "resolves — regression"
                )
            elif (
                recorded is not None
                and live is not None
                and abs(live - recorded) > 1e-9
            ):
                drift.append(f"{m['key']} @{year}: recorded {recorded}, engine {live}")
    if drift:
        raise SystemExit(
            f"{len(drift)} baseline probes drifted:\n  " + "\n  ".join(drift)
        )
    return sum(len(m["probe"]) for m in reg["measures"])


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
    affected = affected_claims(reg)
    if affected:
        for key, info in affected.items():
            print(
                f"  MISSING {key}: {info['uk_claims']} UK claims sit at or "
                f"beyond {info['from_period']} — the exposure envelope to "
                "triage, not a defect count"
            )
    if args.probe:
        print(f"  re-probed {reprobe(reg)} parameter readings against the engine")
    return reg


if __name__ == "__main__":
    main(sys.argv[1:])
