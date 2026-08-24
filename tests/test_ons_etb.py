"""The ONS effects-of-taxes-and-benefits lane (#90).

The distributional-incidence population #68 could not have: HMT
publishes chart bars, ONS publishes observations. What is pinned here is
the reconciliation, the two identity decisions the source forces, and
the coverage facts that must ride on the claims so a `final`-income
divergence is never reported as an engine defect.
"""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LANE = ROOT / "sources" / "ons-etb"
RAW = LANE / "raw" / "tax-benefits-statistics-time-series-v3.csv"
EXTERNAL = ROOT / "data" / "externals" / "ons-etb.json"

RAW_SHA256 = "b7936b1148431d41818a28a1b173db4fcf30d6e69348accb056c872478132a3a"


@pytest.fixture(scope="module")
def rows():
    return json.loads(EXTERNAL.read_text())


@pytest.fixture(scope="module")
def adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ons_etb_adapter", LANE / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- provenance ------------------------------------------------------------


def test_raw_artifact_is_the_pinned_bytes():
    assert RAW.exists()
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == RAW_SHA256


def test_the_csvw_metadata_is_vendored_beside_it():
    meta = LANE / "raw" / "tax-benefits-statistics-time-series-v3.csv-metadata.json"
    assert meta.exists()
    d = json.loads(meta.read_text())
    assert d["dct:title"] == "Effects of Taxes and Benefits on Household Income"
    assert d["dct:issued"].startswith("2022-09-09")


def test_the_version_is_pinned_not_latest(adapter):
    """ONS's bulletin series runs later than this dataset version, so
    following latest_version would silently change the observations."""
    assert adapter.VERSION == "3"
    readme = (LANE / "raw" / "README.md").read_text()
    assert "latest_version" in readme
    assert "pinned deliberately" in readme


def test_the_stale_decile_table_is_a_recorded_non_pick():
    """The decile table this lane originally wanted is a 2015-saved .xls
    from a discontinued series. The lane says quintiles rather than
    implying decile coverage it does not have."""
    readme = (LANE / "raw" / "README.md").read_text()
    assert "deliberately NOT kept" in readme
    assert "2015" in readme
    source = json.loads((LANE / "source.json").read_text())
    assert "Quintiles, not deciles" in source["coverage_note"]


# --- reconciliation --------------------------------------------------------


def test_every_published_observation_is_a_claim_or_a_tallied_drop(
    rows, tmp_path, monkeypatch, adapter
):
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    built, rec = adapter.build()
    assert rec["observations_read"] == 5280
    assert rec["claims"] == 2640 == len(built) == len(rows)
    assert rec["deliberate_drops"] == 2640
    assert rec["claims"] + rec["deliberate_drops"] == rec["observations_read"]


def test_the_dropped_half_is_the_unbaselined_real_terms_series(
    adapter, tmp_path, monkeypatch
):
    """A real-terms figure whose price base is published nowhere cannot
    be reproduced or compared. The 2024 bulletin names CPIH excluding
    Council Tax, but that is a DIFFERENT release from this v3 dataset."""
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    _, rec = adapter.build()
    drop = rec["drops"]["price_base_unpublished"]
    assert drop["cells"] == 2640
    assert "price base" in drop["reason"].lower()
    assert "different release" in drop["reason"]
    assert all(
        r["unit_concept"] == "gbp_nominal" for r in json.loads(EXTERNAL.read_text())
    )


def test_the_grid_is_square(rows):
    """5 income concepts x 6 quintile groups x 2 statistics x 44 periods."""
    assert len({r["income_concept"] for r in rows}) == 5
    assert len({r["quantile"] for r in rows}) == 6
    assert len({r["statistic"] for r in rows}) == 2
    assert len({r["period"] for r in rows}) == 44
    by_concept = {}
    for r in rows:
        by_concept[r["income_concept"]] = by_concept.get(r["income_concept"], 0) + 1
    assert set(by_concept.values()) == {528}


# --- the mixed time dimension ----------------------------------------------


def test_calendar_and_financial_years_are_different_time_bases(rows, adapter):
    """ONS's own code list is named `financial-and-calendar-years` and it
    means it: 1977-1993 are calendar years, 1994-95 onward financial."""
    assert adapter.parse_period("1990") == (1990, "annual", None)
    assert adapter.parse_period("2020-21") == (2021, "fiscal_year", "2020-21")
    bases = {r["time_basis"] for r in rows}
    assert bases == {"annual", "fiscal_year"}
    annual = {r["period"] for r in rows if r["time_basis"] == "annual"}
    fiscal = {r["period"] for r in rows if r["time_basis"] == "fiscal_year"}
    assert max(annual) == 1993
    assert min(fiscal) == 1995  # FY1994-95 keys its END year


def test_a_financial_year_keys_its_end_year(rows):
    fy = next(r for r in rows if r["fy"] == "2020-21")
    assert fy["period"] == 2021
    assert all(r["fy"] is None for r in rows if r["time_basis"] == "annual")


def test_an_unparseable_period_raises(adapter):
    for bad in ("FYE2020", "2020/21", "2020-2021", "2029-99"):
        with pytest.raises(RuntimeError):
            adapter.parse_period(bad)


