"""Input-override campaign exhibits for the KFF Medicaid lane."""

import json
import sqlite3

import pytest

from scorecard_db.ingest_campaign import ingest
from scorecard_db.models import ReformRef


RUN_ID = "campaign-2026-08-18-kff-medicaid"
BUNDLE = "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z"


def _row() -> dict:
    return {
        "engine_version": "1.764.6",
        "data_bundle": BUNDLE,
        "pe_value": 77_300_000.0,
        "baseline_value": 72_300_000.0,
        "delta": 5_000_000.0,
        "status": "constructed",
        "pe_construction": "eligible minus baseline enrolled",
        "computed_at": "2026-08-18T19:00:00+00:00",
        "run_id": RUN_ID,
        "annotations": [
            "Medicaid enrollment is a point-in-time construct",
            "2024 certified Populace bundle",
        ],
        "reform_ref": {
            "framework": "policyengine_us_inputs",
            "reform": {"takes_up_medicaid_if_eligible": True},
        },
        "exhibit_context": {
            "geography": "CA",
            "program": "medicaid",
            "component": "total",
        },
        "exhibit_meta": {
            "metric": "enrollment",
            "unit_concept": "persons",
            "period": 2024,
            "time_basis": "point_in_time",
            "note": "Take-up forced to 100%",
        },
    }


def _stage(tmp_path, row: dict):
    staged = tmp_path / "staged"
    staged.mkdir()
    (staged / "kff_medicaid.jsonl").write_text(json.dumps(row) + "\n")
    return staged


def test_input_reform_exhibit_roundtrip_and_idempotency(tmp_path):
    staged = _stage(tmp_path, _row())
    db_path = tmp_path / "scorecard.db"

    first = ingest(db_path, staged_dir=staged)
    second = ingest(db_path, staged_dir=staged)
    assert (
        first
        == second
        == {
            "attached": 0,
            "exhibits": 1,
            "families": {},
            "exhibits_deferred": [],
        }
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM pe_exhibits WHERE run_id = ?", (RUN_ID,)
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    result = rows[0]

    reform = ReformRef(
        framework="policyengine_us_inputs",
        reform={"takes_up_medicaid_if_eligible": True},
    )
    assert reform.key() == "849973669b6526d6"
    assert reform.to_json() == (
        '{"baseline":null,"framework":"policyengine_us_inputs",'
        '"reform":{"takes_up_medicaid_if_eligible":true},'
        '"rulespec_ref":null}'
    )
    assert result["reform_key"] == reform.key()
    assert result["reform_json"] == reform.to_json()
    assert result["exhibit"] == "campaign:kff_medicaid"
    assert result["metric"] == "enrollment"
    assert result["unit_concept"] == "persons"
    assert result["period"] == 2024
    assert result["time_basis"] == "point_in_time"
    assert json.loads(result["conditions"]) == {
        "component": "total",
        "geography": "CA",
        "program": "medicaid",
    }
    assert result["geography"] == "CA"
    assert result["program"] == "medicaid"
    assert result["value"] == 77_300_000.0
    assert result["baseline_value"] == 72_300_000.0
    assert result["delta"] == 5_000_000.0
    assert result["engine_version"] == "1.764.6"
    assert result["data_bundle"] == BUNDLE
    assert result["computed_at"] == "2026-08-18T19:00:00+00:00"
    assert result["note"] == (
        "Take-up forced to 100% | eligible minus baseline enrolled | "
        "Medicaid enrollment is a point-in-time construct | "
        "2024 certified Populace bundle"
    )


def test_mixed_reform_and_external_match_route_rejected(tmp_path):
    row = _row()
    row["external_claim_match"] = {"claim_id": "not-used"}
    staged = _stage(tmp_path, row)

    with pytest.raises(ValueError, match="mutually exclusive"):
        ingest(tmp_path / "scorecard.db", staged_dir=staged)


def test_reform_route_requires_policyengine_us_inputs(tmp_path):
    row = _row()
    row["reform_ref"] = {
        "framework": "policyengine_us",
        "reform": {"gov.example.parameter": {"2024": True}},
    }
    staged = _stage(tmp_path, row)

    with pytest.raises(ValueError, match="requires framework"):
        ingest(tmp_path / "scorecard.db", staged_dir=staged)
