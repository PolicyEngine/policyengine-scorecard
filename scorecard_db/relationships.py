"""Effective calibration relationship per (program, metric).

The doctrine (issue #1 point 2) exists to label tautologies: a comparison
whose PE side was disciplined toward the same administrative quantity class
the external number embodies is not a validation win. Urban's own numbers are
never literally consumed by populace targets, but the FNS/SSA/SOI series
underlying several of its columns are — so relationship is assigned at the
(program, metric) level from the certified build's documented target surface
and seeds (docs/replication-assessment.md §3-§4), not defaulted.

This module is the canonical home; pipeline/build_comparison.py mirrors it
for the JSON path until that path reads the DB.
"""

from .models import CalibrationRelationship as CR
from .models import Metric

_FNS = (
    CR.CONSUMED_AS_TARGET,
    "§3-§4: SNAP participating units count-calibrated to FNS average-month "
    "household counts (national + state) — the same admin-caseload class as "
    "Urban's numerator",
)
_SSA = (
    CR.CONSUMED_AS_TARGET,
    "§3: SSI count-calibrated to SSA state recipient counts and payments",
)
_ASPE = (
    CR.SEED_SOURCE,
    "§3: TANF flag seeded at ASPE 0.219 — a TRIM3 rate, the same model "
    "family as ATTIS; only dollar targets exist (missed −36%)",
)
_HELD_ELIG = (
    CR.HELD_OUT,
    "§4: no eligibility targets; eligibility is disciplined only indirectly "
    "via income/demographic margins",
)

_MAP = {
    ("snap", Metric.PARTICIPATION_RATE): _FNS,
    ("snap", Metric.PARTICIPATION_GAP_COUNT): _FNS,
    ("snap", Metric.PARTICIPANT_COUNT): _FNS,
    ("snap", Metric.ELIGIBLE_COUNT): _HELD_ELIG,
    ("snap", Metric.ELIGIBILITY_RATE): _HELD_ELIG,
    ("ssi", Metric.PARTICIPATION_RATE): _SSA,
    ("ssi", Metric.PARTICIPATION_GAP_COUNT): _SSA,
    ("ssi", Metric.PARTICIPANT_COUNT): _SSA,
    ("ssi", Metric.ELIGIBLE_COUNT): (
        CR.HELD_OUT,
        "payable-under-forced construction; §4 targets recipient counts, "
        "not eligible counts",
    ),
    ("ssi", Metric.ELIGIBILITY_RATE): (
        CR.HELD_OUT,
        "payable-under-forced construction; §4 targets recipient counts, "
        "not eligible counts",
    ),
    ("tanf", Metric.PARTICIPATION_RATE): _ASPE,
    ("tanf", Metric.PARTICIPATION_GAP_COUNT): _ASPE,
    ("tanf", Metric.PARTICIPANT_COUNT): _ASPE,
    ("tanf", Metric.ELIGIBLE_COUNT): _HELD_ELIG,
    ("tanf", Metric.ELIGIBILITY_RATE): _HELD_ELIG,
    ("eitc", Metric.ELIGIBLE_COUNT): (
        CR.HELD_OUT,
        "forced-flag positive-credit count is not itself a target; SOI "
        "claims targets discipline a subset",
    ),
    ("eitc", Metric.ELIGIBILITY_RATE): (
        CR.HELD_OUT,
        "forced-flag positive-credit count is not itself a target; SOI "
        "claims targets discipline a subset",
    ),
    ("ctc_refund", None): (
        CR.CONSUMED_AS_TARGET,
        "§4-§5: refundable CTC claims and dollars are SOI-targeted; no "
        "take-up flag exists, so the count is claims-shaped",
    ),
    ("wic", None): (
        CR.HELD_OUT,
        "§4: zero WIC calibration targets; §6: the near-match is out-of-sample",
    ),
    ("housing", None): (CR.HELD_OUT, "§4: zero housing targets"),
    ("liheap", None): (CR.HELD_OUT, "no PE national model consumes these"),
    ("ccdf", None): (CR.HELD_OUT, "no PE national model consumes these"),
    # poverty blocks (Urban tidy programs "base"/"fullpart")
    ("base", None): (CR.HELD_OUT, None),  # basis set below (permanent)
    ("fullpart", None): (CR.HELD_OUT, None),
}

