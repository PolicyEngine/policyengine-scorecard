"""Belgium JRC country-report adapter and persistence gates."""

from __future__ import annotations

import dataclasses
import json

import pytest

from be import ingest_jrc_country_report as mod
from be.aliases import SOURCE, canon
from be.worlds import (
    AXIOM_BE_2026_DEMO_WORLD,
    EUROMOD_BE_2022_WORLD,
    EUROMOD_BE_2023_WORLD,
)
from scorecard_db import (
    STANDARD_CONDITIONS,
    BenchmarkClass,
    CalibrationRelationship,
    ComparisonStatus,
    Metric,
    ReformRef,
    ScorecardDB,
    UnitConcept,
    baseline_key,
)
from scorecard_db.build_db import content_hash


EXPECTED_CLAIM_IDS = {
    "a3_4_national_income_tax_euromod_2023": "50e2715b1ccbe7b9b053",
    "a3_4_employee_sics_euromod_2023": "66f852422521a5626ce4",
    "a3_6_child_benefits_euromod_2023": "542478af9ceeb389ab79",
    "a3_7_gini_euromod_2022": "0c155b086b4ed9cf478c",
    "a3_8_poverty_60_total_euromod_2022": "7c694ed444ac77f9a56f",
}


def _staged():
    scores, ledger, summary = mod.stage_all()
    return {score.source_column: score for score in scores}, ledger, summary


def test_vendored_source_hash_and_exact_5_7_6_accounting():
    assert mod._sha256(mod.SOURCE_CSV) == mod.CSV_SHA256
    assert mod._sha256(mod.SOURCE_MANIFEST) == mod.MANIFEST_SHA256
    scores, ledger, summary = _staged()
    assert summary == {
        "claims": 5,
        "ledger_facts": 7,
        "ratios_dispositioned": 6,
        "source_records": 18,
    }
    assert len(scores) == 5
    assert len(ledger) == 7
    assert EXPECTED_CLAIM_IDS == {
        source_column: score.claim_id() for source_column, score in scores.items()
    }


def test_claim_values_units_worlds_and_semantic_pins():
    scores, _, _ = _staged()
    expected = {
        "a3_4_national_income_tax_euromod_2023": (
            Metric.TAX_LIABILITY,
            UnitConcept.EUR,
            2023,
            77_531_000_000.0,
        ),
        "a3_4_employee_sics_euromod_2023": (
            Metric.TAX_LIABILITY,
            UnitConcept.EUR,
            2023,
            28_861_000_000.0,
        ),
        "a3_6_child_benefits_euromod_2023": (
            Metric.BENEFIT_COST,
            UnitConcept.EUR,
            2023,
            7_454_000_000.0,
        ),
        "a3_7_gini_euromod_2022": (
            Metric.GINI,
            UnitConcept.INDEX_0_1,
            2022,
            0.2228,
        ),
        "a3_8_poverty_60_total_euromod_2022": (
            Metric.POVERTY_RATE,
            UnitConcept.SHARE,
            2022,
            0.1123,
        ),
    }
    for source_column, (metric, unit, period, value) in expected.items():
        score = scores[source_column]
        assert (score.metric, score.unit_concept, score.period) == (
            metric,
            unit,
            period,
        )
        assert score.value == pytest.approx(value)
        assert score.conditions["country"] == "BE"
        assert score.conditions["geography"] == "BE"
        assert score.conditions["benchmark_class"] == (
            BenchmarkClass.DIFFERENT_MODEL.value
        )
        assert score.conditions["policy_system_year"] == str(period)
        assert score.conditions["population_frame"] == "private_households"
        assert score.conditions["input_database"] == "be_2022_c1_silc2022_income2021"
        assert score.source_model == "EUROMOD BE (J1.0+)"
        assert "BE_2022_c1" in score.publication["period_semantics"]
        assert "income reference year" in score.publication["period_semantics"]
        assert score.calibration_relationship is CalibrationRelationship.HELD_OUT
        assert set(score.conditions) <= STANDARD_CONDITIONS
        assert score.reform.baseline == (
            EUROMOD_BE_2022_WORLD if period == 2022 else EUROMOD_BE_2023_WORLD
        )
        assert "not the SILC collection year" in score.publication["period_semantics"]

    gini = scores["a3_7_gini_euromod_2022"]
    poverty = scores["a3_8_poverty_60_total_euromod_2022"]
    for score in (gini, poverty):
        assert score.conditions["income_concept"] == (
            "equivalised_household_standard_disposable_income"
        )
        assert score.conditions["housing_costs"] == "not_deducted"
        assert score.conditions["equivalisation"] == "modified_oecd"
        assert (
            "verified against the report itself"
            in score.publication["equivalisation_note"]
        )
        assert "p. 104" in score.publication["equivalisation_note"]
    assert poverty.conditions["poverty_line"] == "relative_60_median"
    assert poverty.conditions["subgroup"] == "total"


