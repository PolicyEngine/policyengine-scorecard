"""Belgian 2026 PIT-reform registry ingest gates."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter

import pytest

from be import ingest_pit_reform_2026 as mod
from scorecard_db import (
    BenchmarkClass,
    CalibrationRelationship,
    ComparisonStatus,
    Metric,
    ScorecardDB,
    TimeBasis,
    UnitConcept,
    baseline_key,
)


POLICY = "be_pit_reform_2026_07_15"
OFFICIAL_VALUES = {
    "spf_finances": (2030, -4_000_000_000.0),
    "cour_des_comptes": (2030, -5_000_000_000.0),
}
PE_VALUES = {
    2026: -513_450_000.0,
    2027: -456_510_000.0,
    2028: -779_680_000.0,
    2029: -2_457_460_000.0,
    2030: -4_156_010_000.0,
}
SOURCE_COUNTS = {
    "spf_finances": 1,
    "cour_des_comptes": 1,
    "policyengine": 5,
}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _staged():
    scores, results, summary = mod.stage_all()
    by_source_column = {score.source_column: score for score in scores}
    assert len(by_source_column) == len(scores)
    return scores, results, summary, by_source_column


def _publication_text(score):
    return json.dumps(score.publication, sort_keys=True, ensure_ascii=False)


def test_vendored_hashes_schema_and_exact_accounting():
    assert _sha256(mod.CLAIMS_PATH) == mod.CLAIMS_SHA256
    assert _sha256(mod.MANIFEST_PATH) == mod.MANIFEST_SHA256

    payload = mod.load_claims()
    assert payload["reform"]["policy"] == POLICY
    assert len(payload["claims"]) == 7

    scores, results, summary, _ = _staged()
    assert summary == {
        "claims": 7,
        "results": 7,
        "sources": 3,
        "self_attachments": 5,
        "official_cross_attachments": 2,
    }
    assert len(scores) == len(results) == 7
    assert Counter(score.source for score in scores) == SOURCE_COUNTS


def test_claim_values_identity_and_period_doctrine():
    scores, _, _, _ = _staged()
    assert {score.reform.reform["policy"] for score in scores} == {POLICY}
    assert mod.REGISTRY_MARK == "be_pit_reform_2026"

    for score in scores:
        assert score.publication["registry"] == mod.REGISTRY_MARK
        assert score.metric is Metric.REVENUE_CHANGE
        assert score.unit_concept is UnitConcept.EUR
        assert score.time_basis is TimeBasis.ANNUAL
        assert score.value_kind == "eur"
        assert score.calibration_relationship is CalibrationRelationship.HELD_OUT
        assert score.conditions["country"] == "BE"
        assert score.conditions["geography"] == "BE"

    official = {
        score.source: score for score in scores if score.source != "policyengine"
    }
    assert set(official) == set(OFFICIAL_VALUES)
    for source, (period, value) in OFFICIAL_VALUES.items():
        score = official[source]
        assert (score.period, score.value) == (period, pytest.approx(value))
        assert score.conditions["basis"] == "forecast"
        assert score.conditions["benchmark_class"] == (
            BenchmarkClass.DIFFERENT_MODEL.value
        )
        assert score.conditions["period_basis"] == (
            "horizon_2030_income_vs_assessment_year_unspecified"
        )
        assert "assessment_year" not in score.conditions

    spf_text = _publication_text(official["spf_finances"]).lower()
    assert "methodology unpublished" in spf_text
    assert "assessment-year-2023 microdata" in spf_text
    court_text = _publication_text(official["cour_des_comptes"]).lower()
    assert "secondary citation" in court_text
    assert "advice document is not pinned" in court_text

    pe = {score.period: score for score in scores if score.source == "policyengine"}
    assert set(pe) == set(PE_VALUES)
    for income_year, value in PE_VALUES.items():
        score = pe[income_year]
        assert score.value == pytest.approx(value)
        assert score.conditions["benchmark_class"] == (
            BenchmarkClass.SAME_ASSUMPTIONS.value
        )
        assert score.conditions["period_basis"] == "income_year"
        assert score.conditions["assessment_year"] == str(income_year + 1)
        assert score.conditions["behavioral_response"] == "none"


def test_every_number_carries_its_manifest_pins():
    payload = mod.load_claims()
    manifest = {
        row["id"]: row
        for row in (
            json.loads(line)
            for line in mod.MANIFEST_PATH.read_text().splitlines()
            if line.strip()
        )
    }
    _, _, _, scores = _staged()

    assert set(scores) == {row["id"] for row in payload["claims"]}
    for row in payload["claims"]:
        text = _publication_text(scores[row["id"]])
        assert row["source_pins"]
        for pin_id in row["source_pins"]:
            assert pin_id in manifest
            assert pin_id in text
            assert manifest[pin_id]["sha256"] in text

    pe_text = "\n".join(
        _publication_text(score)
        for score in scores.values()
        if score.source == "policyengine"
    )
    assert "3d9f690" in pe_text


def test_five_self_results_and_two_annotated_cross_attachments():
    scores, results, _, _ = _staged()
    score_by_claim = {score.claim_id(): score for score in scores}
    result_by_claim = {result.claim_id: result for result in results}
    assert set(result_by_claim) == set(score_by_claim)
    assert {result.run_id for result in results} == {"be-pit-reform-2026@3d9f690"}
    assert all(result.baseline_key is not None for result in results)
    assert {result.baseline_key for result in results} == {
        baseline_key(mod.AXIOM_BASELINE)
    }

    self_results = [
        result
        for result in results
        if score_by_claim[result.claim_id].source == "policyengine"
    ]
    assert len(self_results) == 5
    for result in self_results:
        claim = score_by_claim[result.claim_id]
        assert result.status is ComparisonStatus.COMPARABLE
        assert result.computed_value == pytest.approx(claim.value)

    official_results = [
        result
        for result in results
        if score_by_claim[result.claim_id].source != "policyengine"
    ]
    assert len(official_results) == 2
    for result in official_results:
        claim = score_by_claim[result.claim_id]
        assert result.status is ComparisonStatus.CONSTRUCTED
        assert result.computed_value == pytest.approx(PE_VALUES[2030])
        annotation = " ".join(result.annotations).lower()
        assert "2030" in annotation
        assert "income year" in annotation
        assert "assessment year" in annotation
        assert "unresolved" in annotation
        recipe = json.loads(result.pe_construction)
        assert recipe["kind"] == "official_horizon_cross_attachment"
        assert recipe["claim_period"] == claim.period == 2030
        assert recipe["computed_income_year"] == 2030
        assert recipe["computed_assessment_year"] == 2031
        assert recipe["claim_period_basis"] == (
            "horizon_2030_income_vs_assessment_year_unspecified"
        )
        assert "unresolved" in recipe["period_relationship"]


def _registry_rows(db):
    return {
        "claims": [
            tuple(row)
            for row in db.conn.execute(
                "SELECT claim_id, source, value, period, conditions, reform_json, "
                "baseline_key FROM external_scores "
                "WHERE json_extract(reform_json, '$.reform.policy') = ? "
                "ORDER BY claim_id",
                (POLICY,),
            ).fetchall()
        ],
        "results": [
            tuple(row)
            for row in db.conn.execute(
                "SELECT r.claim_id, r.computed_value, r.status, r.engine_version, "
                "r.data_bundle, r.pe_construction, r.run_id, r.computed_at, "
                "r.annotations, r.baseline_key FROM pe_results r "
                "JOIN external_scores s USING (claim_id) "
                "WHERE json_extract(s.reform_json, '$.reform.policy') = ? "
                "ORDER BY r.claim_id",
                (POLICY,),
            ).fetchall()
        ],
    }


def test_persistence_idempotency_lane_and_baseline_registration(tmp_path, monkeypatch):
    if hasattr(mod, "sync_lane_feed"):
        monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: None)

    path = tmp_path / "scorecard.db"
    first_summary = mod.ingest(path)
    assert first_summary["claims"] == 7
    assert first_summary["results"] == 7

    db = ScorecardDB(path)
    first = _registry_rows(db)
    assert len(first["claims"]) == len(first["results"]) == 7
    assert Counter(row[1] for row in first["claims"]) == SOURCE_COUNTS
    assert db.unregistered_baselines() == []
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM baselines WHERE baseline_key = ? "
            "AND label = 'axiom_be_pit_v05h_same_year_indexed_current_law'",
            (baseline_key(mod.AXIOM_BASELINE),),
        ).fetchone()[0]
        == 1
    )
    labels = {
        row[0]
        for row in db.conn.execute(
            "SELECT label FROM baselines WHERE label LIKE '%pit%baseline%2026%' "
            "OR label = 'axiom_be_pit_v05h_same_year_indexed_current_law'"
        ).fetchall()
    }
    assert {
        "spf_finances_internal_pit_baseline_2026",
        "cour_des_comptes_pit_baseline_2026_unspecified",
        "axiom_be_pit_v05h_same_year_indexed_current_law",
    } <= labels
    lane = db.conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
    ).fetchone()
    assert lane["stage"] == "computed"
    assert "7 claims" in lane["detail"] and "7 results" in lane["detail"]
    db.close()

    second_summary = mod.ingest(path)
    assert second_summary["claims"] == 7
    assert second_summary["results"] == 7
    db = ScorecardDB(path)
    assert _registry_rows(db) == first
    assert db.unregistered_baselines() == []
    db.close()


def test_claims_hash_drift_fails_loudly(tmp_path):
    drifted = tmp_path / "claims.json"
    drifted.write_text(mod.CLAIMS_PATH.read_text() + "\n")
    with pytest.raises(ValueError, match=r"(?i)(claims.*sha|sha.*claims)"):
        mod.load_claims(drifted, verify_sha=True)


def test_manifest_hash_drift_fails_before_staging(tmp_path):
    drifted = tmp_path / "manifest.jsonl"
    drifted.write_text(mod.MANIFEST_PATH.read_text() + "\n")
    with pytest.raises(ValueError, match=r"(?i)(manifest.*sha|sha.*manifest)"):
        mod.load_claims(manifest_path=drifted)


def test_payload_schema_and_census_drift_fail_loudly():
    truncated = copy.deepcopy(mod.load_claims())
    truncated["claims"].pop()
    with pytest.raises(ValueError, match=r"(?i)(account|census|exactly|7 claims)"):
        mod.stage_all(truncated)

    unknown = copy.deepcopy(mod.load_claims())
    unknown["claims"][0]["unmapped_contract_term"] = "invented"
    with pytest.raises(ValueError, match=r"(?i)(schema|unknown|unexpected|unmapped)"):
        mod.stage_all(unknown)
