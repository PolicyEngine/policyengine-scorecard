"""Census STC individual income tax collections (lane census-stc, #176): the
committed extract is exactly what the adapter derives from raw/, the QC
catches a broken national total, and the claims, drops, relationships and
results are exact — each claim keyed to its State's own engine variable."""

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_census_stc as stc
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.models import ComparisonStatus, Metric

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "census-stc"
EXTRACT = REPO / "data" / "externals" / "census-stc.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(
        "census_stc_adapter", SRC / "adapter.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_raw_files_match_their_recorded_hashes():
    recorded = json.loads((SRC / "source.json").read_text())["raw_sha256"]
    for name, digest in recorded.items():
        assert hashlib.sha256((SRC / "raw" / name).read_bytes()).hexdigest() == digest


def test_committed_extract_is_the_adapters_output():
    a = _adapter()
    rows = []
    for year in a.YEARS:
        table = a.read_year(year)
        a.qc(year, table)
        rows += a.tidy(year, table)
    assert rows == json.loads(EXTRACT.read_text())
    assert len(rows) == a.EXPECTED_ROWS == 138


def test_qc_catches_a_broken_national_total():
    a = _adapter()
    table = a.read_year(2025)
    table["T40"]["US"] += 1
    with pytest.raises(ValueError, match="T40: US"):
        a.qc(2025, table)


def test_claims_drops_and_relationships():
    scores, drops = stc.stage()
    assert len(scores) == 132
    assert drops == {"national_total": 3, "no_engine_variable:TN": 3}
    rel = Counter((s.period, s.calibration_relationship) for s in scores)
    assert rel == {
        (2023, CR.CONSUMED_AS_TARGET): 44,
        (2024, CR.HELD_OUT): 44,
        (2025, CR.HELD_OUT): 44,
    }
    assert {s.metric for s in scores} == {Metric.TAX_COLLECTIONS}
    for s in scores:
        assert (
            s.conditions["program"] == f"{s.conditions['geography'].lower()}_income_tax"
        )
    vt = {s.period: s.value for s in scores if s.conditions["geography"] == "VT"}
    assert vt == {2023: 1_210_585_000, 2024: 1_243_069_000, 2025: 1_399_018_000}


def test_fy2023_claims_are_the_calibration_targets():
    staged = json.loads((SRC / "pe" / "us-6.2.1.json").read_text())["geographies"]
    scores, _ = stc.stage()
    fy2023 = {s.conditions["geography"]: s.value for s in scores if s.period == 2023}
    assert fy2023 == {g: v["calibration"]["target"] for g, v in staged.items()}


def test_results_attach_to_fy2023_and_fy2025_by_state_variable():
    scores, _ = stc.stage()
    claims = {s.claim_id(): s for s in scores}
    results = stc.results(scores)
    assert len(results) == 88
    assert Counter(claims[r.claim_id].period for r in results) == {2023: 44, 2025: 44}
    staged = json.loads((SRC / "pe" / "us-6.2.1.json").read_text())["geographies"]
    for r in results:
        s = claims[r.claim_id]
        geo = s.conditions["geography"]
        assert r.status == ComparisonStatus.CONSTRUCTED
        # one State's variable only: App v3 must not match other States
        assert r.policyengine_variables == [f"{geo.lower()}_income_tax"]
        assert r.computed_value == staged[geo]["state_income_tax"]
        assert r.computed_value > 0
        assert all(r.annotations)


def test_every_annotation_has_a_basis():
    spec = json.loads((SRC / "annotations.json").read_text())
    assert all(a["basis"] for a in spec["annotations"])