def test_closed_identity_registry_rejects_unknowns():
    assert canon(SOURCE, "publisher", SOURCE) == SOURCE
    assert canon(SOURCE, "model", mod.SOURCE_MODEL) == mod.SOURCE_MODEL
    with pytest.raises(ValueError, match="unregistered metric"):
        canon(SOURCE, "metric", "new_metric")
    with pytest.raises(ValueError, match="unregistered population_scope"):
        canon(SOURCE, "population_scope", "workerish")
    with pytest.raises(ValueError, match="unregistered model"):
        canon(SOURCE, "model", "EUROMOD maybe")


def test_external_rows_route_only_to_ledger_and_ratios_are_recomputed():
    scores, ledger, _ = _staged()
    assert all("_euromod_" in score.source_column for score in scores.values())
    assert all(
        "_external_" in row["source_column"]
        or row["source_column"] == "a3_6_unemployment_benefits_euromod_2023"
        for row in ledger
    )
    assert all(row["routing"].startswith("ledger") for row in ledger)
    assert all(
        row["benchmark_class"] == BenchmarkClass.ADMINISTRATIVE_FACT.value
        for row in ledger
        if row["conditions"]["series"] == "external"
    )
    assert {row["conditions"]["series"] for row in ledger} == {
        "external",
        "euromod_non_simulated_input",
    }
    assert not any("_ratio_" in row["source_column"] for row in ledger)
    # The ratio validator proves every dropped cell is the rounded published
    # model/statistical quotient; a source mutation cannot pass silently.
    rows = mod._load_rows()
    mod._validate_ratios(rows)
    ratio = next(
        r for r in rows if r["value_id"] == "a3_4_national_income_tax_ratio_2023"
    )
    ratio["value"] = "1.13"
    with pytest.raises(ValueError, match="rounded euromod/external"):
        mod._validate_ratios(rows)


def test_ledger_and_staging_are_deterministic():
    first_scores, first_ledger, first_summary = mod.stage_all()
    next_scores, next_ledger, next_summary = mod.stage_all()
    assert first_summary == next_summary
    assert first_ledger == next_ledger
    assert [s.claim_id() for s in first_scores] == [s.claim_id() for s in next_scores]


def test_source_census_drift_fails_loudly():
    rows = mod._load_rows()
    with pytest.raises(ValueError, match="source census drifted"):
        mod.stage_all(rows[:-1])


def test_manifest_drift_fails_before_staging(tmp_path, monkeypatch):
    drifted = tmp_path / "manifest.yaml"
    drifted.write_text(mod.SOURCE_MANIFEST.read_text() + "# drift\n")
    monkeypatch.setattr(mod, "SOURCE_MANIFEST", drifted)
    with pytest.raises(ValueError, match="manifest SHA-256 drifted"):
        mod.stage_all()


