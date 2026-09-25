"""New Zealand official Budget score ingest gates."""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
from collections import Counter
from dataclasses import replace

import pytest

from nz import ingest_official_budget_scores as mod
from scorecard_db import (
    BenchmarkClass,
    CalibrationRelationship,
    ComparisonStatus,
    Metric,
    PEResult,
    ScorecardDB,
    TimeBasis,
    UnitConcept,
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _staged():
    scores = mod.stage_scores()
    by_column = {score.source_column: score for score in scores}
    assert len(by_column) == len(scores)
    return scores, by_column


def _registry_rows(db):
    return [
        tuple(row)
        for row in db.conn.execute(
            "SELECT claim_id, source, value, period, period_start, period_end, "
            "conditions, reform_json, baseline_key FROM external_scores "
            "WHERE json_extract(publication, '$.registry') = ? "
            "ORDER BY claim_id",
            (mod.REGISTRY_MARK,),
        ).fetchall()
    ]


def test_pinned_package_hashes_schema_census_and_source_tables():
    assert _sha256(mod.CLAIMS_PATH) == mod.CLAIMS_SHA256
    assert _sha256(mod.MANIFEST_PATH) == mod.MANIFEST_SHA256
    assert _sha256(mod.NOTES_PATH) == mod.NOTES_SHA256
    assert _sha256(mod.SOURCE_PAGES_PATH) == mod.SOURCE_PAGES_SHA256

    payload = mod.load_claims()
    assert payload["schema_version"] == 1
    assert payload["registry"] == mod.REGISTRY_MARK
    assert len(payload["claims"]) == 12
    assert mod._source_table_values() == (
        (79.0, 264.0, 30.0, 0.0, 0.0, 373.0),
        (0.0, 15.0, 63.0, 64.0, 63.0, 205.0),
    )


def test_claim_mapping_units_periods_sign_and_provenance():
    scores, _ = _staged()
    assert len(scores) == 12
    assert len({score.claim_id() for score in scores}) == 12
    assert Counter(score.reform.reform["policy"] for score in scores) == {
        "nz_budget_2026_temporary_iwtc_increase": 6,
        "nz_budget_2025_wff_abatement_changes": 6,
    }

    for score in scores:
        assert score.source == "nz_treasury"
        assert score.metric is Metric.OPERATING_COST_CHANGE
        assert score.unit_concept is UnitConcept.NZD
        assert score.time_basis is TimeBasis.FISCAL_YEAR
        assert score.value_kind == "nzd"
        assert score.calibration_relationship is CalibrationRelationship.HELD_OUT
        assert score.reform.framework == "policy_ref"
        assert score.reform.baseline is None
        assert score.conditions["country"] == "NZ"
        assert score.conditions["geography"] == "NZ"
        assert score.conditions["program"] == "working_for_families"
        assert score.conditions["basis"] == "forecast"
        assert score.conditions["period_basis"] == (
            "new_zealand_fiscal_year_ending_30_june"
        )
        assert score.conditions["benchmark_class"] == (
            BenchmarkClass.DIFFERENT_MODEL.value
        )
        assert score.conditions["accounting_scope"] == (
            "official_vote_operating_impact"
        )
        assert score.conditions["source_notation"] == (
            "nzd_millions_increase_dash_normalized_zero"
        )
        assert "scoreability" not in score.conditions
        assert "rulespec_module" not in score.conditions
        assert score.publication["registry"] == mod.REGISTRY_MARK
        assert score.publication["source_sha256"] in {
            "4e82abcf7ef2b605ff7cd6eb75a63826a2c6c18b84fd9cea1b2ceb9a19eda0ae",
            "e6f1e2dcd14665f0728a9f7cf5cff736637ea94152337deb108c18094c9bedec",
        }
        assert score.publication["source_excerpt_sha256"] == (mod.SOURCE_PAGES_SHA256)
        assert (
            f"rulespec-nz@{mod.RULESPEC_NZ_COMMIT}"
            in (score.publication["axiom_rulespec"])
        )
        assert (
            "fiscal_timing_bridge pending" in (score.publication["replication_status"])
        )

    iwtc = next(
        score
        for score in scores
        if score.reform.reform["policy"] == "nz_budget_2026_temporary_iwtc_increase"
    )
    assert iwtc.reform.reform["effective_from"] == "2026-04-01"
    assert iwtc.reform.reform["maximum_effective_to"] == "2027-03-31"
    assert "petrol" in iwtc.reform.reform["termination_condition"]
    wff = next(
        score
        for score in scores
        if score.reform.reform["policy"] == "nz_budget_2025_wff_abatement_changes"
    )
    assert wff.reform.reform["effective_month"] == "2026-04"
    assert "effective_from" not in wff.reform.reform
    assert {pin["id"] for pin in wff.publication["supporting_sources"]} == {
        "budget_2025_fiscal_recommendation_pdf",
        "budget_2025_vote_revenue_estimates_pdf",
    }

    annual = [score for score in scores if score.period_start is None]
    totals = [score for score in scores if score.period_start is not None]
    assert len(annual) == 10 and len(totals) == 2
    for score in annual:
        start = int(score.conditions["fy"][:4])
        assert score.period == start + 1
        assert "window_kind" not in score.conditions
    for score in totals:
        assert score.period == score.period_end
        assert score.conditions["window_kind"] == "total"
        assert "fy" not in score.conditions

    by_policy: dict[str, list] = {}
    for score in scores:
        by_policy.setdefault(score.reform.reform["policy"], []).append(score)
    for group in by_policy.values():
        annual_value = sum(score.value for score in group if score.period_start is None)
        total = next(score for score in group if score.period_start is not None)
        assert total.value == pytest.approx(annual_value)
        assert total.value >= 0


def test_only_first_tranche_replication_candidates_are_present():
    scores, _ = _staged()
    text = json.dumps(
        [score.publication | score.conditions for score in scores],
        ensure_ascii=False,
    ).lower()
    assert "in-work tax credit" in text
    assert "abatement changes" in text
    for held_back in (
        "best start",
        "accommodation supplement",
        "temporary additional support",
        "income-related rent",
    ):
        assert held_back not in text


def test_persistence_idempotency_lane_and_zero_results(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)
    path = tmp_path / "scorecard.db"
    first_summary = mod.ingest(path)
    assert first_summary["claims"] == 12
    assert first_summary["results"] == 0

    db = ScorecardDB(path)
    first = _registry_rows(db)
    assert len(first) == 12
    assert db.unregistered_baselines() == []
    assert db.conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0] == 0
    lane = db.conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
    ).fetchone()
    assert lane["stage"] == "ingested"
    assert "12 official claims" in lane["detail"]
    assert "fiscal timing" in lane["detail"]
    assert "termination bridge" in lane["detail"]
    db.close()

    assert mod.ingest(path) == first_summary
    db = ScorecardDB(path)
    assert _registry_rows(db) == first
    assert db.conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0] == 0
    db.close()


