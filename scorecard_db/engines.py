"""Which ENGINE produced a claim, and which publishers share one (#132).

`source_model` is documented as the model behind a claim. For most
sources it holds one: ``ukmod_b2026.01``, ``ifs_taxben``,
``EUROMOD BE (J1.0+)``. For ``resolution_foundation`` it held the
PUBLISHER's own name, and the consequence was that a fact the harvest
had already established went missing at ingest:

    "Underlying engine for their distributional/projection work: the
     IPPR Tax Benefit Model run on DWP FRS/HBAI microdata (every
     distributional figure sources 'RF projections including use of the
     IPPR Tax Benefit Model')."
        -- sources/harvest-uk-2026-08-02/uk_resolution_foundation/NOTES.md

WHY THIS IS NOT relationships.py. That registry answers "does
PolicyEngine consume this?" — independence FROM the model under test,
and it answers it well. This one answers "do two external sources share
an engine?" — independence BETWEEN sources. Agreement between two
publishers running one engine is not corroboration; it is one estimate
reported twice.

WHY IT IS CLAIM-LEVEL AND NOT SOURCE-LEVEL. JRF is the proof: its UK
Poverty workbook is HBAI-derived and genuinely independent, while other
JRF output is the shared engine. A source-level mapping would be wrong
about half of it, so the engine belongs on the CLAIM and this module
only says which engines exist and who shares them.
"""

from __future__ import annotations

from typing import Optional

# Engine id -> (display name, maintainer, note). Closed: an unknown
# engine raises rather than being invented at a call site.
ENGINES: dict[str, tuple[str, str, str]] = {
    "ukmod": (
        "UKMOD",
        "CeMPA, University of Essex",
        "EUROMOD platform, FRS input. Open code, open validation, "
        "annual country report.",
    ),
    "ifs_taxben": (
        "TAXBEN",
        "Institute for Fiscal Studies",
        "Proprietary; not available to outside researchers.",
    ),
    "euromod": (
        "EUROMOD",
        "JRC, European Commission",
        "The EU platform UKMOD is built on; country models are separate.",
    ),
    "landman_ttm": (
        "IPPR / Resolution Foundation / Landman Economics tax-transfer model",
        "PERU, Manchester Metropolitan University",
        "Written by Landman Economics (Howard Reed, 2008-09); licensed for "
        "a fee; no public documentation, code, versioning or validation "
        "report. SHARED — see SHARED_ENGINE.",
    ),
    "hmt_igotm": (
        "IGOTM",
        "HM Treasury",
        "Government model; limited public information.",
    ),
    "dwp_psm": (
        "Policy Simulation Model",
        "Department for Work and Pensions",
        "Government model; limited public information.",
    ),
    "axiom": (
        "Axiom",
        "PolicyEngine",
        "Rules engine behind the Belgian lane.",
    ),
}

# Publishers that report results from the SAME engine. Recorded as an
# audit ledger, the converse of uk_aliases.DISTINCT: those pairs must
# never be UNIFIED, these must never be treated as INDEPENDENT.
#
# The hazard is visible inside a single document: IPPR's Annex 1
# costings table attributes its two-child-limit row to "JRF analysis
# using IPPR tax-benefit model and DWP 2025e" — one row, another
# organisation's run of the shared engine.
SHARED_ENGINE: dict[str, frozenset[str]] = {
    "landman_ttm": frozenset(
        {
            "ippr",
            "resolution_foundation",
            "jrf",
            "nef",
            "legatum",
        }
    ),
}

# Sources whose claims are model OUTPUT rather than administrative
# fact, and the engine each one's modelled claims come from. A source
# absent here publishes administrative or survey fact, not simulation.
MODEL_OUTPUT_SOURCES: dict[str, str] = {
    "ukmod": "ukmod",
    "ifs": "ifs_taxben",
    "jrc_euromod": "euromod",
    "resolution_foundation": "landman_ttm",
}


def engine_of(source: str) -> Optional[str]:
    """Engine id for a source's MODELLED claims, or None if the source
    publishes fact rather than simulation."""
    return MODEL_OUTPUT_SOURCES.get(source)


def describe(engine_id: str) -> tuple[str, str, str]:
    if engine_id not in ENGINES:
        raise ValueError(
            f"unknown engine {engine_id!r} — add it to ENGINES with its "
            "maintainer rather than naming an engine at a call site"
        )
    return ENGINES[engine_id]


def shares_engine(a: str, b: str) -> Optional[str]:
    """The engine two publishers share, or None.

    Two sources that share an engine are not independent evidence about
    each other. Agreement between them is one estimate reported twice.
    """
    if a == b:
        return None
    for engine, publishers in SHARED_ENGINE.items():
        if a in publishers and b in publishers:
            return engine
    return None


def independent(a: str, b: str) -> bool:
    return shares_engine(a, b) is None