def test_honesty_first_attachments_name_every_gap():
    scores, _, _ = mod.stage_all()
    results = mod.stage_results(scores)
    assert len(results) == 2
    by_claim = {result.claim_id: result for result in results}
    source_by_claim = {score.claim_id(): score.source_column for score in scores}
    assert {source_by_claim[claim_id] for claim_id in by_claim} == set(mod._ATTACHMENTS)
    values = {source_by_claim[r.claim_id]: r.computed_value for r in results}
    assert values == {
        "a3_4_national_income_tax_euromod_2023": pytest.approx(23_284_895_966.30996),
        "a3_4_employee_sics_euromod_2023": pytest.approx(20_874_276_470.798096),
    }
    for result in results:
        assert result.status is ComparisonStatus.CONCEPT_MISMATCH
        assert result.baseline_key == baseline_key(AXIOM_BE_2026_DEMO_WORLD)
        annotation = result.annotations[0]
        assert mod.DEMO_BANNER in annotation
        assert "CY2026" in annotation and "CY2023" in annotation
        assert "US survey support" in annotation and "Belgian SILC" in annotation
        assert "worker slice" in annotation and "national all-" in annotation
        assert "different_model" in annotation
        recipe = json.loads(result.pe_construction)
        assert recipe["attachment_class"] == "concept_mismatch"
        assert recipe["computed_period"] == 2026
        assert recipe["claim_period"] == 2023


def _patch_repo_outputs(monkeypatch, tmp_path):
    monkeypatch.setattr(mod, "LEDGER_PATH", tmp_path / "be-ledger.jsonl")
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *args, **kwargs: 1)


def _logical_dump(path):
    db = ScorecardDB(path)
    out = {
        table: [
            tuple(row)
            for row in db.conn.execute(
                f"SELECT * FROM {table} ORDER BY "
                + ("id" if table == "pe_results" else "1")
            ).fetchall()
        ]
        for table in ("external_scores", "pe_results", "baselines", "lanes")
    }
    db.close()
    return out


def test_ingest_persists_boundary_baselines_and_lane(tmp_path, monkeypatch):
    _patch_repo_outputs(monkeypatch, tmp_path)
    db_path = tmp_path / "be.db"
    summary = mod.ingest(db_path)
    assert summary["claims"] == 5
    assert summary["ledger_facts"] == 7
    assert summary["attachments"] == 2
    db = ScorecardDB(db_path)
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE source = ?", (SOURCE,)
        ).fetchone()[0]
        == 5
    )
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE source = ? "
            "AND source_column = 'a3_6_unemployment_benefits_euromod_2023'",
            (SOURCE,),
        ).fetchone()[0]
        == 0
    )
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM pe_results r JOIN external_scores s USING (claim_id) "
            "WHERE s.source = ?",
            (SOURCE,),
        ).fetchone()[0]
        == 2
    )
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE source = ? "
            "AND (source_column LIKE '%_external_%' OR source_column LIKE '%_ratio_%')",
            (SOURCE,),
        ).fetchone()[0]
        == 0
    )
    assert (
        db.conn.execute(
            "SELECT stage FROM lanes WHERE lane = ?", (mod.LANE_ID,)
        ).fetchone()[0]
        == "computed"
    )
    labels = {
        row[0]
        for row in db.conn.execute(
            "SELECT label FROM baselines WHERE label LIKE '%be_%'"
        ).fetchall()
    }
    assert {
        "euromod_be_2025_current_law_2022",
        "euromod_be_2025_current_law_2023",
        "axiom_be_rulespec_current_law_demo_2026",
    } <= labels
    compared = db.conn.execute(
        "SELECT pe_status, pe_status_effective, claim_baseline_label, "
        "pe_baseline_label FROM comparisons WHERE source = ? AND pe_value IS NOT NULL",
        (SOURCE,),
    ).fetchall()
    assert len(compared) == 2
    assert all(row[0] == row[1] == "concept_mismatch" for row in compared)
    assert all(row[2] != row[3] for row in compared)
    db.close()
    ledger_lines = (tmp_path / "be-ledger.jsonl").read_text().splitlines()
    assert len(ledger_lines) == 7


