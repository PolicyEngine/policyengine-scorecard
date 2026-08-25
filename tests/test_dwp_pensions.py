"""DWP workplace pension participation (#98).

PolicyEngine-UK models pensions and until this lane not one of the
15,858 UK claims said anything about them. What is pinned here is what
makes each rate interpretable — its denominator and its survey — and the
refusal to read the parts of the workbook whose meaning is unlabelled.
"""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LANE = ROOT / "sources" / "dwp-pension-participation"
RAW = LANE / "raw" / "dwp_workplace_pension_participation_2009_2025.xlsx"
EXTERNAL = ROOT / "data" / "externals" / "dwp-pension-participation.json"
SHA = "4d4bd871b23f9ef763101b4491bce437f3c02e622ce9394c857c0346fb326e41"


@pytest.fixture(scope="module")
def rows():
    return json.loads(EXTERNAL.read_text())


@pytest.fixture(scope="module")
def adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "dwp_pens_adapter", LANE / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_raw_artifact_is_the_pinned_bytes():
    assert RAW.exists()
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == SHA


def test_row_counts(rows):
    assert len(rows) == 1377
    by = {}
    for r in rows:
        by[r["axis"]] = by.get(r["axis"], 0) + 1
    assert by == {"earnings_band": 357, "age_band": 459, "region": 561}


# --- what makes a rate interpretable ----------------------------------------


def test_every_rate_carries_its_denominator(rows):
    """Eligibility is part of the identity. The denominator is employees
    ELIGIBLE for automatic enrolment — an earnings trigger and age range
    that have both moved over the series."""
    for r in rows:
        assert "ELIGIBLE for automatic enrolment" in r["denominator"]
        assert "moved over the series" in r["denominator"]


def test_every_rate_carries_the_survey_axis(rows):
    """ASHE is an employer survey of jobs; PE-UK is FRS-based. That
    difference is the first divergence axis, same as the LPC lane."""
    for r in rows:
        assert "ASHE" in r["survey_axis"]
        assert "FRS-based" in r["survey_axis"]


def test_rates_are_shares_not_percents(rows):
    assert all(0.0 <= r["value"] <= 1.0 for r in rows)


def test_a_percent_slipping_in_is_refused(monkeypatch):
    """A hundredfold error nobody could see downstream."""
    from scorecard_db import ingest_dwp_pensions as dp

    raw = json.loads(EXTERNAL.read_text())
    bad = [dict(r) for r in raw]
    bad[0]["value"] = 78.0
    monkeypatch.setattr(dp, "_load", lambda: bad)
    with pytest.raises(ValueError, match="not a share"):
        dp.stage()


# --- geography and identity -------------------------------------------------


def test_geography_is_gb_not_uk(rows):
    """ASHE excludes Northern Ireland."""
    assert {r["geography"] for r in rows} == {"GB"}
    readme = (LANE / "raw" / "README.md").read_text()
    assert "excludes Northern Ireland" in readme


def test_the_axis_rides_on_the_claim(rows):
    """Otherwise an earnings band and an age band collide on one
    subgroup key."""
    from scorecard_db.ingest_dwp_pensions import stage

    scores, _ = stage()
    assert len({s.claim_id() for s in scores}) == len(scores) == 1377
    axes = {s.conditions["axis"] for s in scores}
    assert axes == {"earnings_band", "age_band", "region"}


def test_eligibility_bands_are_not_income_quantiles():
    """DWP's bands are defined by the auto-enrolment trigger, not by an
    income distribution."""
    from scorecard_db.uk_aliases import DISTINCT

    assert ("dwp_pensions:gbp_10k_20k", "ukmod:q1") in DISTINCT
    assert ("dwp_pensions:gbp_70k_plus", "ukmod:q5") in DISTINCT


