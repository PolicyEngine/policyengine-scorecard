"""Validate a Budget scoreability registry (#96 for AB2026; #136 for AB2025).

data/uk/budget_2026_measures.json records what each REPORTED Budget
measure would be as a PolicyEngine-UK reform, and whether the certified
engine can express it — so that on 28 October a counterpart can be
computed immediately instead of the work starting then.
data/uk/ab2025_measures.json is the same shape for the ANNOUNCED
Autumn Budget 2025 measures and the options other producers costed for
it: the key space every AB2025 claim carries in conditions.measure_key,
and the verdict that decides whether a producer's row is compared to a
PolicyEngine number or to a `pe_gap` finding with an action_link.

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
    python pipeline/validate_budget_2026_registry.py --registry data/uk/ab2025_measures.json --resolve
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
    # past events (AB2025 registry): the measure was announced, or was an
    # option a producer costed for that Budget
    "announced",
    "option_costed_by_others",
}


def key_prefix(reg):
    """The measure_key prefix a registry's fiscal event implies.

    autumn_budget_2026 -> ab2026__ ; autumn_budget_2025 -> ab2025__ (with the
    ab2025_option__ sibling for options costed by others).
    """
    m = re.fullmatch(r"autumn_budget_(\d{4})", reg.get("fiscal_event", ""))
    if not m:
        raise ValueError(f"unrecognised fiscal_event {reg.get('fiscal_event')!r}")
    return f"ab{m.group(1)}__"


def _paths_of(m):
    """Every parameter path a measure asks the engine for."""
    return list((m.get("pe_reform_delta") or {}).keys()) + list(
        (m.get("pe_baseline_modifier") or {}).keys()
    )


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
        prefix = key_prefix(reg)
        option_prefix = prefix[:-2] + "_option__"
        if not (k.startswith(prefix) or k.startswith(option_prefix)):
            errors.append(f"{k}: measure_key must carry its fiscal event prefix")
        if m.get("reported_status") == "option_costed_by_others" and not k.startswith(
            option_prefix
        ):
            errors.append(
                f"{k}: an option costed by others carries the _option__ prefix"
            )
        if m.get("reported_status") == "announced" and not k.startswith(prefix):
            errors.append(f"{k}: an announced measure carries the plain event prefix")
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
            # v1 recorded TWO false gaps from guessed paths that failed to
            # resolve. --resolve cannot catch this class, because a
            # not_expressible entry carries no path to resolve. So the
            # claim has to be backed by a NAME SEARCH of the parameter
            # tree, not by one path that happened not to work.
            if (
                not m.get("out_of_model_scope")
                and not (m.get("name_search") or "").strip()
            ):
                errors.append(
                    f"{k}: an in-scope not_expressible verdict must record the "
                    "NAME SEARCH that proved it. A guessed path that fails to "
                    "resolve proves nothing — it is how v1 published two false "
                    "engine gaps that --resolve could not catch"
                )
            # v2 searched only the PARAMETER tree. #106 showed why that
            # is not enough: bus_subsidy_spending is a variable, and a
            # parameter-only search nearly published a false gap.
            elif not m.get("out_of_model_scope") and "VARIABLE" not in (
                m.get("name_search") or ""
            ):
                errors.append(
                    f"{k}: the name search does not say it covered VARIABLES. A "
                    "parameter-only search misses a variable — that is how #106 "
                    "nearly published a false bus gap"
                )
            if not (
                m.get("policyengine_uk_development_item") or m.get("out_of_model_scope")
            ):
                errors.append(
                    f"{k}: a not_expressible measure is either an upstream "
                    "development item or out of the model's scope; say which"
                )
            # A pe_gap row is "a finding with somewhere to go rather than a
            # blank" (hmrc_reckoner_reforms.json gap_citation_rule, gate #9):
            # every not_expressible verdict names the issue that owns it.
            if not re.match(r"https://", m.get("action_link") or ""):
                errors.append(
                    f"{k}: not_expressible without an action_link URL — a gap "
                    "with nowhere to go is a blank, not a finding"
                )
        if m["computability"] == "partial" and not (m.get("missing") or "").strip():
            errors.append(f"{k}: partial without naming the missing legs")
        if m.get("construction") == "reversal_on_certified_world" and not m.get(
            "pe_baseline_modifier"
        ):
            errors.append(
                f"{k}: a reversal_on_certified_world construction must record "
                "the pre-measure world it executes as pe_baseline_modifier"
            )

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
        for path in dict.fromkeys(_paths_of(m)):
            try:
                node = _resolve(params, path)
            except AttributeError:
                problems.append(f"{m['measure_key']}: path does not resolve: {path}")
                continue
            checked += 1
            recorded = (m.get("engine_baseline_2026") or {}).get(path)
            if isinstance(recorded, bool):
                try:
                    live = bool(node(f"{year}-06-01"))
                except Exception:
                    continue
                if live != recorded:
                    problems.append(
                        f"{m['measure_key']}: {path} baseline recorded "
                        f"{recorded}, engine says {live}"
                    )
            elif isinstance(recorded, (int, float)):
                try:
                    live = float(node(f"{year}-06-01"))
                except Exception:
                    continue
                if abs(live - recorded) > 1e-9:
                    problems.append(
                        f"{m['measure_key']}: {path} baseline recorded "
                        f"{recorded}, engine says {live}"
                    )
            elif recorded is None and path in (m.get("engine_baseline_2026") or {}):
                # null records an uncapped (inf) parameter (uncapped_sentinel)
                try:
                    live = float(node(f"{year}-06-01"))
                except Exception:
                    continue
                if live != float("inf"):
                    problems.append(
                        f"{m['measure_key']}: {path} recorded as uncapped (null), "
                        f"engine says {live}"
                    )
    if problems:
        raise SystemExit(
            f"{len(problems)} registry/engine mismatches:\n  " + "\n  ".join(problems)
        )
    return checked


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--registry", default=str(REGISTRY))
    args = ap.parse_args(argv)
    reg = load(args.registry)
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