def test_unregistered_baseline_poison_rolls_back_everything(tmp_path, monkeypatch):
    _patch_repo_outputs(monkeypatch, tmp_path)
    db_path = tmp_path / "be.db"
    mod.ingest(db_path)
    before = _logical_dump(db_path)
    real_stage = mod.stage_all
    poison_world = {"policy": "never_registered_be_world"}

    def poisoned():
        scores, ledger, summary = real_stage()
        bad = dataclasses.replace(
            scores[0],
            source_column="poison",
            conditions=scores[0].conditions | {"data_vintage": "poison"},
            reform=ReformRef(framework="baseline", baseline=poison_world),
        )
        return scores + [bad], ledger, summary

    monkeypatch.setattr(mod, "stage_all", poisoned)
    with pytest.raises(ValueError, match="not in the registry"):
        mod.ingest(db_path)
    after = _logical_dump(db_path)
    assert after == before
    db = ScorecardDB(db_path)
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM baselines WHERE baseline_key = ?",
            (baseline_key(poison_world),),
        ).fetchone()[0]
        == 0
    )
    db.close()


def test_two_be_only_builds_have_identical_content_hash(tmp_path, monkeypatch):
    _patch_repo_outputs(monkeypatch, tmp_path)
    first = tmp_path / "first.db"
    second = tmp_path / "second.db"
    mod.ingest(first)
    mod.ingest(second)
    assert content_hash(first) == content_hash(second)


def test_unemployment_euromod_value_is_ledger_routed_survey_input():
    """Sol review of #82, blocker 3: Table A3.6 marks bun Simulated=N (p. 127)
    and bun_be is off in the baseline (p. 24) — the 11,706 is the SILC
    income-year-2021 base of 10,416 uprated, not executed model output."""
    scores, ledger, _ = mod.stage_all()
    assert all(
        score.source_column != "a3_6_unemployment_benefits_euromod_2023"
        for score in scores
    )
    survey = [
        fact
        for fact in ledger
        if fact["source_column"] == "a3_6_unemployment_benefits_euromod_2023"
    ]
    assert len(survey) == 1
    fact = survey[0]
    assert fact["benchmark_class"] == "survey_statistic"
    assert fact["conditions"]["series"] == "euromod_non_simulated_input"
    assert fact["conditions"]["benchmark_class"] == "survey_statistic"
    assert "policy_system_year" not in fact["conditions"]
    assert "population_frame" not in fact["conditions"]
    assert fact["underlying_issuer"] == "EU-SILC"
    assert fact["period_semantics"] == "simulation_year_of_uprated_survey_input"
    assert fact["conditions"]["simulation_year"] == "2023"
    assert "reference_year" not in fact["conditions"]
    assert "Simulated=N" in fact["routing"]
    assert "10,416" in fact["publication"]["period_semantics"]


def test_external_facts_carry_underlying_issuers():
    """Sol review of #82, finding 5: the report's own source table names the
    original issuers (pp. 120-126; Gini/AROP comparators are EU-SILC-based
    per p. 104). JRC stays the secondary publisher."""
    _, ledger, _ = mod.stage_all()
    issuers = {
        fact["source_column"]: fact["underlying_issuer"]
        for fact in ledger
        if fact["conditions"]["series"] == "external"
    }
    assert issuers == {
        "a3_4_national_income_tax_external_2023": "NBB",
        "a3_4_employee_sics_external_2023": "NBB",
        "a3_6_child_benefits_external_2023": "NBB",
        "a3_6_unemployment_benefits_external_2023": "RVA",
        "a3_7_gini_external_2022": "EU-SILC",
        "a3_8_poverty_60_total_external_2022": "EU-SILC",
    }
    assert all(
        fact["publisher"] == "European Commission Joint Research Centre"
        for fact in ledger
    )


def test_lane_note_carries_the_5_7_6_accounting(tmp_path, monkeypatch):
    """Sol delta review of #82: a semantically stale lane note passed the
    byte-drift gate; pin the persisted detail to the real accounting."""
    _patch_repo_outputs(monkeypatch, tmp_path)
    db_path = tmp_path / "be.db"
    mod.ingest(db_path)
    db = ScorecardDB(db_path)
    note = db.conn.execute(
        "SELECT detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
    ).fetchone()[0]
    db.close()
    assert "5 model claims" in note
    assert "7 Ledger facts" in note
    assert "survey input" in note