def test_claims_export_before_model_results(tmp_path, monkeypatch):
    from scorecard_db.export_populations import export

    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)
    db_path = tmp_path / "scorecard.db"
    out_path = tmp_path / "populations.json"
    mod.ingest(db_path)
    stats = export(db_path, out_path=out_path, built="2026-08-29")
    payload = json.loads(out_path.read_text())

    assert stats["rows"] == 12
    assert payload["summary"]["by_source"] == {"nz_treasury": 12}
    assert payload["summary"]["by_latest_status"] == {"not_computed": 12}
    assert all(row["country"] == "NZ" for row in payload["rows"])
    assert all(row["results"] == [] for row in payload["rows"])
    assert all(row["latest"]["status"] == "not_computed" for row in payload["rows"])
    assert {row["external_value"] for row in payload["rows"]} >= {
        0.0,
        15_000_000.0,
        373_000_000.0,
    }


def test_refresh_preserves_current_attachments_and_prunes_only_stale_claims(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    current = mod.stage_scores()[0]
    stale = replace(
        current,
        conditions={**current.conditions, "measure": "stale_registry_measure"},
        publication={**current.publication, "name": "stale registry measure"},
    )
    unrelated = replace(
        current,
        source="other_source",
        conditions={**current.conditions, "country": "US", "geography": "US"},
        publication={"registry": "other_registry", "name": "unrelated"},
    )

    def result(score):
        return PEResult(
            claim_id=score.claim_id(),
            computed_value=1.0,
            status=ComparisonStatus.CONSTRUCTED,
            engine_version="test-engine",
            data_bundle="test-bundle",
            run_id="test-run",
            computed_at="2026-08-29",
            baseline_key=score.reform.baseline_key(),
        )

    db = ScorecardDB(path)
    db.upsert_scores([stale, unrelated])
    db.add_results([result(current), result(stale), result(unrelated)])
    for score in (current, stale, unrelated):
        db.diagnose(score.claim_id(), "vintage", "test")
    db.close()

    refresh_summary = mod.ingest(path)
    assert refresh_summary["results"] == 1
    assert refresh_summary["lane_stage"] == "computed"
    db = ScorecardDB(path)
    for table in ("external_scores", "pe_results", "diagnoses"):
        assert (
            db.conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE claim_id = ?",
                (current.claim_id(),),
            ).fetchone()[0]
            == 1
        )
        assert (
            db.conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE claim_id = ?",
                (stale.claim_id(),),
            ).fetchone()[0]
            == 0
        )
        assert (
            db.conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE claim_id = ?",
                (unrelated.claim_id(),),
            ).fetchone()[0]
            == 1
        )
    lane = db.conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
    ).fetchone()
    assert lane["stage"] == "computed"
    assert "1 of 12 claims computed" in lane["detail"]
    db.close()