def test_the_lpc_age_band_distinction_is_deferred_not_asserted():
    """DWP's age bands are also not LPC's minimum-wage age bands — one is
    an enrolment range, the other a wage-rate category — but the `lpc`
    vocabulary is registered on #93's branch, not here. Asserting a pair
    against a source nobody has registered is the same overclaiming the
    review caught on #92: the ledger would read as if the distinction had
    been checked when there is nothing on the other side. So it is
    deferred in a comment and stated in prose instead."""
    from scorecard_db.uk_aliases import DISTINCT, known

    assert not known("lpc", "subgroup"), "lpc is registered here after all"
    assert not any("lpc" in a + b for a, b in DISTINCT)
    src = (ROOT / "scorecard_db" / "uk_aliases.py").read_text()
    assert "DEFERRED, deliberately" in src
    note = json.loads((LANE / "source.json").read_text())["identity_note"]
    assert "DEFERRED from the ledger" in note


def test_unregistered_values_raise():
    from scorecard_db.uk_aliases import canon

    with pytest.raises(ValueError, match="unregistered"):
        canon("dwp_pensions", "earnings_band", "£80,000+")


# --- what is deliberately not read ------------------------------------------


def test_the_unlabelled_blocks_are_not_guessed_at(tmp_path, monkeypatch, adapter):
    """Each sheet holds six tables side by side and only the first has a
    descriptor. A number whose meaning is inferred from its column
    position is not a claim."""
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    _, counts, unread = adapter.build()
    assert counts == {"1.3a": 357, "1.4": 459, "1.9a": 561}
    assert unread["unlabelled_side_by_side_blocks"]["blocks"] == 15
    assert unread["sheets_not_read"]["sheets"] > 0
    for entry in unread.values():
        assert len(entry["reason"]) > 80


def test_a_reshuffled_workbook_raises(tmp_path, monkeypatch, adapter):
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    monkeypatch.setattr(adapter, "BLOCK1_ANCHOR", "Something DWP never printed")
    with pytest.raises(RuntimeError, match="block-1 anchor failed"):
        adapter.build()


def test_an_unregistered_category_raises(tmp_path, monkeypatch, adapter):
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    sheets = dict(adapter.SHEETS)
    sheets["1.4"] = ("age_band", {"22 to 25": "age_22_25"})
    monkeypatch.setattr(adapter, "SHEETS", sheets)
    with pytest.raises(RuntimeError, match="unregistered 1.4 age_band"):
        adapter.build()


# --- ingest ------------------------------------------------------------------


def test_every_claim_is_held_out():
    from scorecard_db.ingest_dwp_pensions import stage
    from scorecard_db.models import CalibrationRelationship

    scores, _ = stage()
    assert all(
        s.calibration_relationship is CalibrationRelationship.HELD_OUT for s in scores
    )


def test_the_relationship_names_the_narrower_question():
    """The engine models contributions and relief but has no pension
    commencement lump sum at all (#98), so the pensions question this
    scorecard can ask is narrower than the pensions system."""
    from scorecard_db.models import Metric
    from scorecard_db.relationships import uk_relationship

    _, evidence = uk_relationship("dwp_pensions", Metric.PARTICIPATION_RATE)
    assert "no pension commencement lump sum" in evidence
    assert "2026-08-25" in evidence


def test_full_ingest_round_trip(tmp_path):
    import sqlite3

    from scorecard_db import ScorecardDB
    from scorecard_db.ingest_dwp_pensions import ingest

    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    assert ingest(db_path)["claims"] == 1377
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source='dwp_pensions'"
    ).fetchone()[0]
    assert n == 1377
    lane = conn.execute(
        "SELECT * FROM lanes WHERE lane='dwp-pension-participation'"
    ).fetchone()
    conn.close()
    assert lane["stage"] == "ingested"


def test_build_db_registers_the_step():
    import inspect

    from scorecard_db import build_db

    assert "ingest_dwp_pensions.ingest" in inspect.getsource(build_db)
