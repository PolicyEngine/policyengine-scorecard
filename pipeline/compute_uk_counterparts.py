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
override applied, if no applied override reads back as on, or if any
take-up-validated benefit's sensitive series are identical to baseline.
The movement check is PER BENEFIT — universal credit moving must never
bless an unchanged pension credit caseload, because each benefit's
fullpart series is its own DWP take-up denominator; one benefit's silent
no-op is the silent-100%-take-up failure class regardless of what the
others did. So it is a per-benefit hard failure, not a warning.

Counterpart coverage maps to the ingested UK external lanes:
  - dwp_takeup:  pension credit / guarantee credit / savings credit
                 benefit-unit caseloads + GBP totals, and pension-age
                 housing benefit as its own program
                 (housing_benefit_pensioners, the DWP external program
                 id) — never the unrestricted HB total under that label;
                 baseline and fullpart, GB-restricted
  - dwp_hbai:    persons below 60% median BHC/AHC, relative, by age
                 group, each numerator with its own matching population
                 denominator (total, children, pensioners) so every
                 published cut has a rate derivation (single policy
                 year; the 3-year-average construction is downstream)
  - uk_hmrc:     taxpayer counts + income tax liability, total and by
                 marginal band (basic/higher/additional — the external
                 adapter's subgroup vocabulary); a band that cannot be
                 resolved emits pe_gap, never an all-taxpayer aggregate
                 under a band label
  - obr:         GBP expenditure per modeled benefit line
  - ukmod:       caseloads + expenditure for the shared instruments

Geography: country is a household-level enum, and household-enum
projection to group entities crashes in core, so masks are built from
the person-level projection and anchored to each group entity via its
first person member — the same rule compute_counterparts.py uses for US
states. A geography-restricted line whose entity has no country anchor
emits pe_gap: an unrestricted total is never emitted under a GB/NI
label.

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

Where the outputs live, decided deliberately (post-#74). The two
artifacts land in data/pe/ — pe_uk_metrics.json and pe_uk_meta.json —
alongside the US pe_metrics.json / pe_meta.json that are already tracked
there. They are RUN OUTPUTS, not derived build artifacts: the operator
commits them from the managed environment, and a later build reads them
as an input, exactly the relationship sources/campaign-20260802/uk_runs/
already has with the campaign ingest. They are therefore tracked, and
their first creation is a normal commit rather than something the
no-drift gate has to be taught about (the gate compares a build against
HEAD; an untracked new file would have slipped past it silently).

The ingest that reads pe_uk_metrics.json into the DB lands with the
first real run (#76), because it needs that run's actual gap set to
build its claim attachments. Until then nothing imports these rows, and
that is why every gap here is CITED at emission (see GAP_REASONS): the
exporter only surfaces claims that already have a DB result, so an
uncited gap would vanish rather than stay on the page.

Not executed in CI or on unmanaged machines: requires the
policyengine.py-managed environment and the certified populace-uk
bundle. Still unverified until that first real run, and knowingly so:
(a) the engine entry point — ``pe.uk.managed_microsimulation()`` mirrors
the documented US surface but has not been called against an installed
policyengine.py; (b) which CANDIDATES names actually exist in
policyengine-uk, and so how many concepts land as ``pe_gap``. The
FULLPART_OVERRIDES names are no longer in that list: they are the
``would_claim_*`` / ``claims_all_entitled_benefits`` inputs the compute
campaign's fulltakeup runs used successfully against this engine.
Everything below the engine boundary (registries, row shapes, argv
parsing, the denominator path, the geography-restriction refusal, the
per-benefit movement contract) is covered by
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
    # the PC claim flag: take-up lives on the AGGREGATE, so the component
    # series have to be gated on it explicitly
    "would_claim_pc": ["would_claim_pc"],
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
    # uk_hmrc counterparts. Every concept declared here is emitted (as a
    # value or a pe_gap) — no declared-but-unused advertisement. Band
    # cuts are boolean marginal-band flags matching the external
    # adapter's subgroup vocabulary (basic/higher/additional); a GBP
    # amount like higher_rate_earned_income_tax is a different concept
    # and is banned as a candidate.
    "income_tax": ["income_tax"],
    # The certified engine exposes a `tax_band` ENUM, not three boolean
    # band flags — none of pays_*_rate_tax / is_*_rate_taxpayer exists at
    # this pin, so the band cuts guaranteed three uncited gaps every run.
    # The enum is the primary resolution; the booleans stay only as
    # forward/backward-compatible fallbacks for engines that do expose
    # them.
    "tax_band": ["tax_band"],
    "pays_basic_rate": ["pays_basic_rate_tax", "is_basic_rate_taxpayer"],
    "pays_higher_rate": ["pays_higher_rate_tax", "is_higher_rate_taxpayer"],
    "pays_additional_rate": [
        "pays_additional_rate_tax",
        "is_additional_rate_taxpayer",
    ],
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

# Take-up controls: forcing full participation is an input-variable
# override run (the policyengine_uk_inputs framework in the DB's
# ReformRef vocabulary). These are the engine's actual take-up inputs —
# the set the compute campaign's fulltakeup runs used successfully
# (would_claim_* per benefit plus the global claims_all_entitled_benefits
# switch), not guessed takes_up_* names. build_sim still aborts loudly
# rather than emitting a fullpart series identical to baseline if none
# applies, and assert_fullpart_moved enforces movement per benefit.
FULLPART_OVERRIDES = {
    # engine input flag -> forced value
    "would_claim_pc": True,
    "would_claim_housing_benefit": True,
    "would_claim_uc": True,
    "would_claim_child_benefit": True,
    "claims_all_entitled_benefits": True,
}

# Benefits whose ENTITLED population the combined fullpart world cannot
# express, with the gap reason each is emitted under.
#
# Housing Benefit is the case the round-2 engine read found. In pinned
# 2.89.2, housing_benefit_eligible requires BOTH ~would_claim_uc (the
# UC/legacy mutual exclusion — there is an engine regression test for
# exactly this) and housing_benefit_reported > 0. Eligibility is
# therefore RECEIPT-gated: a take-up world cannot create entitled
# non-recipients for HB, and forcing all five flags on drives HB toward
# ZERO rather than toward all-entitled. Emitting those rows as `ok`
# would publish a take-up denominator smaller than its numerator.
#
# So HB's fullpart rows are a CITED GAP, not a number. The baseline rows
# are unaffected — HB as a level is fine; it is the entitled-population
# construction that the engine cannot express today.
FULLPART_UNEXPRESSIBLE = {
    "housing_benefit": "housing_benefit_receipt_gated",
    "housing_benefit_pensioners": "housing_benefit_receipt_gated",
}

# (program, concept, entity_kind, geography restriction)
# Entity levels follow the engine's own variable entities: ESA/JSA are
# benefit-unit variables and winter fuel is household-level — mapping
# them to a lower entity projects awards onto every member and
# overcounts recipients.
BENEFIT_LINES = [
    ("pension_credit", "pension_credit", "benunit", "GB"),
    # NOTE: guarantee_credit and savings_credit are NOT plain lines. See
    # PC_COMPONENT_LINES — the engine's raw components are entitlement
    # quantities that never consult would_claim_pc, while DWP publishes
    # CLAIMED guarantee credit and savings-credit-only.
    ("housing_benefit", "housing_benefit", "benunit", "GB"),
    ("universal_credit", "universal_credit", "benunit", "GB"),
    ("child_benefit", "child_benefit", "benunit", "UK"),
    ("state_pension", "state_pension", "person", "GB"),
    ("dla", "dla", "person", "GB"),
    ("pip", "pip", "person", "GB"),
    ("attendance_allowance", "attendance_allowance", "person", "GB"),
    ("carers_allowance", "carers_allowance", "person", "GB"),
    ("esa_income", "esa_income", "benunit", "GB"),
    ("jsa", "jsa", "benunit", "GB"),
    ("winter_fuel_allowance", "winter_fuel_allowance", "household", "GB"),
    ("council_tax_reduction", "council_tax_benefit", "benunit", "GB"),
]

# Pension Credit components, as DWP defines them — not as the engine's
# raw component variables.
#
# Round-2 engine read: `guarantee_credit` and `savings_credit` are
# ENTITLEMENT components and never consult `would_claim_pc`; the only
# reference to that flag is in pension_credit.py, on the aggregate. So
# emitting the raw components as recipient counts published a
# wrong-concept value under status "ok" — an entitlement caseload
# labelled as a claimed one — and under a `savings_credit` slug the
# closed external registry does not even recognise.
#
# DWP's two published series are:
#   guarantee_credit      benefit units RECEIVING guarantee credit
#   savings_credit_only   benefit units receiving savings credit and NOT
#                         guarantee credit (sources/dwp-takeup/adapter.py
#                         line 88: the series additionally requires
#                         guarantee_credit == 0)
# Both are gated on the PC claim flag, which is where take-up lives.
# (program, component concept, entity, geo, exclude-if-positive concept)
PC_COMPONENT_LINES = [
    ("guarantee_credit", "guarantee_credit", "benunit", "GB", None),
    ("savings_credit_only", "savings_credit", "benunit", "GB", "guarantee_credit"),
]
PC_CLAIM_FLAG = "would_claim_pc"

# DWP take-up advertises pension-age housing benefit under its own
# external program id (housing_benefit_pensioners, per
# sources/dwp-takeup/adapter.py TITLE_PROGRAMS) — a pension-age benunit
# cut of HB, emitted alongside (never instead of) the unrestricted
# housing_benefit total that serves the obr/ukmod expenditure lanes.
PENSION_AGE_HB_LINE = ("housing_benefit_pensioners", "housing_benefit", "benunit", "GB")

# HMRC marginal-band cuts: external subgroup id -> (tax_band enum value,
# fallback boolean concept). The external subgroup vocabulary comes from
# sources/hmrc-personal-tax/adapter.py; the enum values are the engine's
# own tax_band names. Resolution order is enum first, boolean second —
# the boolean variables do not exist in the certified engine, so leading
# with them guaranteed three uncited band gaps on every run.
HMRC_BAND_CUTS = [
    ("basic_rate", "BASIC", "pays_basic_rate"),
    ("higher_rate", "HIGHER", "pays_higher_rate"),
    ("additional_rate", "ADDITIONAL", "pays_additional_rate"),
]

# (program, metric) -> (external source id, unit concept). The closed UK
# registry keeps DWP benefit_units distinct from UKMOD families and knows
# only savings_credit_only (never a bare savings_credit), so a row that
# does not say which lane it answers cannot be attached to anything.
_DWP_BU = ("dwp_takeup", "benefit_units")
_OBR_GBP = ("obr", "gbp_nominal")
_UKMOD_BU = ("ukmod", "families")
ROW_IDENTITY = {}
for _p in (
    "pension_credit",
    "guarantee_credit",
    "savings_credit_only",
    "housing_benefit_pensioners",
):
    ROW_IDENTITY[(_p, "recipient_count")] = _DWP_BU
    ROW_IDENTITY[(_p, "benefit_spending")] = ("dwp_takeup", "gbp_nominal")
for _p in (
    "housing_benefit",
    "universal_credit",
    "child_benefit",
    "state_pension",
    "dla",
    "pip",
    "attendance_allowance",
    "carers_allowance",
    "esa_income",
    "jsa",
    "winter_fuel_allowance",
    "council_tax_reduction",
):
    # The expenditure lanes: OBR publishes the spending line, UKMOD the
    # caseload in ITS OWN family unit — never the DWP benefit unit.
    ROW_IDENTITY[(_p, "benefit_spending")] = _OBR_GBP
    ROW_IDENTITY[(_p, "recipient_count")] = _UKMOD_BU
for _hc in ("bhc", "ahc"):
    ROW_IDENTITY[("hbai_low_income", f"poverty_count_{_hc}")] = ("dwp_hbai", "persons")
    ROW_IDENTITY[("hbai_low_income", f"population_{_hc}")] = ("dwp_hbai", "persons")
ROW_IDENTITY[("income_tax", "taxpayer_count")] = ("uk_hmrc", "individuals")
ROW_IDENTITY[("income_tax", "tax_liability")] = ("uk_hmrc", "gbp_nominal")
ROW_IDENTITY[("national_insurance", "tax_liability")] = ("uk_hmrc", "gbp_nominal")

# Metrics whose fullpart values must move when take-up is forced on.
TAKEUP_SENSITIVE_METRICS = ("recipient_count", "benefit_spending")

# Forcing take-up ON can only ever ADD recipients and spending. The
# round-2 probe: validation aggregated both metrics and passed when
# EITHER moved in ANY direction, so a frozen PC recipient_count with a
# moved spending figure read as "1/2 moved" — and a broken caseload
# denominator (hence a 100%-take-up error) survived. Direction is part of
# the contract, per metric.
TAKEUP_DIRECTION = "increase"

# Per-benefit movement contract (see assert_fullpart_moved): each of
# these programs feeds DWP take-up denominators through its own override
# flag, so each must move on its own — one benefit moving must never
# bless another's unchanged caseload.
# HB is deliberately absent: its fullpart rows are a cited gap
# (FULLPART_UNEXPRESSIBLE), so there is nothing to validate movement on,
# and demanding movement would force the wrong-direction number back in.
TAKEUP_VALIDATED_PROGRAMS = (
    "pension_credit",
    "universal_credit",
    "child_benefit",
)
# Pension credit components: expected to move with would_claim_pc but
# warn-only — savings credit is closed to new claims, so a forced-on PC
# can move the aggregate while a component split stays put.
TAKEUP_COMPONENT_PROGRAMS = ("guarantee_credit", "savings_credit_only")

rows = []
meta = {
    "year": YEAR,
    "runs": {},
    "resolved": {},
    "unresolved": [],
    "fullpart_overrides_applied": [],
}


def emit(
    run,
    program,
    metric,
    subgroup,
    geo,
    value,
    status="ok",
    gap_reason=None,
    gap_rationale=None,
    action_link=None,
):
    # source + unit_concept travel with every row. The closed UK registry
    # deliberately keeps DWP `benefit_units` distinct from UKMOD
    # `families`, so one generic benunit count cannot serve both lanes:
    # attachment has to know which external source and which unit concept
    # a value is a counterpart to.
    lane = ROW_IDENTITY.get((program, metric))
    if lane is None:
        raise RuntimeError(
            f"({program}, {metric}) has no source/unit assignment — add it "
            "to ROW_IDENTITY deliberately; an unattributed row cannot be "
            "attached to an external claim"
        )
    source, unit_concept = lane
    rows.append(
        {
            "run": run,
            "country": "UK",
            "source": source,
            "program": program,
            "metric": metric,
            "subgroup": subgroup,
            "geography": geo,
            "unit_concept": unit_concept,
            "value": None if value is None else float(value),
            "status": status,
            "gap_reason": gap_reason,
            "gap_rationale": gap_rationale,
            "action_link": action_link,
        }
    )


# Every gap this pipeline can emit, with the rationale and the citable
# action link the descriptive gate (#9) requires. A gap is a FINDING —
# "PolicyEngine cannot express this yet, here is where that is tracked" —
# and a record without a citation is just a blank. Emitting a gap whose
# concept is not in this registry raises: a new gap is named deliberately.
GAP_REASONS = {
    "engine_variable_missing": (
        "No variable in the certified policyengine-uk bundle expresses this "
        "concept; the counterpart cannot be computed at this pin.",
        "https://github.com/PolicyEngine/policyengine-scorecard/issues/40",
    ),
    "housing_benefit_receipt_gated": (
        "Housing Benefit entitlement cannot be expressed in a full-take-up "
        "world at this pin: housing_benefit_eligible requires BOTH "
        "~would_claim_uc (the UC/legacy mutual exclusion, which has its own "
        "engine regression test) and housing_benefit_reported > 0, so "
        "eligibility is RECEIPT-gated. Forcing the take-up flags on drives "
        "HB toward zero rather than toward all-entitled, and the engine "
        "cannot produce entitled non-recipients for HB at all. This is a "
        "capability gap, not a divergence.",
        "https://github.com/PolicyEngine/policyengine-uk/issues/1178",
    ),
    "country_anchor_unavailable": (
        "The geography restriction could not be anchored to this entity, and "
        "an unrestricted total must never be emitted under a GB/NI label.",
        "https://github.com/PolicyEngine/policyengine-scorecard/issues/40",
    ),
    "unweighted_population": (
        "The population denominator did not come back as a weighted "
        "MicroSeries; an unweighted record count is never emitted as if it "
        "were weighted.",
        "https://github.com/PolicyEngine/policyengine-scorecard/issues/40",
    ),
    "tax_band_unresolvable": (
        "The marginal-band cut could not be resolved from the engine's "
        "tax_band enum or any boolean band variable, and an all-taxpayer "
        "aggregate must never be emitted under a band label.",
        "https://github.com/PolicyEngine/policyengine-scorecard/issues/40",
    ),
}


def pe_gap(
    run, program, metric, subgroup, geo, concept, reason="engine_variable_missing"
):
    """Emit a CITED gap. Descriptive gate #9: a gap record carries a
    rationale and an action link, or it is not a finding — it is an
    absence, and the exporter only surfaces claims that already have a
    DB result, so an uncited gap can disappear entirely."""
    if reason not in GAP_REASONS:
        raise RuntimeError(
            f"unregistered gap reason {reason!r} — name it in GAP_REASONS "
            "with its rationale and action link before emitting it"
        )
    rationale, action_link = GAP_REASONS[reason]
    meta["unresolved"].append(
        {"concept": concept, "program": program, "reason": reason}
    )
    emit(
        run,
        program,
        metric,
        subgroup,
        geo,
        None,
        status="pe_gap",
        gap_reason=reason,
        gap_rationale=f"{rationale} (concept: {concept})",
        action_link=action_link,
    )


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


def _is_microseries(series):
    """True only for a genuine microdf MicroSeries, identified by TYPE.

    Never by reading its weight array — the module contract forbids
    touching weight arrays, and .weights access was exactly how the old
    check violated it. When microdf is not importable (CI), an object
    cannot be a real MicroSeries, so identity falls back to the type's
    own name and defining module.
    """
    try:
        from microdf import MicroSeries  # type: ignore
    except ImportError:
        cls = type(series)
        return (
            cls.__name__ == "MicroSeries" and cls.__module__.split(".")[0] == "microdf"
        )
    return isinstance(series, MicroSeries)


def weighted_population(series):
    """Weighted record count of a MicroSeries, or None.

    MicroSeries.count() IS the weighted count (microdf sums weights). A
    plain pandas Series / ndarray also answers len()/count(), but those
    are UNWEIGHTED record counts (~10^5 for a UK survey) and must never
    be emitted as a population denominator. Returning None forces the
    caller onto the pe_gap path.
    """
    if not _is_microseries(series):
        return None
    return float(series.count())


def emit_population_denominator(run_name, hc, series, subgroup="total"):
    """Population denominator for the HBAI rate derivation, or a pe_gap.

    Emitted per subgroup so every published numerator cut (total,
    children, pensioners) has its matching denominator. Never emits an
    unweighted count under status "ok"."""
    n = weighted_population(series)
    if n is None:
        log(
            f"  WARNING: no weighted count for population_{hc}/{subgroup} "
            f"({type(series).__name__} is not a weighted MicroSeries) -> pe_gap"
        )
        pe_gap(
            run_name,
            "hbai_low_income",
            f"population_{hc}",
            subgroup,
            "UK",
            "weighted_population",
        )
        return None
    emit(run_name, "hbai_low_income", f"population_{hc}", subgroup, "UK", n)
    return n


def restricted_mask(masks, entity, geo):
    """(mask, honoured) for a geography restriction at an entity level.

    UK is unrestricted: no mask is fine. GB/NI are restrictions: if the
    entity has no country anchor, the restriction cannot be honoured and
    the caller must emit pe_gap — an unrestricted total must never go
    out under a GB/NI label."""
    mask = masks.get(entity, {}).get(geo)
    if geo == "UK":
        return mask, True
    return mask, mask is not None


def build_sim(fullpart):
    """Managed sim on the certified populace-uk bundle.

    For the fullpart run, every override is set BEFORE any calculate on
    this sim (a calculate first would cache baseline take-up and the
    override would silently do nothing), then read back to confirm it
    took effect.

    Reads the module-global YEAR (set once by main() from argv), like
    every sim.calculate in this file — a year parameter here was
    half-wired (callers never passed it), so it is gone rather than a
    silent divergence trap.
    """
    # UNVERIFIED against an installed engine: mirrors the documented
    # binding surface used by compute_counterparts.py
    # (pe.us.managed_microsimulation()) and docs/ARCHITECTURE.md. If the
    # UK accessor turns out to be spelled differently, this is the line
    # that changes — do not silently swap in a bare country-package
    # Microsimulation, which is a different (uncertified) world.
    import policyengine as pe  # type: ignore

    sim = pe.uk.managed_microsimulation()
    run_name = "fullpart" if fullpart else "baseline"
    # Provenance: sim.policyengine_bundle is the managed-run bundle
    # record (US precedent: compute_counterparts.py reads exactly this);
    # data_bundle/dataset are fallbacks only, and which path served is
    # recorded so a fallback never masquerades as the bundle record.
    bundle = getattr(sim, "policyengine_bundle", None)
    if hasattr(bundle, "items"):
        bundle_info = {k: str(v) for k, v in bundle.items()}
        bundle_source = "policyengine_bundle"
    elif bundle:
        # a non-mapping bundle record still beats the fallback, but it is
        # stringified rather than crashed on
        bundle_info = str(bundle)
        bundle_source = "policyengine_bundle (non-mapping, stringified)"
    else:
        bundle_info = getattr(sim, "data_bundle", None) or getattr(sim, "dataset", None)
        bundle_source = "data_bundle/dataset fallback"
    run_meta = {
        "bundle": bundle_info,
        "bundle_source": bundle_source,
        "year": YEAR,
    }
    meta["runs"][run_name] = run_meta
    if not fullpart:
        return sim

    import numpy as np

    vs = sim.tax_benefit_system.variables
    run_meta.update({"flags_set_true": [], "flags_missing": [], "flags_failed": []})
    for flag, value in FULLPART_OVERRIDES.items():
        if flag not in vs:
            run_meta["flags_missing"].append(flag)
            log(f"  WARNING: override flag {flag} not in variables")
            continue
        entity = vs[flag].entity.key
        n = sim.populations[entity].count  # entity population, NOT a calculate()
        # ndarray, not a Python list: set_input on some core versions
        # expects an ndarray and a list may coerce oddly or fail silently
        # (US parity: np.ones(n, dtype=bool) in compute_counterparts.py)
        arr = np.full(n, value, dtype=bool)
        periods, label = periods_for(vs[flag], YEAR)
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
        periods, _ = periods_for(vs[flag], YEAR)
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


def first_person_anchor(sim, entity, person_values):
    """Value of each group-entity row via its first person member.

    Household-enum projection to group entities crashes in core, so
    group-entity categorical/boolean cuts anchor on the first member —
    the same rule compute_counterparts.py's first_person_anchor_state
    uses for US states."""
    import numpy as np
    import pandas as pd

    pop = sim.populations[entity]
    row_of_person = np.asarray(pop.members_entity_id)
    first = pd.Series(person_values).groupby(pd.Series(row_of_person)).first()
    return first.reindex(np.arange(pop.count)).to_numpy()


def geo_masks(sim, vs):
    """Country masks per entity level, from the person-level projection.

    country is a household-level enum: the person level takes the
    downward projection (map_to="person"), and group entities anchor on
    their first person member via first_person_anchor — never a direct
    map_to onto a group entity, which crashes (or corrupts) on enums.
    An entity whose anchor fails is simply absent from the result, and
    restricted_mask() then forces its GB/NI lines to pe_gap — failure
    here must never become an unrestricted total under a GB label.
    GB = not NI."""
    import numpy as np

    name = resolve(vs, "country")
    masks = {}
    if name is None:
        log("  WARNING: no country variable; all GB/NI-restricted lines go pe_gap")
        return masks
    c = sim.calculate(name, YEAR, map_to="person")
    person_country = np.asarray(getattr(c, "values", c)).astype(str)
    for entity in ("person", "benunit", "household"):
        try:
            arr = (
                person_country
                if entity == "person"
                else first_person_anchor(sim, entity, person_country).astype(str)
            )
        except Exception as e:
            log(
                f"  WARNING: no {entity}-level country anchor ({e}); "
                f"GB/NI-restricted {entity} lines go pe_gap"
            )
            continue
        masks[entity] = {
            "UK": np.ones(len(arr), dtype=bool),
            "GB": arr != "NORTHERN_IRELAND",
            "NI": arr == "NORTHERN_IRELAND",
        }
    return masks


def assert_fullpart_moved(baseline_rows, fullpart_rows):
    """Fail loudly, per benefit AND PER METRIC AND BY DIRECTION.

    Every DWP take-up counterpart divides recipients by the fullpart
    entitled caseload; if a benefit's fullpart == baseline, that
    benefit's denominator is the baseline caseload and its take-up rate
    silently comes out at 100% while every row still reads status "ok".

    Round 2 found the check was still too weak in two ways. It
    AGGREGATED the two sensitive metrics, so a probe with a frozen
    pension-credit recipient_count and a moved spending figure passed as
    "1/2 moved" — exactly the broken-caseload-denominator case. And it
    accepted ANY movement, so a DECREASE passed silently, which is how a
    receipt-gated benefit driven toward zero would have read as healthy.

    So: every (program, metric) pair that is comparable must move, and it
    must move UP. Forcing take-up on adds recipients and adds spending;
    it can never remove either. A benefit whose entitled population the
    engine cannot express is a cited gap upstream of this check
    (FULLPART_UNEXPRESSIBLE), not a number that gets to fail quietly.
    """

    def key(r):
        return (r["program"], r["metric"], r["subgroup"], r["geography"])

    base = {
        key(r): r["value"]
        for r in baseline_rows
        if r["status"] == "ok" and r["metric"] in TAKEUP_SENSITIVE_METRICS
    }
    by_pair = {}
    wrong_direction = []
    for r in fullpart_rows:
        if r["status"] != "ok" or r["metric"] not in TAKEUP_SENSITIVE_METRICS:
            continue
        if key(r) not in base:
            continue
        was, now = base[key(r)], r["value"]
        stats = by_pair.setdefault(
            (r["program"], r["metric"]), {"compared": 0, "moved": 0}
        )
        stats["compared"] += 1
        if now > was:
            stats["moved"] += 1
        elif now < was:
            wrong_direction.append((key(r), was, now))
    compared = sum(s["compared"] for s in by_pair.values())
    moved = sum(s["moved"] for s in by_pair.values())
    by_program = {}
    for (program, metric), stats in by_pair.items():
        agg = by_program.setdefault(program, {"compared": 0, "moved": 0, "metrics": {}})
        agg["compared"] += stats["compared"]
        agg["moved"] += stats["moved"]
        agg["metrics"][metric] = stats
    meta["fullpart_moved"] = {
        "compared": compared,
        "moved": moved,
        "direction": TAKEUP_DIRECTION,
        "by_program": by_program,
    }
    log(
        f"fullpart vs baseline: {moved}/{compared} take-up-sensitive values "
        f"increased (direction is part of the contract)"
    )
    for program, stats in sorted(by_program.items()):
        detail = ", ".join(
            f"{m}:{v['moved']}/{v['compared']}"
            for m, v in sorted(stats["metrics"].items())
        )
        log(f"  {program}: {detail}")

    if wrong_direction:
        raise RuntimeError(
            "forcing take-up ON made these values FALL, which is impossible "
            "for a take-up denominator and is how a receipt-gated benefit "
            f"reads as healthy: {wrong_direction[:5]}. Do not publish this run."
        )
    if not compared:
        raise RuntimeError(
            "no take-up-sensitive values were comparable between baseline and "
            "fullpart (all pe_gap?) — nothing verifies the fullpart run."
        )
    stuck = sorted(
        f"{program}/{metric}"
        for (program, metric), stats in by_pair.items()
        if program in TAKEUP_VALIDATED_PROGRAMS
        and stats["compared"]
        and not stats["moved"]
    )
    if stuck:
        raise RuntimeError(
            f"fullpart is identical to baseline for {stuck}: the overrides "
            "applied and read back on, but these values did not increase. "
            "Their DWP take-up denominators would silently be the baseline "
            "caseload (a 100% take-up rate). Do not publish this run."
        )
    # PER METRIC: a program that moved on spending but not on caseload has
    # a broken denominator, and that is the exact probe that used to pass.
    for program in TAKEUP_VALIDATED_PROGRAMS:
        stats = by_program.get(program)
        if not stats or not stats["compared"]:
            log(
                f"  WARNING: {program} had no comparable take-up-sensitive "
                "values (pe_gap?) — its take-up denominators are unverified"
            )
            continue
        missing = [m for m in TAKEUP_SENSITIVE_METRICS if m not in stats["metrics"]]
        if missing:
            raise RuntimeError(
                f"{program} has no comparable {missing} rows, so its "
                "take-up validation covers only part of the contract. "
                "Every take-up-sensitive metric is validated or the "
                "benefit is a cited gap — never a partial pass."
            )
    for p in TAKEUP_COMPONENT_PROGRAMS:
        stats = by_program.get(p, {})
        if stats.get("compared", 0) and not stats.get("moved", 0):
            log(
                f"  WARNING: component {p} did not move under forced take-up "
                "(closed-to-new-claims components can legitimately hold still)"
            )


def compute_run(run_name, fullpart):
    import numpy as np

    log(f"building {run_name} sim")
    sim = build_sim(fullpart)
    vs = sim.tax_benefit_system.variables
    masks = geo_masks(sim, vs)

    def weighted(
        concept, entity, geo, kind, program, metric, subgroup="total", extra_mask=None
    ):
        name = resolve(vs, concept)
        if name is None:
            pe_gap(run_name, program, metric, subgroup, geo, concept)
            return
        mask, honoured = restricted_mask(masks, entity, geo)
        if not honoured:
            # the geography restriction cannot be applied at this entity
            # level — pe_gap, never an unrestricted total under a GB label
            pe_gap(run_name, program, metric, subgroup, geo, f"country_anchor_{entity}")
            return
        series = sim.calculate(name, YEAR, map_to=entity)
        if extra_mask is not None:
            mask = extra_mask if mask is None else (mask & extra_mask)
        if mask is not None:
            series = series[mask]
        if kind == "sum":
            emit(run_name, program, metric, subgroup, geo, series.sum())
        elif kind == "count_positive":
            emit(run_name, program, metric, subgroup, geo, (series > 0).sum())
        else:
            raise ValueError(kind)

    def benunit_bool(concept, entity="benunit"):
        """Entity-level numpy bool array for a flag concept, or None."""
        name = resolve(vs, concept)
        if name is None:
            return None
        m = sim.calculate(name, YEAR, map_to=entity)
        return np.asarray(getattr(m, "values", m)).astype(bool)

    def person_bool(concept):
        """Person-level numpy bool array for a flag concept, or None."""
        name = resolve(vs, concept)
        if name is None:
            return None
        m = sim.calculate(name, YEAR, map_to="person")
        return np.asarray(getattr(m, "values", m)).astype(bool)

    # benefit caseloads + expenditure (dwp_takeup / obr / ukmod)
    for program, concept, entity, geo in BENEFIT_LINES:
        if fullpart and program in FULLPART_UNEXPRESSIBLE:
            # The engine cannot build this benefit's entitled population
            # (see FULLPART_UNEXPRESSIBLE). A cited gap, not a number
            # whose direction happens to be wrong.
            for metric in TAKEUP_SENSITIVE_METRICS:
                pe_gap(
                    run_name,
                    program,
                    metric,
                    "total",
                    geo,
                    concept,
                    reason=FULLPART_UNEXPRESSIBLE[program],
                )
            continue
        weighted(concept, entity, geo, "count_positive", program, "recipient_count")
        weighted(concept, entity, geo, "sum", program, "benefit_spending")

    # Pension Credit components, as DWP publishes them (PC_COMPONENT_LINES).
    # The engine's raw guarantee_credit / savings_credit are entitlement
    # quantities that never consult would_claim_pc; DWP counts CLAIMED
    # guarantee credit and savings-credit-ONLY. Both are therefore gated
    # on the PC claim flag, and savings-credit-only additionally requires
    # guarantee credit to be zero. Without the gate these rows published a
    # wrong-concept value under status "ok".
    pc_claim = benunit_bool(PC_CLAIM_FLAG)
    for program, concept, entity, geo, exclude in PC_COMPONENT_LINES:
        if pc_claim is None:
            for metric in TAKEUP_SENSITIVE_METRICS:
                pe_gap(run_name, program, metric, "total", geo, PC_CLAIM_FLAG)
            continue
        mask = pc_claim
        if exclude is not None:
            other = resolve(vs, exclude)
            if other is None:
                for metric in TAKEUP_SENSITIVE_METRICS:
                    pe_gap(run_name, program, metric, "total", geo, exclude)
                continue
            other_series = sim.calculate(other, YEAR, map_to=entity)
            mask = mask & (
                np.asarray(getattr(other_series, "values", other_series)) == 0
            )
        weighted(
            concept,
            entity,
            geo,
            "count_positive",
            program,
            "recipient_count",
            extra_mask=mask,
        )
        weighted(
            concept,
            entity,
            geo,
            "sum",
            program,
            "benefit_spending",
            extra_mask=mask,
        )

    # dwp_takeup's HB program is pension-age only (working-age HB has
    # migrated to UC): emit it under the external program id with a
    # pension-age benunit cut anchored on the first (head) person's
    # SP-age flag — the same anchor rule the geography masks use. If the
    # flag or the anchor is unavailable, the cut goes pe_gap; the
    # unrestricted housing_benefit line above never stands in for it.
    program, concept, entity, geo = PENSION_AGE_HB_LINE
    sp_age = person_bool("is_SP_age")
    if sp_age is None:
        for metric in ("recipient_count", "benefit_spending"):
            pe_gap(run_name, program, metric, "total", geo, "is_SP_age")
    else:
        try:
            pension_age_bu = first_person_anchor(sim, entity, sp_age).astype(bool)
        except Exception as e:
            log(f"  WARNING: no {entity}-level SP-age anchor ({e}); {program} pe_gap")
            pension_age_bu = None
        if pension_age_bu is None:
            for metric in ("recipient_count", "benefit_spending"):
                pe_gap(
                    run_name, program, metric, "total", geo, f"sp_age_anchor_{entity}"
                )
        else:
            weighted(
                concept,
                entity,
                geo,
                "count_positive",
                program,
                "recipient_count",
                extra_mask=pension_age_bu,
            )
            weighted(
                concept,
                entity,
                geo,
                "sum",
                program,
                "benefit_spending",
                extra_mask=pension_age_bu,
            )

    # hbai poverty counterparts: persons in relative poverty, BHC and
    # AHC, by age group — every numerator cut paired with its own
    # population denominator so each published rate has a derivation
    # (region cuts follow once the base concept is validated against
    # HBAI's published UK rows)
    # HBAI subgroup cuts every housing-cost basis owes, so the loop can
    # be exhaustive rather than bailing out after one gap.
    HBAI_SUBGROUPS = (("children", "is_child"), ("pensioners", "is_SP_age"))

    def hbai_gaps(hc, concept):
        """Every cell this basis owes, as cited gaps. The round-2 probe:
        an unresolvable poverty variable emitted only the total-numerator
        gap and `continue`d, so an empty-registry run produced 2 HBAI
        gaps where 12 claims were owed — and the exporter only surfaces
        claims that already have a result, so the other 10 vanished."""
        for subgroup in ("total",) + tuple(s for s, _ in HBAI_SUBGROUPS):
            for metric in (f"poverty_count_{hc}", f"population_{hc}"):
                pe_gap(run_name, "hbai_low_income", metric, subgroup, "UK", concept)

    for hc, concept in (
        ("bhc", "in_relative_poverty_bhc"),
        ("ahc", "in_relative_poverty_ahc"),
    ):
        pov = resolve(vs, concept)
        if pov is None:
            hbai_gaps(hc, concept)
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
        emit_population_denominator(run_name, hc, in_pov)
        for subgroup, mask_concept in HBAI_SUBGROUPS:
            arr = person_bool(mask_concept)
            if arr is None:
                pe_gap(
                    run_name,
                    "hbai_low_income",
                    f"poverty_count_{hc}",
                    subgroup,
                    "UK",
                    mask_concept,
                )
                # without the cut there is no subgroup denominator either
                pe_gap(
                    run_name,
                    "hbai_low_income",
                    f"population_{hc}",
                    subgroup,
                    "UK",
                    mask_concept,
                )
                continue
            emit(
                run_name,
                "hbai_low_income",
                f"poverty_count_{hc}",
                subgroup,
                "UK",
                in_pov[arr].sum(),
            )
            # matching subgroup denominator: weighted count of everyone
            # in the subgroup (the indexed series keeps its weights)
            emit_population_denominator(run_name, hc, in_pov[arr], subgroup)

    # uk_hmrc counterparts: taxpayer counts + liability, total and by
    # marginal band (the external adapter's subgroup vocabulary). A band
    # whose flag concept is unresolvable emits pe_gap for both metrics —
    # never an all-taxpayer aggregate under a band label.
    weighted(
        "income_tax", "person", "UK", "count_positive", "income_tax", "taxpayer_count"
    )
    weighted("income_tax", "person", "UK", "sum", "income_tax", "tax_liability")
    band_enum = resolve(vs, "tax_band")
    band_values = None
    if band_enum is not None:
        series = sim.calculate(band_enum, YEAR, map_to="person")
        raw = getattr(series, "values", series)
        # An EnumArray stores integer INDICES; decode_to_str() turns them
        # into the enum member NAMES ("BASIC"/"HIGHER"/"ADDITIONAL" at the
        # certified pin). Comparing the undecoded array to a name would
        # match nothing and silently empty every band cut, so a series
        # that cannot be decoded is not used at all — the band falls to
        # its boolean fallback and then to a cited gap.
        if hasattr(raw, "decode_to_str"):
            band_values = np.asarray(raw.decode_to_str()).astype(str)
        else:
            log(
                f"  WARNING: {band_enum} did not come back as a decodable "
                "enum array; band cuts fall back to the boolean concepts"
            )
    for band_subgroup, enum_value, band_concept in HMRC_BAND_CUTS:
        band = None
        if band_values is not None:
            # Accept the member NAME (what decode_to_str returns) or the
            # member VALUE, so a core release that changes which one it
            # decodes to does not silently empty the cut.
            band = (band_values == enum_value) | (
                np.char.lower(band_values) == enum_value.lower()
            )
            if not band.any():
                # The enum resolved but names its bands differently at
                # this pin: fall through rather than emit an empty cut as
                # if it were a real zero.
                band = None
        if band is None:
            band = person_bool(band_concept)
        if band is None:
            for metric in ("taxpayer_count", "tax_liability"):
                pe_gap(
                    run_name,
                    "income_tax",
                    metric,
                    band_subgroup,
                    "UK",
                    f"tax_band={enum_value} / {band_concept}",
                    reason="tax_band_unresolvable",
                )
            continue
        weighted(
            "income_tax",
            "person",
            "UK",
            "count_positive",
            "income_tax",
            "taxpayer_count",
            subgroup=band_subgroup,
            extra_mask=band,
        )
        weighted(
            "income_tax",
            "person",
            "UK",
            "sum",
            "income_tax",
            "tax_liability",
            subgroup=band_subgroup,
            extra_mask=band,
        )
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