def test_refresh_uses_latest_result_and_marks_a_computed_lane_regressed(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    score = mod.stage_scores()[0]
    db = ScorecardDB(path)
    db.add_results(
        [
            PEResult(
                claim_id=score.claim_id(),
                computed_value=1.0,
                status=ComparisonStatus.CONSTRUCTED,
                engine_version="test-engine",
                data_bundle="test-bundle",
                run_id="older-run",
                computed_at="2026-08-28",
                baseline_key=score.reform.baseline_key(),
            )
        ]
    )
    db.close()

    first_refresh = mod.ingest(path)
    assert first_refresh["results"] == 1
    assert first_refresh["computed_claims"] == 1
    assert first_refresh["lane_stage"] == "computed"

    db = ScorecardDB(path)
    db.add_results(
        [
            PEResult(
                claim_id=score.claim_id(),
                computed_value=None,
                status=ComparisonStatus.NOT_COMPUTED,
                engine_version="test-engine",
                data_bundle="test-bundle",
                run_id="newer-run",
                computed_at="2026-08-29",
                baseline_key=score.reform.baseline_key(),
            )
        ]
    )
    db.close()

    second_refresh = mod.ingest(path)
    assert second_refresh["results"] == 1
    assert second_refresh["computed_claims"] == 0
    assert second_refresh["lane_stage"] == "regressed"
    db = ScorecardDB(path)
    lane = db.conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
    ).fetchone()
    assert lane["stage"] == "regressed"
    assert "0 of 12 claims retain results" in lane["detail"]
    db.close()


def test_lane_mirror_failure_is_recoverable_by_idempotent_retry(tmp_path, monkeypatch):
    path = tmp_path / "scorecard.db"

    def fail_sync(*args, **kwargs):
        raise OSError("simulated lane mirror failure")

    monkeypatch.setattr(mod, "sync_lane_feed", fail_sync)
    with pytest.raises(OSError, match="lane mirror failure"):
        mod.ingest(path)
    db = ScorecardDB(path)
    assert len(_registry_rows(db)) == 12
    assert (
        db.conn.execute(
            "SELECT stage FROM lanes WHERE lane = ?", (mod.LANE_ID,)
        ).fetchone()[0]
        == "ingested"
    )
    db.close()

    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)
    assert mod.ingest(path)["claims"] == 12
    db = ScorecardDB(path)
    assert len(_registry_rows(db)) == 12
    db.close()


def test_hash_schema_census_and_value_drift_fail_loudly(tmp_path):
    drifted = tmp_path / "claims.json"
    drifted.write_text(mod.CLAIMS_PATH.read_text() + "\n")
    with pytest.raises(ValueError, match=r"(?i)claims.*sha"):
        mod.load_claims(drifted)

    truncated = copy.deepcopy(mod.load_claims())
    truncated["claims"].pop()
    with pytest.raises(ValueError, match=r"(?i)census|exactly 12"):
        mod.stage_scores(truncated)

    unknown = copy.deepcopy(mod.load_claims())
    unknown["claims"][0]["unmapped_field"] = "invented"
    with pytest.raises(ValueError, match=r"(?i)schema"):
        mod.stage_scores(unknown)

    drifted_value = copy.deepcopy(mod.load_claims())
    drifted_value["claims"][0]["value_nzd_millions"] = 80.0
    drifted_value["claims"][0]["source_display"] = "80.000"
    with pytest.raises(ValueError, match=r"(?i)annual row drifted|source-page"):
        mod.stage_scores(drifted_value)


def test_manifest_boolean_and_vendored_excerpt_gates(tmp_path):
    rows = [json.loads(line) for line in mod.MANIFEST_PATH.read_text().splitlines()]
    rows[0]["stored_in_repo"] = "false"
    drifted = tmp_path / "manifest.jsonl"
    drifted.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(ValueError, match=r"true or false"):
        mod.load_manifest(drifted, verify_sha=False)

    excerpt = mod.SOURCE_PAGES_PATH.read_text()
    assert "79.000" in excerpt and "205.000" in excerpt


def test_nonzero_capital_total_cannot_be_silently_discarded(tmp_path, monkeypatch):
    lines = mod.SOURCE_PAGES_PATH.read_text().splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith("Revenue"))
    assert lines[index].rstrip().endswith("-")
    lines[index] = lines[index].rstrip()[:-1] + "1.000"
    drifted = tmp_path / "source-pages.txt"
    drifted.write_text("\n".join(lines) + "\n")
    monkeypatch.setattr(mod, "SOURCE_PAGES_PATH", drifted)
    with pytest.raises(ValueError, match=r"(?i)capital total"):
        mod._source_table_values()


def test_write_failure_rolls_back_whole_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)
    path = tmp_path / "scorecard.db"
    first_summary = mod.ingest(path)
    db = ScorecardDB(path)
    first = _registry_rows(db)
    db.close()

    real = ScorecardDB.score_row
    calls = {"n": 0}

    def sabotaged(score):
        row = real(score)
        calls["n"] += 1
        if calls["n"] == 5:
            return row[:17] + ("bogus_status",) + row[18:]
        return row

    monkeypatch.setattr(ScorecardDB, "score_row", staticmethod(sabotaged))
    with pytest.raises(sqlite3.IntegrityError):
        mod.ingest(path)

    db = ScorecardDB(path)
    assert _registry_rows(db) == first
    db.close()
    monkeypatch.setattr(ScorecardDB, "score_row", staticmethod(real))
    assert mod.ingest(path) == first_summary