# Doctrine (Max, 2026-08-02, final formulation): we may not calibrate
# against ANY tax-benefit quantity from a survey — reported or computed —
# or anything derived from such. Four quadrants: admin tax-benefit
# quantities = targets (SOI, FNS, SSA, ACF); raw survey quantities =
# targets (ACS population/structure/income margins); survey tax-benefit
# quantities (total SNAP from the CPS) and their derivatives (SPM/OPM
# poverty above all; other models' survey-based estimates) = NEVER.
# Populace replaces the survey's tax-benefit measurement with imputed,
# computed, admin-calibrated values; fitting the survey-derived version
# launders its error back in and destroys the validation signal. Release
# gates may fail on held-out regressions (issue #1 point 3); fitting the
# statistic is categorically different and prohibited.
PERMANENT_HOLDOUT_METRICS = frozenset(
    {
        Metric.POVERTY_RATE,
        Metric.POVERTY_RATE_CHANGE,
        Metric.POVERTY_COUNT_CHANGE,
        # A poverty COUNT is the same survey-derived quantity as a poverty
        # rate with the denominator multiplied back in; the doctrine covers
        # "anything derived from such". Added with the UK HBAI ingest (#33),
        # which is the first population to carry poverty counts.
        Metric.POVERTY_COUNT,
    }
)
PERMANENT_HOLDOUT_BASIS = (
    "PERMANENT holdout (doctrine 2026-08-02): no tax-benefit quantity from "
    "a survey — reported or computed — nor anything derived from such may "
    "be a calibration target; SPM poverty derives from survey tax-benefit "
    "measurement. Admin tax-benefit quantities and raw survey margins "
    "(ACS population/structure) remain legitimate targets."
)


def never_calibrate(metric) -> bool:
    """True if this metric may never become a calibration target."""
    return Metric(metric) in PERMANENT_HOLDOUT_METRICS


def effective_relationship(program, metric):
    """(CalibrationRelationship, basis) for a program × Metric pair."""
    if metric is not None and never_calibrate(metric):
        return CR.HELD_OUT, PERMANENT_HOLDOUT_BASIS
    hit = _MAP.get((program, metric)) or _MAP.get((program, None))
    if hit is None:
        return CR.HELD_OUT, "no PE consumption identified"
    return hit


# --- UK sources (#33) ----------------------------------------------------
# Assigned from the LITERAL consumption surfaces, read at the certified
# pins (2026-08-19): populace-uk-2023-dd68c73 embeds policyengine-uk-data
# @ dd68c73, whose targets/sources/{obr,dwp,hmrc_spi}.py define the 149
# consumed targets; engine-side take-up parameters read from
# policyengine-uk (gov/dwp/*/takeup.yaml). consumed_as_target is claimed
# ONLY where a row's quantity matches a named consumed line; everything
# else is seed_source (shared base or parameter seeding, evidence named)
# or held_out. Never family-wide defaults in either direction.

# OBR EFO Table 4.9 welfare lines consumed by pe-uk-data@dd68c73
# (targets/sources/obr.py::_parse_welfare row labels; March-2026 EFO,
# forecast columns FY2024-25..2030-31 — the FY2024-25 OUTTURN column is
# also read there, but outturn cells route to Ledger, never to claims).
# Stated in the ADAPTER's program vocabulary; the pe-uk-data label each
# maps to is quoted (targets/sources/obr.py benefit_rows, verbatim).
OBR_CONSUMED_WELFARE_PROGRAMS = frozenset(
    {
        "housing_benefit_not_jsa",  # "Housing benefit (not on JSA)"
        "dla_and_pip",  # "Disability living allowance and personal indep…"
        "incapacity_benefits",  # "Incapacity benefits"
        "attendance_allowance",  # "Attendance allowance"
        "pension_credit",  # "Pension credit"
        "carers_allowance",  # "Carer's allowance"
        "statutory_maternity_pay",  # "Statutory maternity pay"
        "winter_fuel_payment",  # "Winter fuel payment"
        "universal_credit",  # "Universal credit" (in-cap + outside-cap)
        "child_benefit",  # "Child benefit"
        "state_pension",  # "State pension"
        "jobseekers_allowance",  # "Jobseeker's allowance"
    }
)
_OBR_CONSUMED = (
    CR.CONSUMED_AS_TARGET,
    "pe-uk-data@dd68c73 targets/sources/obr.py::_parse_welfare consumes "
    "this Table 4.9 line's March-2026 EFO forecast values as calibration "
    "targets (read 2026-08-19).",
)
_OBR_UNCONSUMED = (
    CR.HELD_OUT,
    "Table 4.9 line NOT in pe-uk-data@dd68c73's consumed welfare set "
    "(targets/sources/obr.py, read 2026-08-19); forecast-vs-forecast "
    "comparison.",
)

# DWP income-related-benefits take-up (FYE 2024 publication, adapter #43).
# Engine evidence (policyengine-uk, read 2026-08-19):
#   gov/dwp/pension_credit/takeup.yaml = 0.7, citing the FYE-2020 edition
#   of THIS series -> the parameter is seeded from an older edition;
#   gov/dwp/housing_benefit/takeup.yaml = 1.0 "by definition ... only
#   current claimants are eligible (no new claims)" -> a stated modeling
#   choice, the live comparator for policyengine-uk#1813.
# Administrative cells (recipient counts, amounts claimed) route to
# Ledger and never reach these claims.
_PC_TAKEUP_SEED = (
    CR.SEED_SOURCE,
    "policyengine-uk pension_credit/takeup.yaml (0.7) cites the FYE-2020 "
    "edition of this series — parameter seeding from an older edition, "
    "not calibration to this one; edition mismatch (FYE-2024 here) is a "
    "named axis. Modeled derivatives (entitled non-recipients, unclaimed "
    "amounts) share the seeding series.",
)
_HB_TAKEUP_HELD = (
    CR.HELD_OUT,
    "policyengine-uk housing_benefit/takeup.yaml sets 1.0 by stated "
    "design ('only current claimants are eligible — no new claims'); "
    "nothing is fitted to this series. Live comparator for "
    "policyengine-uk#1813.",
)

