"""UK counterpart metrics on the certified populace UK artifact (#40).

The UK sibling of compute_counterparts.py, under the same binding
contract:

  - policyengine.py managed_microsimulation() on the certified
    populace-uk bundle; run under the machine-wide sim lock:
    ``simlock -- .venv-pe/bin/python pipeline/compute_uk_counterparts.py [YEAR]``
    (the optional single positional argument is the policy year,
    default 2025; there are no run-selection arguments — both runs
    always execute, because fullpart is only meaningful against the
    baseline computed in the same process).
  - Emits weighted COUNTS and GBP AGGREGATES only — every rate and
    delta is derived downstream in one place, never here.
  - Microsimulation + microdf auto-weighting only; never touch weight
    arrays. Cross-entity combinations via calculate(..., map_to=...).
    Subgroup cuts by boolean-array indexing of MicroSeries. Never
    multiply a MicroSeries by a plain ndarray.

Two sequential runs:
  1. baseline     — as-served artifact (calibrated take-up)
  2. fullpart     — take-up forced on for the modeled benefits, giving
                    the entitled-population denominators the DWP
                    take-up counterparts need (recipients / entitled)

The fullpart run sets its input overrides BEFORE any calculate on that
sim, at each flag's own definition period (monthly flags get all twelve
months, with an eternity fallback), and then verifies the override took:
post-set means are recorded in pe_uk_meta.json, and the run aborts if no
override applied, if no applied override reads back as on, or if the
resulting series are identical to baseline. A silently no-op fullpart run
would make every DWP take-up denominator the baseline caseload while
still reading ``status: "ok"``, so it is a hard failure, not a warning.

Counterpart coverage maps to the ingested UK external lanes:
  - dwp_takeup:  pension credit / guarantee credit / HB (pension-age)
                 benefit-unit caseloads + GBP totals, baseline and
                 fullpart, GB-restricted
  - dwp_hbai:    persons below 60% median BHC/AHC, relative, by age
                 group and country/region (single policy year; the
                 3-year-average construction is downstream)
  - uk_hmrc:     taxpayer counts by marginal band + income tax
                 liability aggregates
  - obr:         GBP expenditure per modeled benefit line
  - ukmod:       caseloads + expenditure for the shared instruments

Variable-name drift is expected across engine versions, so every
concept resolves through CANDIDATES (first existing variable wins,
recorded in pe_uk_meta.json). A candidate list holds only genuine
synonyms of one concept — never a near-neighbour of a different
concept, which would emit a wrong-concept value under ``status: "ok"``.
A concept with no resolvable variable emits a ``pe_gap`` row instead of
crashing: the gap stays on the page, per the scorecard status taxonomy.
Likewise a population denominator whose weighted count is unavailable
emits ``pe_gap``; an unweighted record count is never emitted as if it
were weighted.

Not executed in CI or on unmanaged machines: requires the
policyengine.py-managed environment and the certified populace-uk
bundle. Still unverified until that first real run, and knowingly so:
(a) the engine entry point — ``pe.uk.managed_microsimulation()`` mirrors
the documented US surface but has not been called against an installed
policyengine.py; (b) which CANDIDATES names actually exist in
policyengine-uk, and so how many concepts land as ``pe_gap``; (c)
whether the FULLPART_OVERRIDES input variables exist at all — UK take-up
is parameter/seed-driven, so if they do not, the fullpart run will abort
loudly and the take-up lane needs a parametric reform instead of an
input override. Everything below the engine boundary (registries, row
shapes, argv parsing, the denominator path) is covered by
tests/test_uk_pipeline_registry.py.
"""

import gc
import json
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "pe"
OUT.mkdir(parents=True, exist_ok=True)
# Overridden from argv in main() — module import stays side-effect-free
# so the registries are testable without the engine.
YEAR = 2025

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