def test_unregistered_dimension_values_raise(adapter, tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    monkeypatch.setattr(adapter, "INCOME_CONCEPTS", {"Original": "original"})
    with pytest.raises(RuntimeError, match="unregistered income concept"):
        adapter.build()


# --- ingest ----------------------------------------------------------------


def test_ingest_stages_the_whole_population():
    from scorecard_db.ingest_ons_etb import stage

    scores, counts = stage()
    assert len(scores) == 2640
    assert len({s.claim_id() for s in scores}) == 2640
    assert {c: sum(v.values()) for c, v in counts.items()} == {
        "original": 528,
        "gross": 528,
        "disposable": 528,
        "post_tax": 528,
        "final": 528,
    }


def test_income_concepts_are_five_quantities_not_one(rows):
    """Each is a running total after another stage of the system. A
    claim that did not say which stage would be uninterpretable."""
    from scorecard_db.ingest_ons_etb import stage

    scores, _ = stage()
    concepts = {s.conditions["income_concept"] for s in scores}
    assert concepts == {"original", "gross", "disposable", "post_tax", "final"}
    # the same quintile, statistic and period across two concepts are two
    # DIFFERENT claims
    pair = [
        s
        for s in scores
        if s.period == 2021
        and s.conditions["quantile"] == "q1"
        and "statistic" not in s.conditions
        and s.conditions["income_concept"] in ("original", "final")
    ]
    assert len(pair) == 2
    assert pair[0].claim_id() != pair[1].claim_id()


def test_coverage_facts_ride_on_the_claim():
    """A `final`-income divergence is a COVERAGE gap — PE-UK has no
    benefits-in-kind counterpart — and must never be reportable as an
    engine defect. The claim says so, and cites where."""
    from scorecard_db.ingest_ons_etb import stage

    scores, _ = stage()
    by_concept = {}
    for s in scores:
        by_concept.setdefault(s.conditions["income_concept"], set()).add(
            s.conditions["pe_expressibility"]
        )
    assert by_concept["original"] == {"expressible"}
    assert by_concept["gross"] == {"expressible"}
    assert by_concept["disposable"] == {"expressible"}
    assert by_concept["post_tax"] == {"partial"}
    assert by_concept["final"] == {"not_expressible"}
    final = [s for s in scores if s.conditions["income_concept"] == "final"]
    assert all(
        s.conditions["action_link"].startswith("https://github.com/PolicyEngine/")
        for s in final
    )


def test_the_ranking_axis_is_recorded_and_never_unified():
    """The DISTINCT set is an audit ledger, so it is exhaustive over the
    pairs the prose claims — and names only vocabularies that exist
    (review)."""
    from scorecard_db.ingest_ons_etb import INCOME_AXIS, stage
    from scorecard_db.uk_aliases import DISTINCT, known

    scores, _ = stage()
    assert all(s.conditions["income_axis"] == INCOME_AXIS for s in scores)
    assert "equivalised_disposable" in INCOME_AXIS
    for q in range(1, 6):
        assert (f"ons_etb:q{q}", f"ukmod:q{q}") in DISTINCT
    assert ("ons_etb:q1", "resolution_foundation:quintile_1") in DISTINCT
    assert ("ons_etb:q5", "resolution_foundation:quintile_5") in DISTINCT
    assert ("ons_etb:q1", "ifs:decile_1") in DISTINCT
    # ...and HBAI is deliberately absent: it registers no quantile or
    # decile vocabulary, so there is nothing there to assert against.
    assert not any("hbai" in a + b for a, b in DISTINCT)
    assert not known("dwp_hbai", "quantile")


def test_the_adapter_pins_its_read_encoding():
    """The SHA-256 gate fixes the BYTES; a platform default could still
    change how they are decoded (review)."""
    src = (LANE / "adapter.py").read_text()
    assert 'encoding="utf-8"' in src


def test_vendored_text_artifacts_are_protected_from_eol_rewriting():
    """A Windows checkout with autocrlf on would rewrite line endings and
    break every SHA pin confusingly (reported in review)."""
    attrs = (ROOT / ".gitattributes").read_text()
    assert "*.csv -text" in attrs
    assert "*.csv-metadata.json -text" in attrs


def test_mean_is_the_absent_default():
    """models.py: statistic is present only when the value is a median."""
    from scorecard_db.ingest_ons_etb import stage

    scores, _ = stage()
    medians = [s for s in scores if s.conditions.get("statistic") == "median"]
    means = [s for s in scores if "statistic" not in s.conditions]
    assert len(medians) == len(means) == 1320


def test_every_claim_is_uk_and_held_out():
    from scorecard_db.ingest_ons_etb import stage
    from scorecard_db.models import CalibrationRelationship

    scores, _ = stage()
    assert all(s.conditions["country"] == "UK" for s in scores)
    assert all(
        s.calibration_relationship is CalibrationRelationship.HELD_OUT for s in scores
    )


def test_the_held_out_evidence_names_the_survey_difference():
    from scorecard_db.models import Metric
    from scorecard_db.relationships import uk_relationship

    _, evidence = uk_relationship("ons_etb", Metric.INCOME_STATISTIC)
    assert "FRS" in evidence
    assert "2026-08-24" in evidence
    assert "benefits-in-kind" in evidence


def test_full_ingest_round_trip(tmp_path):
    import sqlite3

    from scorecard_db import ScorecardDB
    from scorecard_db.ingest_ons_etb import ingest

    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    summary = ingest(db_path)
    assert summary["claims"] == 2640
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source='ons_etb'"
    ).fetchone()[0]
    assert n == 2640
    lane = conn.execute("SELECT * FROM lanes WHERE lane='ons-etb'").fetchone()
    conn.close()
    assert lane["stage"] == "ingested"
    assert "not_expressible" in lane["detail"]


def test_build_db_registers_the_step():
    import inspect

    from scorecard_db import build_db

    assert "ingest_ons_etb.ingest" in inspect.getsource(build_db)


def test_the_lane_reaches_mission_control():
    lanes = json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    entry = next(lane for lane in lanes if lane["id"] == "ons-etb")
    assert entry["country"] == "UK" and entry["mode"] == 1
