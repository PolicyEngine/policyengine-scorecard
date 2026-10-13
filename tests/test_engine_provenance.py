"""Engine provenance, and which publishers are not independent (#132).

relationships.py answers "does PolicyEngine consume this?" — independence
FROM the model under test. This answers "do two external sources share an
engine?" — independence BETWEEN sources.
"""

import sqlite3

import pytest

from scorecard_db import engines


def test_rf_names_the_engine_not_itself():
    """The defect this fixes: source_model held the PUBLISHER, losing a
    fact the harvest had already established."""
    assert engines.engine_of("resolution_foundation") == "landman_ttm"
    name, maintainer, _ = engines.describe("landman_ttm")
    assert "Landman Economics" in name
    assert "Manchester Metropolitan" in maintainer


def test_the_shared_engine_ledger_names_all_four_publishers():
    """One engine, four badges. Agreement between them is one estimate
    reported twice, not corroboration."""
    shared = engines.SHARED_ENGINE["landman_ttm"]
    assert {"ippr", "resolution_foundation", "jrf", "nef"} <= shared


def test_rf_and_ippr_are_not_independent():
    assert engines.shares_engine("resolution_foundation", "ippr") == "landman_ttm"
    assert not engines.independent("resolution_foundation", "ippr")
    assert not engines.independent("jrf", "ippr")


def test_genuinely_separate_lineages_stay_independent():
    """UKMOD, TAXBEN and the shared TTM are three lineages. The ledger
    must not over-claim by marking everything related."""
    assert engines.independent("resolution_foundation", "ukmod")
    assert engines.independent("ukmod", "ifs")
    assert engines.independent("ifs", "resolution_foundation")
    assert engines.shares_engine("ukmod", "ukmod") is None


def test_an_unknown_engine_raises_rather_than_being_invented():
    with pytest.raises(ValueError, match="unknown engine"):
        engines.describe("some_model_someone_typed")


def test_a_source_publishing_fact_has_no_engine():
    """Engine provenance is for simulation output. DWP and HMRC publish
    administrative fact and must not be given one."""
    for src in ("dwp_hbai", "uk_hmrc", "obr", "lpc"):
        assert engines.engine_of(src) is None


def test_every_model_output_source_names_a_registered_engine():
    for src, engine in engines.MODEL_OUTPUT_SOURCES.items():
        assert engine in engines.ENGINES, src


def test_the_built_db_carries_engines_not_publishers():
    """The end-to-end check: no model-output claim may carry its own
    source slug in source_model."""
    conn = sqlite3.connect("data/scorecard.db")
    rows = dict(
        conn.execute(
            "SELECT source, source_model FROM external_scores "
            "WHERE source IN (?, ?, ?) GROUP BY source",
            ("resolution_foundation", "ifs", "ukmod"),
        )
    )
    conn.close()
    assert rows["resolution_foundation"] == "landman_ttm"
    for source, model in rows.items():
        assert model != source, f"{source}: source_model is the publisher"


# --- one engine at several releases ---------------------------------------


def test_the_release_ledger_names_registered_engines_and_shared_publishers():
    for engine, by_source in engines.ENGINE_RELEASES.items():
        assert engine in engines.ENGINES, engine
        assert set(by_source) <= engines.SHARED_ENGINE[engine], engine


def test_a_versioned_spelling_splits_into_engine_and_release():
    assert engines.split_release("ukmod_b1.13") == ("ukmod", "b1.13")
    assert engines.split_release("ukmod") == ("ukmod", None)
    # a registered id is never read as a release of a shorter one
    assert engines.split_release("ifs_taxben") == ("ifs_taxben", None)
    assert engines.split_release("arithmetic") == ("arithmetic", None)


def test_a_release_the_ledger_lacks_is_not_known():
    assert engines.known_release("cpag", "ukmod_b1.13")
    assert engines.known_release("fraser_of_allander", "ukmod")
    assert engines.known_release("ifs", "arithmetic")
    assert not engines.known_release("cpag", "ukmod_b9.99")
    assert not engines.known_release("ifs", "ukmod_b1.13")


def test_every_versioned_spelling_in_the_built_db_is_a_recorded_release():
    """The ledger is consumed, not decorative: a claim may carry a release
    only if the ledger records that publisher running it."""
    conn = sqlite3.connect("data/scorecard.db")
    rows = conn.execute(
        "SELECT DISTINCT source, source_model FROM external_scores"
        " WHERE source_model IS NOT NULL"
    ).fetchall()
    conn.close()
    versioned = [(s, m) for s, m in rows if engines.split_release(m)[1] is not None]
    assert ("ukmod", "ukmod_b2026.01") in versioned
    for source, model in versioned:
        assert engines.known_release(source, model), (source, model)
