"""UK benefit uprating (lane uk-benefit-uprating): the committed extract is
the adapter's output, the read-back answers each published uprating, and
the lane attaches to the HM Treasury and Resolution Foundation claims
without editing them."""

import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

from scorecard_db import ingest_uk_benefit_uprating as up
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.models import ComparisonStatus, Metric, UnitConcept

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "uk-benefit-uprating"
EXTRACT = REPO / "data" / "externals" / "uk-benefit-uprating.json"


def _load(name, path):
    # unique module names: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _adapter():
    return _load("uk_benefit_uprating_adapter", SRC / "adapter.py")


def test_raw_files_match_their_recorded_hashes():
    recorded = json.loads((SRC / "source.json").read_text())["raw_sha256"]
    for name, digest in recorded.items():
        assert hashlib.sha256((SRC / "raw" / name).read_bytes()).hexdigest() == digest


def test_committed_extract_is_the_adapters_output():
    pytest.importorskip("openpyxl")
    rows = _adapter().extract()
    assert rows == json.loads(EXTRACT.read_text())
    assert [(r["source"], r["period"], round(r["value"], 3)) for r in rows] == [
        ("ons_cpi", "2026-09", 3.5),
        ("obr_efo_economy", "2026Q3", 2.084),
    ]
    assert round(rows[1]["calendar_year_value"], 2) == 2.30


def test_ons_release_date_is_the_london_date():
    a = _adapter()
    assert a.release_date("2026-10-20T23:00:00.000Z") == "2026-10-21"
    assert a.release_date("2026-01-20T07:00:00.000Z") == "2026-01-20"


def test_a_month_that_occurs_twice_is_refused():
    a = _adapter()
    month = {"date": "2026 SEP", "value": "3.5"}
    with pytest.raises(ValueError, match="occurs 2 times"):
        a.ons_september({"months": [month, month]}, "2026 SEP")


def test_claims():
    scores = up.stage()
    assert [s.source for s in scores] == ["ons_cpi", "obr_efo_economy"]
    assert {s.metric for s in scores} == {Metric.CPI_INFLATION_RATE}
    assert {s.unit_concept for s in scores} == {UnitConcept.PERCENT}
    assert {s.period for s in scores} == {2026}
    assert {s.calibration_relationship for s in scores} == {CR.CONSUMED_AS_TARGET}
    assert scores[0].conditions["month"] == "2026-09"
    assert scores[1].conditions["quarter"] == "2026Q3"


def test_readback_provenance_and_april_2026_entries():
    staged = up._readback()
    assert staged["provenance"]["bundle_id"] == up.PE_BUNDLE
    assert staged["provenance"]["data_bundle"] == "parameter-tree"
    sa = staged["rates"]["uc_sa_single_25plus"]["values"]
    # Universal Credit Act 2025: £400.14 (2025-26) -> £424.90 (2026-27)
    assert (sa["2025"], sa["2026"]) == (400.14, 424.9)
    assert staged["protected_health_element_monthly"]["2026"] == 429.8
    assert staged["lha_freeze"]["2026"] is True


def test_cpi_claims_get_the_april_2027_basket_rise():
    staged = up._readback()
    child, lo, hi = up.basket_rise(staged, "2027")
    assert lo == pytest.approx(hi)
    results = up.own_results(up.stage(), staged)
    assert len(results) == 2
    for r in results:
        assert r.status == ComparisonStatus.CONSTRUCTED
        assert r.computed_value == pytest.approx(100 * child)
        assert "uc_child_element" in r.policyengine_variables
    assert any("points above" in note for note in results[0].annotations)


def test_readback_rises_helper():
    pipeline = _load(
        "compute_uk_uprating_readback",
        REPO / "pipeline" / "compute_uk_uprating_readback.py",
    )
    assert pipeline.rises({"2025": 100.0, "2026": 103.8}) == {
        "2026": pytest.approx(0.038)
    }


def test_lha_rise_needs_the_freeze():
    staged = {"lha_freeze": {"2026": False}}
    with pytest.raises(ValueError, match="rent-derived"):
        up.rise(staged, "lha", "2026")


def _db():
    db = REPO / "data" / "scorecard.db"
    if not db.exists():
        pytest.skip("scorecard.db not built")
    return sqlite3.connect(db)


def test_attached_results_in_the_built_db():
    conn = _db()
    rows = conn.execute(
        "SELECT s.source, r.status, COUNT(*) FROM pe_results r "
        "JOIN external_scores s USING (claim_id) WHERE r.run_id LIKE ? "
        "GROUP BY 1, 2",
        (up.RUN_PREFIX + "%",),
    ).fetchall()
    conn.close()
    assert sorted(rows) == [
        ("hm_treasury", "comparable", 4),
        ("obr_efo_economy", "constructed", 1),
        ("ons_cpi", "constructed", 1),
        ("resolution_foundation", "comparable", 11),
    ]


def test_every_hmt_uprating_claim_is_mapped():
    conn = _db()
    policies = {
        json.loads(r)["reform"]["policy"]
        for (r,) in conn.execute(
            "SELECT reform_json FROM external_scores WHERE source = 'hm_treasury' "
            "AND metric = 'benefit_uprating_rate'"
        )
    }
    conn.close()
    assert policies == set(up.HMT_MAP)
