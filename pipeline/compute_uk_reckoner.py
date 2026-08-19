"""PE-UK counterparts to the HMRC ready reckoner (mode 2, #60).

The reckoner sibling of the OBR costings lane: HMRC's *direct effects of
illustrative tax changes* (June 2025 edition) are one-parameter reform
deltas against HMRC's indexed baseline, already ingested as external
claims by sources/hmrc-personal-tax/adapter.py. This pipeline computes
the PolicyEngine-UK static delta for each expressible measure in
data/uk/hmrc_reckoner_reforms.json on the certified populace-uk bundle.

Binding contract (same as pipeline/compute_uk_counterparts.py):
  - policyengine.py managed_microsimulation() on the certified
    populace-uk bundle, under the machine-wide sim lock:
    ``simlock -- .venv-pe/bin/python pipeline/compute_uk_reckoner.py``
  - One baseline sim per policy year, reused across measures; one reform
    sim per (measure, year). Reform parameter values are BASELINE VALUE
    PLUS DELTA read from the live parameter tree at each year — the
    registry stores deltas (absolute or relative), never absolute
    schedules, because the reckoner's own construction is
    "baseline + illustrative change".
  - Registry rows whose parameter paths fail to resolve on the engine
    are demoted to ``pe_gap`` rows: a delta is never applied to a
    guessed parameter. paths_verified: false rows MUST resolve in
    --dry-run before any sim (see the registry's
    parameter_path_verification note).
  - Emits per-run JSON artifacts (one per measure x year) and staged
    rows under the campaign ingest contract
    (results/uk/staged/reckoner.jsonl: external_claim_match descriptor
    exactly as the external rows carry it — source hmrc-personal-tax,
    program, subgroup = verbatim HMRC label — plus engine_version, full
    bundle id, status, construction, run_id, annotations).

Sign orientation: HMRC publishes magnitudes with direction in the
English label (sign_convention magnitude_with_direction_in_label; see
the adapter docstring). Staged rows therefore carry the SIGNED PE delta
(reform - baseline revenue, positive = gain to the Exchequer) plus the
registry's change_direction/section_direction annotations, and the
downstream comparison orients the external magnitude from those fields —
this pipeline never flips the external value.

Basis axis: reckoner rows for the income-tax rates are post-behavioural
(HMRC nets large behavioural offsets at the additional rate); PE deltas
are static. Every staged row carries basis: static and the comparison
inherits benchmark_class different_model. No score-like summary.

Modes:
  --dry-run   validate the registry (schema, slug rule, join against
              data/externals/hmrc-personal-tax.json) and, if
              policyengine-uk is importable, resolve every non-null
              parameter path against the live tree. No sims, no output.
  (default)   full compute; requires the managed environment.

HONESTY: this script has never been executed against a managed
policyengine.py environment — no certified populace-uk bundle exists on
the authoring machine. Everything below the engine boundary (registry
schema, join, delta arithmetic, slug rule, staged-row shape) is covered
by tests/test_reckoner_registry.py; the engine boundary itself is
unverified until the first real run, and the dry-run path-resolution
gate exists precisely so that first run cannot silently compute against
a wrong parameter.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "hmrc_reckoner_reforms.json"
EXTERNALS = ROOT / "data" / "externals" / "hmrc-personal-tax.json"
STAGED_OUT = ROOT / "results" / "uk" / "staged" / "reckoner.jsonl"
ARTIFACT_DIR = ROOT / "results" / "uk" / "reckoner"

# Reckoner forecast window: 2026-27 to 2028-29 -> PE calendar-year proxies.
YEARS = (2026, 2027, 2028)

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def slug(label):
    """Label slug for measure keys (reckoner_202506__<program>__<slug>).

    The program prefix is mandatory: HMRC prints identical change labels
    under different tax heads (VAT and IPT both carry "Change standard
    rate by 1 percentage point"), and a label-only key would join one
    reform world to two programs — the defect class the #48 review
    caught in the harvest ingest."""
    s = label.lower()
    s = re.sub(r"[£%]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:60].rstrip("_")


def load_registry(path=REGISTRY):
    return json.loads(Path(path).read_text())


def validate_registry(registry, externals_path=EXTERNALS):
    """Schema + join validation; raises with every defect listed.

    Checkable without the engine: measure_key uniqueness and slug rule,
    computability vocabulary, expressible => non-null delta dict with
    finite numeric deltas and a delta_kind, null-delta rows carry a
    note, and every (program, hmrc_label) joins an external
    revenue_effect claim verbatim — the registry may never advertise a
    measure the external side does not carry.
    """
    errors = []
    ext = json.loads(Path(externals_path).read_text())
    ext_keys = {
        (r["program"], r["subgroup"]) for r in ext if r["metric"] == "revenue_effect"
    }
    seen_keys = set()
    for m in registry["measures"]:
        k = m["measure_key"]
        if k in seen_keys:
            errors.append(f"duplicate measure_key {k}")
        seen_keys.add(k)
        if k != f"reckoner_202506__{m['program']}__{slug(m['hmrc_label'])}":
            errors.append(f"{k}: violates the slug rule for {m['hmrc_label']!r}")
        if m["computability"] not in ("expressible", "partial", "not_expressible"):
            errors.append(f"{k}: bad computability {m['computability']!r}")
        if (m["program"], m["hmrc_label"]) not in ext_keys:
            errors.append(f"{k}: no external revenue_effect claim joins it")
        deltas = m["pe_reform_delta"]
        if m["computability"] == "expressible" and not deltas:
            errors.append(f"{k}: expressible but pe_reform_delta is null")
        if m["computability"] == "not_expressible" and deltas:
            errors.append(f"{k}: not_expressible yet carries a reform delta")
        if deltas:
            if m["delta_kind"] not in ("absolute", "relative"):
                errors.append(f"{k}: delta_kind {m['delta_kind']!r}")
            for path, v in deltas.items():
                if not isinstance(v, (int, float)) or v != v or v == 0:
                    errors.append(f"{k}: non-finite/zero delta at {path}")
                if m["delta_kind"] == "relative" and abs(v) > 0.5:
                    errors.append(f"{k}: implausible relative delta {v} at {path}")
        if not deltas and m["computability"] != "expressible" and not m.get("note"):
            errors.append(f"{k}: null delta without an explanatory note")
    if errors:
        raise ValueError(
            f"registry invalid ({len(errors)} defects):\n  " + "\n  ".join(errors)
        )
    return len(registry["measures"])


def resolve_paths_or_gap(measure, parameters):
    """Split a measure's delta paths into (resolved, missing) on the live
    engine parameter tree. Bracket syntax path[i].field follows the OBR
    registry convention. Any missing path demotes the WHOLE measure to
    pe_gap — a partial application of a multi-leg delta is a different
    reform than the one the label states."""
    resolved, missing = {}, []
    for path in measure["pe_reform_delta"] or {}:
        node = parameters
        try:
            for part in re.split(r"\.(?![^\[]*\])", path):
                mbr = re.fullmatch(r"(.+)\[(\d+)\]", part)
                if mbr:
                    node = getattr(node, mbr.group(1)).brackets[int(mbr.group(2))]
                else:
                    node = getattr(node, part)
            resolved[path] = node
        except AttributeError:
            missing.append(path)
    return resolved, missing


def reform_values(measure, resolved, year):
    """Absolute reform value per path: live baseline value(year) + delta
    (absolute) or * (1 + delta) (relative). Reads the engine's own
    baseline so the delta is applied to what the certified world
    actually uses, mirroring HMRC's baseline-plus-change construction."""
    out = {}
    for path, node in resolved.items():
        # Baseline read at a single mid-year instant while the reform
        # spans the full calendar year: identical for flat-year
        # parameters (every current registry path), but a relative delta
        # on a parameter that steps mid-year would scale the 06-01 value
        # only — revisit if such a path enters the registry.
        base = float(node(f"{year}-06-01"))
        delta = measure["pe_reform_delta"][path]
        if measure["delta_kind"] == "relative":
            out[path] = base * (1.0 + delta)
        else:
            out[path] = base + delta
    return out


def staged_row(measure, year, pe_delta_gbp, status, run_id, engine_version, bundle):
    return {
        "external_claim_match": {
            "source": "hmrc-personal-tax",
            "program": measure["program"],
            "metric": "revenue_effect",
            "subgroup": measure["hmrc_label"],
            "period": f"{year}-{str(year + 1)[2:]}",
        },
        "measure_key": measure["measure_key"],
        "pe_value": pe_delta_gbp,
        "status": status,
        "construction": measure["construction"],
        "basis": "static",
        "run_id": run_id,
        "engine_version": engine_version,
        "policyengine_bundle": bundle,
        "annotations": {
            "sign_convention_external": "magnitude_with_direction_in_label",
            "change_direction": measure["change_direction"],
            "section_direction": measure["section_direction"],
            "calendar_year_proxy": f"CY {year} proxies FY {year}-{str(year + 1)[2:]}",
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--registry", default=REGISTRY, type=Path)
    args = ap.parse_args(argv)

    registry = load_registry(args.registry)
    n = validate_registry(registry)
    log(f"registry valid: {n} measures")

    try:
        import policyengine_uk  # type: ignore

        system = policyengine_uk.CountryTaxBenefitSystem()
        parameters = system.parameters
        engine = True
    except ImportError:
        parameters = None
        engine = False

    if engine:
        gaps = []
        for m in registry["measures"]:
            if not m["pe_reform_delta"]:
                continue
            _, missing = resolve_paths_or_gap(m, parameters)
            if missing:
                gaps.append((m["measure_key"], missing))
        for k, missing in gaps:
            log(f"  UNRESOLVED {k}: {missing}")
        if args.dry_run and gaps:
            raise SystemExit(
                f"{len(gaps)} measures have unresolvable parameter paths; "
                "fix the registry before computing (a delta is never applied "
                "to a guessed parameter)."
            )
    else:
        log("policyengine-uk not importable: path resolution deferred to the run")

    if args.dry_run:
        log("dry run complete: no sims, no output")
        return

    # Full compute: managed sims on the certified bundle. UNVERIFIED
    # against an installed policyengine.py — mirrors the documented
    # binding surface (see module docstring and compute_uk_counterparts).
    import policyengine as pe  # type: ignore

    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    STAGED_OUT.parent.mkdir(parents=True, exist_ok=True)
    staged = []
    for year in YEARS:
        base_sim = pe.uk.managed_microsimulation()
        bundle = str(getattr(base_sim, "policyengine_bundle", None))
        engine_version = getattr(base_sim, "engine_version", None)
        base_rev = {}
        for m in registry["measures"]:
            if m["computability"] == "not_expressible" or not m["pe_reform_delta"]:
                staged.append(
                    staged_row(m, year, None, "pe_gap", run_id, engine_version, bundle)
                )
                continue
            resolved, missing = resolve_paths_or_gap(
                m, base_sim.tax_benefit_system.parameters
            )
            if missing:
                staged.append(
                    staged_row(m, year, None, "pe_gap", run_id, engine_version, bundle)
                )
                continue
            values = reform_values(m, resolved, year)
            # All 24 expressible measures today fall in these three
            # programs; a future expressible measure elsewhere demotes to
            # pe_gap (the gap stays on the page) instead of crashing.
            head_var = {
                "income_tax": "income_tax",
                "national_insurance": "national_insurance",
                "child_benefit": "child_benefit",
            }.get(m["program"])
            if head_var is None:
                staged.append(
                    staged_row(m, year, None, "pe_gap", run_id, engine_version, bundle)
                )
                continue
            if head_var not in base_rev:
                base_rev[head_var] = float(base_sim.calculate(head_var, year).sum())
            reform = {p: {f"{year}-01-01.{year}-12-31": v} for p, v in values.items()}
            sim = pe.uk.managed_microsimulation(reform=reform)
            reform_rev = float(sim.calculate(head_var, year).sum())
            # positive = gain to the Exchequer; child benefit is spending,
            # so its Exchequer gain is the negative of the spending change
            delta = reform_rev - base_rev[head_var]
            if m["program"] == "child_benefit":
                delta = -delta
            artifact = {
                "measure_key": m["measure_key"],
                "year": year,
                "run_id": run_id,
                "reform": reform,
                "baseline_value": base_rev[head_var],
                "reform_value": reform_rev,
                "pe_delta_gbp": delta,
                "bundle": bundle,
                "engine_version": engine_version,
            }
            (ARTIFACT_DIR / f"{m['measure_key']}_{year}.json").write_text(
                json.dumps(artifact, indent=1)
            )
            staged.append(
                staged_row(m, year, delta, "ok", run_id, engine_version, bundle)
            )
            del sim
        del base_sim
        log(f"year {year} done ({len(staged)} staged rows so far)")

    with open(STAGED_OUT, "w") as f:
        for row in staged:
            f.write(json.dumps(row) + "\n")
    log(f"wrote {len(staged)} staged rows -> {STAGED_OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
