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
        "§4: zero WIC calibration targets; §6: the near-match is "
        "out-of-sample",
    ),
    ("housing", None): (CR.HELD_OUT, "§4: zero housing targets"),
    ("liheap", None): (CR.HELD_OUT, "no PE national model consumes these"),
    ("ccdf", None): (CR.HELD_OUT, "no PE national model consumes these"),
    # poverty blocks (Urban tidy programs "base"/"fullpart")
    ("base", None): (
        CR.HELD_OUT, "§4: no poverty targets in the Build P surface",
    ),
    ("fullpart", None): (
        CR.HELD_OUT, "§4: no poverty targets in the Build P surface",
    ),
}


def effective_relationship(program, metric):
    """(CalibrationRelationship, basis) for a program × Metric pair."""
    hit = _MAP.get((program, metric)) or _MAP.get((program, None))
    if hit is None:
        return CR.HELD_OUT, "no PE consumption identified"
    return hit