# Concept -> ordered candidate variable names (first existing wins).
# Kept declarative so an engine rename is a one-line fix and the meta
# file records exactly which name served each concept.
#
# INVARIANT: every name in a list must be a genuine synonym for that
# concept in some engine version — a rename, a case variant, or a
# historic name for the same instrument. A "close enough" variable of a
# different concept (e.g. generic in_poverty standing in for an AHC
# measure, or a GBP amount standing in for a boolean flag) is a silent
# wrong-concept emission and is banned; the concept must go pe_gap
# instead. Enforced by tests/test_uk_pipeline_registry.py.
CANDIDATES = {
    # entity keys
    "person_weight_probe": ["age"],
    # dwp_takeup counterparts (benunit-level GB benefits)
    "pension_credit": ["pension_credit"],
    "guarantee_credit": ["guarantee_credit"],
    "savings_credit": ["savings_credit"],
    "housing_benefit": ["housing_benefit"],
    # hbai counterparts
    # BHC/AHC are distinct concepts: HBAI's headline relative low-income
    # measures differ by ~4pp of children between them. Neither list may
    # fall back to the other, nor to a housing-cost-agnostic in_poverty.
    "in_relative_poverty_bhc": ["in_relative_poverty_bhc", "in_poverty_bhc"],
    "in_relative_poverty_ahc": ["in_relative_poverty_ahc", "in_poverty_ahc"],
    "is_child": ["is_child"],
    "is_SP_age": ["is_SP_age", "is_state_pension_age", "is_pension_age"],
    "country": ["country"],
    "region": ["region", "ons_region"],
    # uk_hmrc counterparts
    "income_tax": ["income_tax"],
    "total_income": ["total_income"],
    # boolean "is a higher-rate taxpayer" only; higher_rate_earned_income_tax
    # is a GBP amount, a different concept, so it is not a candidate here.
    "pays_higher_rate": ["pays_higher_rate_tax", "is_higher_rate_taxpayer"],
    "marginal_tax_rate_band": ["tax_band", "marginal_tax_rate_band"],
    # obr / ukmod counterparts (household or benunit GBP aggregates)
    "universal_credit": ["universal_credit"],
    "child_benefit": ["child_benefit"],
    "state_pension": ["state_pension"],
    "dla": ["dla"],
    "pip": ["pip"],
    "attendance_allowance": ["attendance_allowance"],
    "carers_allowance": ["carers_allowance"],
    "esa_income": ["esa_income", "ESA_income"],
    "jsa": ["jsa", "JSA"],
    "winter_fuel_allowance": ["winter_fuel_allowance"],
    # council tax benefit was replaced by council tax reduction in 2013;
    # same instrument, so these are genuine synonyms.
    "council_tax_benefit": ["council_tax_benefit", "council_tax_reduction"],
    "national_insurance": ["national_insurance"],
    "employer_ni": ["employer_ni", "ni_employer"],
}

# Take-up controls: PE UK take-up is parameter/seed-driven; forcing full
# participation is an input-variable override run (the
# policyengine_uk_inputs framework in the DB's ReformRef vocabulary).
# Whether these input variables exist in policyengine-uk at all is
# UNVERIFIED (see module docstring); build_sim aborts loudly rather than
# emitting a fullpart series identical to baseline if they do not.
FULLPART_OVERRIDES = {
    # input flag candidates -> forced value
    "takes_up_pension_credit": True,
    "takes_up_housing_benefit": True,
    "takes_up_universal_credit": True,
    "takes_up_child_benefit": True,
    "takes_up_council_tax_reduction": True,
}

# (program, concept, entity_kind, geography restriction)
BENEFIT_LINES = [
    ("pension_credit", "pension_credit", "benunit", "GB"),
    ("guarantee_credit", "guarantee_credit", "benunit", "GB"),
    ("savings_credit", "savings_credit", "benunit", "GB"),
    ("housing_benefit", "housing_benefit", "benunit", "GB"),
    ("universal_credit", "universal_credit", "benunit", "GB"),
    ("child_benefit", "child_benefit", "benunit", "UK"),
    ("state_pension", "state_pension", "person", "GB"),
    ("dla", "dla", "person", "GB"),
    ("pip", "pip", "person", "GB"),
    ("attendance_allowance", "attendance_allowance", "person", "GB"),
    ("carers_allowance", "carers_allowance", "person", "GB"),
    ("esa_income", "esa_income", "person", "GB"),
    ("jsa", "jsa", "person", "GB"),
    ("winter_fuel_allowance", "winter_fuel_allowance", "benunit", "GB"),
    ("council_tax_reduction", "council_tax_benefit", "benunit", "GB"),
]

# Metrics whose fullpart values must move when take-up is forced on.
TAKEUP_SENSITIVE_METRICS = ("recipient_count", "benefit_spending")

rows = []
meta = {
    "year": YEAR,
    "runs": {},
    "resolved": {},
    "unresolved": [],
    "fullpart_overrides_applied": [],
}


