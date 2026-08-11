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
