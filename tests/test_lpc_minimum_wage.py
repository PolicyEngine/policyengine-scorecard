"""The Low Pay Commission minimum-wage lane (#88).

PolicyEngine-UK carries a minimum-wage implementation and nothing
validated it. What is pinned here is the two things this lane
introduces on purpose — a JOBS unit concept, and the bite denominator
riding on the claim — plus what the adapter deliberately does not read.
"""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LANE = ROOT / "sources" / "lpc-minimum-wage"
EXTERNAL = ROOT / "data" / "externals" / "lpc-minimum-wage.json"

SHAS = {
    "lpc_2025_main_report_data.xlsx": (
        "bd0c10dc42bc04d5af09792731464b9549f971a3ff36f9c2ddf0ee69281f08ee"
    ),
    "lpc_2025_coverage_by_la_region_nation.xlsx": (
        "2cab42281f0b8094ab1a9077016cf21b91e1069da1fe7dd07f7bb771e108498d"
    ),
}


@pytest.fixture(scope="module")
def rows():
    return json.loads(EXTERNAL.read_text())


@pytest.fixture(scope="module")
def adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location("lpc_adapter", LANE / "adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_raw_artifacts_are_the_pinned_bytes():
    for name, sha in SHAS.items():
        p = LANE / "raw" / name
        assert p.exists(), name
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sha, name


def test_row_counts(rows):
    assert len(rows) == 119
    by = {}
    for r in rows:
        by[r["metric"]] = by.get(r["metric"], 0) + 1
    assert by == {
        "minimum_wage_bite": 66,
        "minimum_wage_coverage": 13,
        "minimum_wage_coverage_rate": 40,
    }


# --- a job is not a person -------------------------------------------------


def test_coverage_counts_jobs(rows):
    from scorecard_db.models import UnitConcept

    counts = [r for r in rows if r["metric"] == "minimum_wage_coverage"]
    assert counts
    assert all(r["unit_concept"] == "jobs" for r in counts)
    assert UnitConcept.JOBS.value == "jobs"


def test_jobs_is_never_unified_with_a_population_unit():
    """One person can hold two jobs and one household several. ASHE is an
    employer survey OF JOBS."""
    from scorecard_db.uk_aliases import DISTINCT

    assert ("lpc:jobs", "dwp_hbai:persons") in DISTINCT
    assert ("lpc:jobs", "uk_hmrc:individuals") in DISTINCT


def test_the_count_and_the_rate_are_different_metrics(rows):
    """Same reason poverty_count and poverty_rate are: a count and a rate
    answer different questions."""
    from scorecard_db.models import Metric

    assert Metric.MINIMUM_WAGE_COVERAGE != Metric.MINIMUM_WAGE_COVERAGE_RATE
    uk = [
        r
        for r in rows
        if r["geography"] == "UK" and r["period"] == 2025 and "coverage" in r["metric"]
    ]
    kinds = {r["metric"]: r["value"] for r in uk}
    assert kinds["minimum_wage_coverage"] == 2020000.0
    assert kinds["minimum_wage_coverage_rate"] == 6.6


# --- bite carries its denominator ------------------------------------------


def test_every_bite_claim_names_its_denominator(rows):
    """Bite is the rate over ASHE's median. PE-UK's world is FRS-based, so
    a PE-vs-LPC bite gap is a survey-population difference BEFORE it is an
    engine question — and the claim says so."""
    bite = [r for r in rows if r["metric"] == "minimum_wage_bite"]
    assert len(bite) == 66
    for r in bite:
        assert "ASHE median hourly wage" in r["denominator"]
        assert "FRS-based" in r["denominator"]


def test_a_bite_claim_without_a_denominator_is_refused(monkeypatch):
    from scorecard_db import ingest_lpc_minimum_wage as lpc

    raw = json.loads(EXTERNAL.read_text())
    stripped = []
    for r in raw:
        r = dict(r)
        if r["metric"] == "minimum_wage_bite":
            r.pop("denominator", None)
        stripped.append(r)
    monkeypatch.setattr(lpc, "_load", lambda: stripped)
    with pytest.raises(ValueError, match="without its denominator"):
        lpc.stage()


def test_the_survey_difference_is_the_stated_first_axis():
    source = json.loads((LANE / "source.json").read_text())
    text = source["diagnosis_upstream"]
    assert "DIFFERENT-DATA COMPARISON BEFORE IT IS ANYTHING ELSE" in text
    assert "citable-known-issue gate" in text
    assert "Underpayment" in text  # explicitly out of scope, not forgotten


# --- rate scope ------------------------------------------------------------


def test_every_claim_says_which_rate_it_is_about(rows):
    """Adult rate, an age-band rate, or all NMW/NLW rates together are
    three different questions."""
    scopes = {r["rate_scope"] for r in rows}
    assert scopes == {"adult_rate", "age_band_rate", "all_nmw_nlw_rates"}


def test_unregistered_identity_values_raise():
    from scorecard_db.uk_aliases import canon

    for axis, bad in (
        ("geography", "Greater Manchester"),
        ("subgroup", "young people"),
        ("rate_scope", "some rate"),
    ):
        with pytest.raises(ValueError, match="unregistered"):
            canon("lpc", axis, bad)


def test_lpc_region_names_map_onto_the_repo_vocabulary(rows, adapter):
    """LPC prints 'East of England' where the rest of the repo says
    'East'; aliased once, in the adapter's closed registry."""
    assert adapter.REGIONS["East of England"] == "East"
    geos = {r["geography"] for r in rows}
    assert "East of England" not in geos
    assert "East" in geos


# --- what is deliberately not read -----------------------------------------


def test_the_unread_sheets_are_tallied(tmp_path, monkeypatch, adapter):
    """191 of 193 main-annex sheets and a 349-row local-authority table
    are declared drops with reasons, not omissions."""
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    _, counts, unread = adapter.build()
    assert counts == {
        "adult_series": 54,
        "bite_by_age": 39,
        "regional_coverage": 26,
    }
    assert unread["main_annex_sheets_unread"]["sheets"] == 191
    assert unread["local_authority_coverage_rows"]["rows"] == 349
    for entry in unread.values():
        assert len(entry["reason"]) > 80


def test_local_authority_geography_is_a_stated_decision():
    readme = (LANE / "raw" / "README.md").read_text()
    assert "deliberately NOT kept" in readme
    assert "Local authority" in readme
    source = json.loads((LANE / "source.json").read_text())
    assert "nothing else can join to" in source["local_authority_note"]


def test_title_anchors_guard_against_a_reshuffled_workbook(
    adapter, tmp_path, monkeypatch
):
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    monkeypatch.setattr(adapter, "AGE_BANDS", {"16-17 (per cent)": "age_16_17"})
    with pytest.raises(RuntimeError, match="unregistered age band"):
        adapter.build()


# --- ingest ----------------------------------------------------------------


def test_stage_validates_then_maps_units(monkeypatch):
    from scorecard_db import ingest_lpc_minimum_wage as lpc

    raw = json.loads(EXTERNAL.read_text())
    bad = [dict(r) for r in raw]
    bad[0]["unit_concept"] = (
        "jobs" if bad[0]["unit_concept"] == "percent" else "percent"
    )
    monkeypatch.setattr(lpc, "_load", lambda: bad)
    with pytest.raises(ValueError, match="staged unit"):
        lpc.stage()


def test_every_claim_is_uk_and_held_out():
    from scorecard_db.ingest_lpc_minimum_wage import stage
    from scorecard_db.models import CalibrationRelationship

    scores, _ = stage()
    assert len(scores) == 119
    assert len({s.claim_id() for s in scores}) == 119
    assert all(s.conditions["country"] == "UK" for s in scores)
    assert all(
        s.calibration_relationship is CalibrationRelationship.HELD_OUT for s in scores
    )


def test_the_held_out_evidence_names_the_survey_difference():
    from scorecard_db.models import Metric
    from scorecard_db.relationships import uk_relationship

    _, evidence = uk_relationship("lpc", Metric.MINIMUM_WAGE_BITE)
    assert "employer survey of jobs" in evidence
    assert "FRS-based" in evidence
    assert "2026-08-24" in evidence


def test_full_ingest_round_trip(tmp_path):
    import sqlite3

    from scorecard_db import ScorecardDB
    from scorecard_db.ingest_lpc_minimum_wage import ingest

    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    assert ingest(db_path)["claims"] == 119
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source='lpc'"
    ).fetchone()[0]
    assert n == 119
    jobs = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source='lpc' AND unit_concept='jobs'"
    ).fetchone()[0]
    assert jobs == 13
    lane = conn.execute("SELECT * FROM lanes WHERE lane='lpc-minimum-wage'").fetchone()
    conn.close()
    assert lane["stage"] == "ingested"


def test_build_db_registers_the_step():
    import inspect

    from scorecard_db import build_db

    assert "ingest_lpc_minimum_wage.ingest" in inspect.getsource(build_db)


def test_the_lane_reaches_mission_control():
    lanes = json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    entry = next(lane for lane in lanes if lane["id"] == "lpc-minimum-wage")
    assert entry["country"] == "UK" and entry["mode"] == 1


def test_the_jobs_persons_pair_is_a_unit_axis_claim_not_a_ranking_one():
    """#91 and #92 assert that HBAI names no DISTINCT pair, on the
    stated grounds that it registers no ranking vocabulary. That
    reasoning is about the RANKING axis and stays true. This lane adds a
    pair on the UNIT axis, where both sides are registered: LPC counts
    jobs, HBAI counts persons, and one person can hold two jobs — so
    the two must never be unified or summed."""
    from scorecard_db.uk_aliases import DISTINCT, known

    assert "jobs" in known("lpc", "unit")
    assert "persons" in known("dwp_hbai", "unit")
    assert ("lpc:jobs", "dwp_hbai:persons") in DISTINCT
    # and the ranking claim those tests make is untouched
    assert not known("dwp_hbai", "quantile")