def emit(run, program, metric, subgroup, geo, value, status="ok"):
    rows.append(
        {
            "run": run,
            "country": "UK",
            "program": program,
            "metric": metric,
            "subgroup": subgroup,
            "geography": geo,
            "value": None if value is None else float(value),
            "status": status,
        }
    )


def pe_gap(run, program, metric, subgroup, geo, concept):
    meta["unresolved"].append({"concept": concept, "program": program})
    emit(run, program, metric, subgroup, geo, None, status="pe_gap")


def resolve(vs, concept):
    """First existing candidate variable for a concept, else None."""
    if concept in meta["resolved"]:
        return meta["resolved"][concept]
    for name in CANDIDATES[concept]:
        if name in vs:
            v = vs[name]
            meta["resolved"][concept] = name
            meta.setdefault("variables", {})[name] = {
                "label": getattr(v, "label", None),
                "entity": v.entity.key,
                "definition_period": str(getattr(v, "definition_period", None)),
            }
            return name
    meta["resolved"][concept] = None
    return None


def parse_year(argv, default=2025):
    """Policy year from the single positional argument.

    ``compute_uk_counterparts.py 2026`` -> 2026. Unlike the US script,
    which takes a run-selection list at argv[1] and the year at argv[2],
    this one has no run selection, so the year is argv[1].
    """
    if len(argv) > 1 and argv[1].strip():
        return int(argv[1])
    return default


def periods_for(variable, year):
    """Periods to set an input over, from the variable's own definition
    period — a monthly flag set only at the year period silently fails to
    override the months the engine actually reads."""
    period = str(getattr(variable, "definition_period", "") or "").lower()
    if period in ("month", "monthly"):
        return [f"{year}-{m:02d}" for m in range(1, 13)], "12 months"
    if period == "eternity":
        return ["eternity"], "eternity"
    return [year], "year"


def weighted_population(series):
    """Weighted record count of a MicroSeries, or None.

    microdf's MicroSeries.count() returns the sum of weights. A plain
    pandas Series / ndarray also answers to len() and sometimes count(),
    but those are UNWEIGHTED record counts (~10^5 for a UK survey) and
    must never be emitted as a population denominator. Returning None
    forces the caller onto the pe_gap path.
    """
    if getattr(series, "weights", None) is None:
        return None
    counter = getattr(series, "count", None)
    if not callable(counter):
        return None
    return float(counter())


def emit_population_denominator(run_name, hc, series):
    """Population denominator for the HBAI rate derivation, or a pe_gap.

    Never emits an unweighted count under status "ok"."""
    n = weighted_population(series)
    if n is None:
        log(
            f"  WARNING: no weighted count for population_{hc} "
            f"({type(series).__name__} is not a weighted MicroSeries) -> pe_gap"
        )
        pe_gap(
            run_name,
            "hbai_low_income",
            f"population_{hc}",
            "total",
            "UK",
            "weighted_population",
        )
        return None
    emit(run_name, "hbai_low_income", f"population_{hc}", "total", "UK", n)
    return n


