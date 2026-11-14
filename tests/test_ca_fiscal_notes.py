"""California fiscal notes on YCTC bills (lane ca-fiscal-notes): the
committed extract is the adapter's output, the PolicyEngine reform encodes
exactly the age schedule each analysis states, and the lane owns only its
own ca_fiscal_note rows."""

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

from scorecard_db import ingest_ca_fiscal_notes as ca
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.models import ComparisonStatus, Metric

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "ca-fiscal-notes"
EXTRACT = REPO / "data" / "externals" / "ca-fiscal-notes.json"


def _load(name, path):
    # unique module names: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _campaign():
    sys.path.insert(0, str(REPO / "pipeline" / "campaign_us"))
    return _load(
        "ca_fiscal_notes_campaign",
        REPO / "pipeline" / "campaign_us" / "ca_fiscal_notes.py",
    )


def test_raw_files_match_their_recorded_hashes():
    recorded = json.loads((SRC / "source.json").read_text())["raw_sha256"]
    for name, digest in recorded.items():
        assert hashlib.sha256((SRC / "raw" / name).read_bytes()).hexdigest() == digest


def test_committed_extract_is_the_adapters_output():
    pytest.importorskip("pypdf")
    a = _load("ca_fiscal_notes_adapter", SRC / "adapter.py")
    rows = []
    for bill, name in a.BILLS.items():
        rows += a.parse_bill(bill, a._pdf_text(a.RAW / name))
    assert rows == json.loads(EXTRACT.read_text())
    assert [(r["bill"], r["period"], r["value"]) for r in rows] == [
        ("AB 397", "FY 2025-26", -220e6),
        ("AB 397", "FY 2026-27", -370e6),
        ("AB 397", "FY 2027-28", -550e6),
        ("AB 1690", "FY 2027-28", -60e6),
        ("AB 1690", "FY 2028-29", -130e6),
    ]


def test_the_reform_encodes_each_bills_age_schedule():
    campaign = _campaign()
    for row in json.loads(EXTRACT.read_text()):
        periods = campaign.BILLS[ca.bill_slug(row["bill"])][campaign.AGE]
        for year in range(2025, 2029):
            stated = row["age_schedule"].get(str(year), 6)
            encoded = next(
                (
                    age
                    for window, age in periods.items()
                    if int(window[:4]) <= year <= int(window.split(".")[1][:4])
                ),
                6,
            )
            assert encoded == stated, (row["bill"], year)


def test_claims_and_results():
    scores = ca.stage()
    assert len(scores) == 5
    assert {s.source for s in scores} == {"ca_fiscal_note"}
    assert {s.calibration_relationship for s in scores} == {CR.HELD_OUT}
    assert {s.metric for s in scores} == {Metric.REVENUE_CHANGE}
    assert {s.conditions["program"] for s in scores} == {"ca_yctc"}
    assert sorted(s.period for s in scores) == [2026, 2027, 2028, 2028, 2029]
    results = ca.results(scores)
    assert len(results) == 5
    for r in results:
        assert r.status == ComparisonStatus.CONSTRUCTED
        assert r.computed_value < 0  # a credit expansion loses revenue
        assert r.policyengine_variables == ["ca_yctc"]
        # App v3 matches the reform's parameter path in the construction
        assert "gov.states.ca.tax.income.credits.young_child.ineligible_age" in (
            r.pe_construction
        )


def test_the_registry_claim_survives():
    db = REPO / "data" / "scorecard.db"
    if not db.exists():
        pytest.skip("scorecard.db not built")
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT COALESCE(source_model, ''), COUNT(*) FROM external_scores "
        "WHERE source = 'ca_fiscal_note' GROUP BY 1"
    ).fetchall()
    conn.close()
    assert dict(rows) == {"": 1, "ftb_revenue_estimate": 5}
