"""UK counterpart metrics on the certified populace UK artifact (#40).

The UK sibling of compute_counterparts.py, under the same binding
contract:

  - policyengine.py managed_microsimulation() on the certified
    populace-uk bundle; run under the machine-wide sim lock
    (``simlock -- .venv-pe/bin/python pipeline/compute_uk_counterparts.py``).
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
recorded in pe_uk_meta.json). A concept with no resolvable variable
emits a ``pe_gap`` row instead of crashing: the gap stays on the page,
per the scorecard status taxonomy.

Outputs:
  data/pe/pe_uk_metrics.json — {run, country, program, metric, subgroup,
                                geography, value, status}
  data/pe/pe_uk_meta.json    — bundle info + resolved-variable metadata +
                               unresolved-concept log

Not executed in CI or on unmanaged machines: requires the
policyengine.py-managed environment and the certified populace-uk
bundle. The script degrades loudly, not silently, everywhere else.
"""

import gc
import json
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "pe"
OUT.mkdir(parents=True, exist_ok=True)
YEAR = int(sys.argv[2]) if len(sys.argv) > 2 else 2025

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


# Concept -> ordered candidate variable names (first existing wins).
# Kept declarative so an engine rename is a one-line fix and the meta
# file records exactly which name served each concept.
CANDIDATES = {
    # entity keys
    "person_weight_probe": ["age"],
    # dwp_takeup counterparts (benunit-level GB benefits)
    "pension_credit": ["pension_credit"],
    "guarantee_credit": ["guarantee_credit"],
    "savings_credit": ["savings_credit"],
    "housing_benefit": ["housing_benefit"],
    # hbai counterparts
    "in_relative_poverty_bhc": ["in_relative_poverty_bhc", "in_poverty_bhc"],
    "in_relative_poverty_ahc": [
        "in_relative_poverty_ahc",
        "in_poverty_ahc",
        "in_poverty",
    ],
    "is_child": ["is_child"],
    "is_SP_age": ["is_SP_age", "is_state_pension_age", "is_pension_age"],
    "country": ["country"],
    "region": ["region", "ons_region"],
    # uk_hmrc counterparts
    "income_tax": ["income_tax"],
    "total_income": ["total_income"],
    "pays_higher_rate": ["higher_rate_earned_income_tax", "pays_higher_rate_tax"],
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
    "council_tax_benefit": ["council_tax_benefit", "council_tax_reduction"],
    "national_insurance": ["national_insurance"],
    "employer_ni": ["employer_ni", "ni_employer"],
}

# Take-up controls: PE UK take-up is parameter/seed-driven; forcing full
# participation is an input-variable override run (the
# policyengine_uk_inputs framework in the DB's ReformRef vocabulary).
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
            }
            return name
    meta["resolved"][concept] = None
    return None


def build_sim(fullpart):
    """Managed sim on the certified populace-uk bundle."""
    from policyengine import managed_microsimulation  # type: ignore

    sim = managed_microsimulation(country="uk")
    meta["runs"]["fullpart" if fullpart else "baseline"] = {
        "bundle": getattr(sim, "data_bundle", None) or getattr(sim, "dataset", None),
        "year": YEAR,
    }
    if fullpart:
        vs = sim.tax_benefit_system.variables
        for flag, value in FULLPART_OVERRIDES.items():
            if flag in vs:
                n = len(sim.calculate(flag, YEAR))
                sim.set_input(flag, YEAR, [value] * n)
                meta["fullpart_overrides_applied"].append(flag)
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
        # population denominators for downstream rate derivation
        emit(
            run_name,
            "hbai_low_income",
            f"population_{hc}",
            "total",
            "UK",
            in_pov.count() if hasattr(in_pov, "count") else len(in_pov),
        )

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
    for run_name, fullpart in (("baseline", False), ("fullpart", True)):
        compute_run(run_name, fullpart)
    (OUT / "pe_uk_metrics.json").write_text(json.dumps(rows))
    (OUT / "pe_uk_meta.json").write_text(json.dumps(meta, indent=1))
    gaps = sum(r["status"] == "pe_gap" for r in rows)
    log(f"wrote {len(rows)} rows ({gaps} pe_gap) -> {OUT}/pe_uk_metrics.json")
    if meta["unresolved"]:
        log("unresolved concepts (pe_gap rows, fix CANDIDATES or engine):")
        for u in meta["unresolved"]:
            log(f"  {u['concept']} ({u['program']})")


if __name__ == "__main__":
    main()