def build_sim(fullpart, year=None):
    """Managed sim on the certified populace-uk bundle.

    For the fullpart run, every override is set BEFORE any calculate on
    this sim (a calculate first would cache baseline take-up and the
    override would silently do nothing), then read back to confirm it
    took effect.
    """
    year = YEAR if year is None else year
    # UNVERIFIED against an installed engine: mirrors the documented
    # binding surface used by compute_counterparts.py
    # (pe.us.managed_microsimulation()) and docs/ARCHITECTURE.md. If the
    # UK accessor turns out to be spelled differently, this is the line
    # that changes — do not silently swap in a bare country-package
    # Microsimulation, which is a different (uncertified) world.
    import policyengine as pe  # type: ignore

    sim = pe.uk.managed_microsimulation()
    run_name = "fullpart" if fullpart else "baseline"
    run_meta = {
        "bundle": getattr(sim, "data_bundle", None) or getattr(sim, "dataset", None),
        "year": year,
    }
    meta["runs"][run_name] = run_meta
    if not fullpart:
        return sim

    vs = sim.tax_benefit_system.variables
    run_meta.update({"flags_set_true": [], "flags_missing": [], "flags_failed": []})
    for flag, value in FULLPART_OVERRIDES.items():
        if flag not in vs:
            run_meta["flags_missing"].append(flag)
            log(f"  WARNING: override flag {flag} not in variables")
            continue
        entity = vs[flag].entity.key
        n = sim.populations[entity].count  # entity population, NOT a calculate()
        arr = [value] * n
        periods, label = periods_for(vs[flag], year)
        try:
            for p in periods:
                sim.set_input(flag, p, arr)
            run_meta["flags_set_true"].append(f"{flag} ({label})")
        except Exception as e:
            log(f"  set_input({flag}, {label}) failed: {e}; trying eternity")
            try:
                sim.set_input(flag, "eternity", arr)
                run_meta["flags_set_true"].append(f"{flag} (eternity)")
            except Exception as e2:
                log(f"  ERROR setting {flag}: {e2}")
                run_meta["flags_failed"].append(flag)

    meta["fullpart_overrides_applied"] = [
        f.split(" ")[0] for f in run_meta["flags_set_true"]
    ]
    if not meta["fullpart_overrides_applied"]:
        raise RuntimeError(
            "fullpart run applied NO take-up override "
            f"(missing={run_meta['flags_missing']}, "
            f"failed={run_meta['flags_failed']}). Without an override the "
            "fullpart series equals baseline and every DWP take-up "
            "denominator would silently be the baseline caseload. UK "
            "take-up may be parameter-driven rather than input-driven: fix "
            "FULLPART_OVERRIDES or express full take-up as a reform."
        )

    # Verify the toggle took: read each applied flag back at its own period.
    run_meta["flag_means_after"] = {}
    for flag in meta["fullpart_overrides_applied"]:
        periods, _ = periods_for(vs[flag], year)
        try:
            probe = periods[len(periods) // 2]
            got = sim.calculate(flag, probe)
            values = getattr(got, "values", got)
            run_meta["flag_means_after"][flag] = float(
                sum(float(x) for x in values) / max(len(values), 1)
            )
        except Exception as e:
            log(f"  WARNING: could not read back {flag}: {e}")
            run_meta["flag_means_after"][flag] = None
    log(f"  flag means after set: {run_meta['flag_means_after']}")
    on = [
        f for f, m in run_meta["flag_means_after"].items() if m is not None and m > 0.99
    ]
    run_meta["flags_verified_on"] = on
    if not on:
        raise RuntimeError(
            "fullpart run set overrides but none reads back as on "
            f"({run_meta['flag_means_after']}). The override is a no-op and "
            "fullpart would be identical to baseline."
        )
    if len(on) < len(meta["fullpart_overrides_applied"]):
        log(
            f"  WARNING: overrides that did not read back on: "
            f"{sorted(set(meta['fullpart_overrides_applied']) - set(on))}"
        )
    return sim


def geo_masks(sim, vs):
    """Country masks at each entity level via map_to; GB = not NI."""
    name = resolve(vs, "country")
    masks = {}
    if name is None:
        return masks
    for entity in ("person", "benunit", "household"):
        c = sim.calculate(name, YEAR, map_to=entity)
        arr = getattr(c, "values", c)
        masks[entity] = {
            "UK": arr == arr,  # all-true
            "GB": arr != "NORTHERN_IRELAND",
            "NI": arr == "NORTHERN_IRELAND",
        }
    return masks


def assert_fullpart_moved(baseline_rows, fullpart_rows):
    """Fail loudly if forcing take-up on changed nothing.

    Every DWP take-up counterpart divides recipients by the fullpart
    entitled caseload; if fullpart == baseline the denominator is the
    baseline caseload and every take-up rate silently comes out at 100%
    while every row still reads status "ok".
    """

    def key(r):
        return (r["program"], r["metric"], r["subgroup"], r["geography"])

    base = {
        key(r): r["value"]
        for r in baseline_rows
        if r["status"] == "ok" and r["metric"] in TAKEUP_SENSITIVE_METRICS
    }
    compared = moved = 0
    for r in fullpart_rows:
        if r["status"] != "ok" or r["metric"] not in TAKEUP_SENSITIVE_METRICS:
            continue
        if key(r) not in base:
            continue
        compared += 1
        if r["value"] != base[key(r)]:
            moved += 1
    meta["fullpart_moved"] = {"compared": compared, "moved": moved}
    log(f"fullpart vs baseline: {moved}/{compared} take-up-sensitive values moved")
    if compared and not moved:
        raise RuntimeError(
            f"fullpart is byte-identical to baseline across all {compared} "
            "take-up-sensitive values: the overrides applied and read back on, "
            "but changed no benefit. Every DWP take-up denominator would be the "
            "baseline caseload. Do not publish this run."
        )
    if not compared:
        raise RuntimeError(
            "no take-up-sensitive values were comparable between baseline and "
            "fullpart (all pe_gap?) — nothing verifies the fullpart run."
        )


def compute_run(run_name, fullpart):
    log(f"building {run_name} sim")
    sim = build_sim(fullpart)
    vs = sim.tax_benefit_system.variables
    masks = geo_masks(sim, vs)

    def weighted(concept, entity, geo, kind, program, metric, subgroup="total"):
        name = resolve(vs, concept)
        if name is None:
            pe_gap(run_name, program, metric, subgroup, geo, concept)
            return
        series = sim.calculate(name, YEAR, map_to=entity)
        mask = masks.get(entity, {}).get(geo)
        if mask is not None:
            series = series[mask]
        if kind == "sum":
            emit(run_name, program, metric, subgroup, geo, series.sum())
        elif kind == "count_positive":
            emit(run_name, program, metric, subgroup, geo, (series > 0).sum())
        else:
            raise ValueError(kind)

    # benefit caseloads + expenditure (dwp_takeup / obr / ukmod)
    for program, concept, entity, geo in BENEFIT_LINES:
        weighted(concept, entity, geo, "count_positive", program, "recipient_count")
        weighted(concept, entity, geo, "sum", program, "benefit_spending")

    # hbai poverty counterparts: persons in relative poverty, BHC and AHC,
    # by age group and by country (region cuts follow once the base
    # concept is validated against HBAI's published UK rows)
    for hc, concept in (
        ("bhc", "in_relative_poverty_bhc"),
        ("ahc", "in_relative_poverty_ahc"),
    ):
        pov = resolve(vs, concept)
        if pov is None:
            pe_gap(
                run_name,
                "hbai_low_income",
                f"poverty_count_{hc}",
                "total",
                "UK",
                concept,
            )
            continue
        in_pov = sim.calculate(pov, YEAR, map_to="person")
        emit(
            run_name,
            "hbai_low_income",
            f"poverty_count_{hc}",
            "total",
            "UK",
            in_pov.sum(),
        )
        for subgroup, mask_concept in (
            ("children", "is_child"),
            ("pensioners", "is_SP_age"),
        ):
            mname = resolve(vs, mask_concept)
            if mname is None:
                pe_gap(
                    run_name,
                    "hbai_low_income",
                    f"poverty_count_{hc}",
                    subgroup,
                    "UK",
                    mask_concept,
                )
                continue
            m = sim.calculate(mname, YEAR, map_to="person")
            arr = getattr(m, "values", m).astype(bool)
            emit(
                run_name,
                "hbai_low_income",
                f"poverty_count_{hc}",
                subgroup,
                "UK",
                in_pov[arr].sum(),
            )
        # population denominator for downstream rate derivation —
        # weighted or pe_gap, never an unweighted record count
        emit_population_denominator(run_name, hc, in_pov)

    # uk_hmrc counterparts: taxpayer counts + liability aggregate
    weighted(
        "income_tax", "person", "UK", "count_positive", "income_tax", "taxpayer_count"
    )
    weighted("income_tax", "person", "UK", "sum", "income_tax", "tax_liability")
    weighted(
        "national_insurance",
        "person",
        "UK",
        "sum",
        "national_insurance",
        "tax_liability",
    )

    del sim
    gc.collect()
    log(f"{run_name} done: {len(rows)} rows so far")


def main():
    global YEAR
    YEAR = parse_year(sys.argv)
    meta["year"] = YEAR
    log(f"policy year {YEAR}")
    per_run = {}
    for run_name, fullpart in (("baseline", False), ("fullpart", True)):
        start = len(rows)
        compute_run(run_name, fullpart)
        per_run[run_name] = rows[start:]
    assert_fullpart_moved(per_run["baseline"], per_run["fullpart"])
    (OUT / "pe_uk_metrics.json").write_text(json.dumps(rows))
    (OUT / "pe_uk_meta.json").write_text(json.dumps(meta, indent=1, default=str))
    gaps = sum(r["status"] == "pe_gap" for r in rows)
    log(f"wrote {len(rows)} rows ({gaps} pe_gap) -> {OUT}/pe_uk_metrics.json")
    if meta["unresolved"]:
        log("unresolved concepts (pe_gap rows, fix CANDIDATES or engine):")
        for u in meta["unresolved"]:
            log(f"  {u['concept']} ({u['program']})")


if __name__ == "__main__":
    main()