# HMRC liabilities (adapter #45): HMRC's liabilities statistics are SPI
# projections; pe-uk-data@dd68c73 consumes SPI Tables 3.6/3.7 income-band
# distributions (targets/sources/hmrc_spi.py) — a shared microdata base,
# not these statistics themselves.
_HMRC_SPI_SEED = (
    CR.SEED_SOURCE,
    "shared SPI base: pe-uk-data@dd68c73 consumes SPI Tables 3.6/3.7 "
    "income-band distributions (targets/sources/hmrc_spi.py, read "
    "2026-08-19); these liabilities tables are projections from the same "
    "SPI microdata, not themselves consumed.",
)
_HMRC_RECKONER_HELD = (
    CR.HELD_OUT,
    "ready-reckoner rows are HMRC model claims (policy-change scores); "
    "nothing in pe-uk-data consumes them.",
)

_UKMOD_HELD = (
    CR.HELD_OUT,
    "UKMOD is a peer microsimulation, not a calibration source; no PE UK "
    "parameter is fitted to its published statistics.",
)

# OBR published policy EFFECTS (#55): package impacts on GDP/CPI, the
# per-measure supply-side scorings, and the decisions' effect on
# borrowing. Distinct from the obr welfare-baseline source, whose
# FY2024-25 outturn column pe-uk-data does consume: nothing in
# pe-uk-data or policyengine-uk reads a macro-effect path — they are
# what the Macro members are scored AGAINST.
_OBR_POLICY_EFFECTS_HELD = (
    CR.HELD_OUT,
    "OBR macro/policy-effect estimates are scored, never consumed: no "
    "pe-uk-data target and no policyengine-uk parameter is fitted to a "
    "GDP/CPI impact path, a supply-side scoring, or the decisions' "
    "effect on borrowing (consumption surfaces read 2026-08-19 at the "
    "certified pins; the obr welfare source is the only OBR material "
    "with a consuming pin).",
)


def uk_relationship(source, metric, program=None, kind=None):
    """(CalibrationRelationship, basis) for a UK claim, keyed exactly.

    ``program`` is the claim's program condition; ``kind`` disambiguates
    within a source where the publication mixes products:
      dwp_takeup: "takeup_rate" | "modeled_estimate" (ENR / unclaimed) |
                  "average_award"
      uk_hmrc:    "liabilities" | "reckoner"
      obr:        forecast rows only (outturn cells route to Ledger
                  before relationships are assigned)
    Unknown combinations raise — assignment is always deliberate.
    """
    if metric is not None and never_calibrate(metric):
        return CR.HELD_OUT, PERMANENT_HOLDOUT_BASIS
    if source == "dwp_takeup":
        if program in ("housing_benefit_pensioners", "housing_benefit"):
            return _HB_TAKEUP_HELD
        if program in (
            "pension_credit",
            "guarantee_credit",
            "savings_credit_only",
        ):
            if kind == "average_award":
                return (
                    CR.HELD_OUT,
                    "average award amounts fall out of the modelled "
                    "entitlement; not a seeding series input.",
                )
            return _PC_TAKEUP_SEED
        raise ValueError(
            f"dwp_takeup program {program!r} needs a deliberate relationship assignment"
        )
    if source == "uk_hmrc":
        if kind == "reckoner":
            return _HMRC_RECKONER_HELD
        if kind == "liabilities":
            return _HMRC_SPI_SEED
        raise ValueError(f"uk_hmrc kind {kind!r} needs a deliberate assignment")
    if source == "obr":
        if kind == "outturn":
            raise ValueError(
                "OBR outturn cells route to Ledger before relationship "
                "assignment — an outturn row must never become a claim"
            )
        if program in OBR_CONSUMED_WELFARE_PROGRAMS:
            return _OBR_CONSUMED
        return _OBR_UNCONSUMED
    if source == "obr_policy_effects":
        if kind not in ("post_behavioural", "supply_side"):
            raise ValueError(
                f"obr_policy_effects basis {kind!r} needs a deliberate assignment"
            )
        return _OBR_POLICY_EFFECTS_HELD
    if source == "ukmod":
        return _UKMOD_HELD
    if source == "hm_treasury":
        return (CR.HELD_OUT, "fiscal-event costings are scored, never consumed.")
    if source == "dwp":
        return (
            CR.HELD_OUT,
            "FRR impact statements are scored, never consumed; the DWP "
            "quarterly deductions OUTTURN tables PE's parameters do "
            "consume are deliberately not ingested as external scores.",
        )
    raise ValueError(
        f"no UK calibration relationship for ({source!r}, {metric}, "
        f"{program!r}, {kind!r}) — assign it here rather than defaulting"
    )
