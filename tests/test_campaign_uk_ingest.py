"""UK campaign compute-batch ingest tests (2026-08-02).

End-to-end against a module-scoped scratch DB: US harvest (for the CPSP
register diagnoses) + UK harvest claims ingested first, then the UK
campaign batch joined on top via scorecard_db/ingest_campaign_uk (the US
day-1 families are ingest_campaign's, tested in test_campaign_ingest).
Checks the join surfaces, the #13 baseline recording (executed baselines
on results and the pre_ab2025 exhibits), the descriptive-register
statuses/diagnoses, the pentagon attachments, and idempotency.
"""

import json

import pytest

from scorecard_db import ScorecardDB, baseline_key

pytestmark = pytest.mark.filterwarnings("ignore")


@pytest.fixture(scope="module")
def campaign_db(tmp_path_factory):
    from scorecard_db import ingest_campaign_uk, ingest_harvest, ingest_uk

    path = tmp_path_factory.mktemp("campaign_uk") / "scorecard.db"
    ingest_harvest.ingest(path)
    ingest_uk.ingest(path)
    stats = ingest_campaign_uk.ingest(path)
    db = ScorecardDB(path)
    yield db, stats
    db.close()


class TestJoinCounts:
    def test_every_family_lands(self, campaign_db):
        _, stats = campaign_db
        assert stats["results"] == {
            "uk_reckoner": 23,
            "uk_free_joins": 23,
            "uk_obr_measures": 10,
            "uk_uprating": 6,
            "two_child_pentagon": 3,
            "total": 65,
        }
        assert stats["pentagon_exhibit_rows_superseded"] == 1
        assert stats["exhibits"] == 11
        assert stats["diagnoses"] == 8

    def test_only_the_two_honest_skips(self, campaign_db):
        _, stats = campaign_db
        assert len(stats["skipped"]) == 2
        assert any("LCWRA" in s for s in stats["skipped"])
        assert any("LHA" in s for s in stats["skipped"])

    def test_idempotent_reingest(self, campaign_db, tmp_path):
        db, _ = campaign_db
        from scorecard_db import ingest_campaign_uk

        before = db.conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0]
        ingest_campaign_uk.ingest(db.path)
        after = db.conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0]
        assert before == after


class TestReckonerJoins:
    def test_basic_rate_magnitude_and_provenance(self, campaign_db):
        db, _ = campaign_db
        row = db.conn.execute(
            "SELECT c.pe_value, c.value, c.pe_status, c.pe_baseline_key,"
            " c.data_bundle"
            " FROM comparisons c WHERE c.source='hmrc' AND c.period=2026"
            " AND json_extract(c.conditions,'$.measure')="
            "'Change basic rate by 1p'"
        ).fetchone()
        assert row["pe_status"] == "constructed"
        assert abs(row["pe_value"] - 7.278e9) < 5e6  # |PE delta|
        assert row["value"] == pytest.approx(6.9e9)  # HMRC magnitude
        assert row["pe_baseline_key"] == baseline_key({"policy": "current_law"})
        assert row["data_bundle"].startswith("populace-uk-2023")

    def test_all_23_runs_joined(self, campaign_db):
        db, _ = campaign_db
        n = db.conn.execute(
            "SELECT COUNT(*) FROM pe_results WHERE run_id='uk-reckoner-2026'"
        ).fetchone()[0]
        assert n == 23


class TestFreeJoins:
    def test_dwp_vintage_caveat_surfaces(self, campaign_db):
        """The campaign runner selected BECL rows by the staged end-year
        ints, so its nominal-2026 state_pension value is the FY2025-26
        cell — the result attaches to the claim the value identifies and
        says so."""
        db, _ = campaign_db
        row = db.conn.execute(
            "SELECT r.annotations, s.period FROM pe_results r"
            " JOIN external_scores s USING (claim_id)"
            " WHERE r.run_id='uk-free-joins-2026' AND s.source='dwp'"
            " AND json_extract(s.conditions,'$.program')='state_pension'"
        ).fetchone()
        assert row["period"] == 2025
        assert "end-year" in row["annotations"]

    def test_skipped_rows_are_not_computed_with_reasons(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT r.status, r.annotations FROM pe_results r"
            " JOIN external_scores s USING (claim_id)"
            " WHERE r.run_id='uk-free-joins-2026'"
            " AND json_extract(s.conditions,'$.line_item')="
            "'Pay as you earn'"
        ).fetchall()
        assert len(rows) == 2  # 3.4 accrued + 3.8 cash claims
        for r in rows:
            assert r["status"] == "not_computed"
            assert "collection channel" in r["annotations"]


class TestOBRMeasureJoins:
    def test_anchor_carries_component_sum(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT annotations FROM pe_results"
            " WHERE run_id='uk-obr-measure-reversals-2026'"
        ).fetchall()
        assert len(rows) == 10
        for r in rows:
            assert "external anchor = sum of the measure's" in (r["annotations"])


class TestUpratingChecks:
    def test_parameter_checks_are_comparable_and_close(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT c.value, c.pe_value, c.pe_status_effective,"
            " json_extract(c.conditions,'$.program') AS program"
            " FROM comparisons c"
            " WHERE c.source='resolution_foundation'"
            " AND c.metric='benefit_uprating' AND c.pe_value IS NOT NULL"
        ).fetchall()
        assert len(rows) == 4
        for r in rows:
            assert r["pe_status_effective"] == "comparable"
            # RF states rounded percentages; the tree gives exact ones.
            assert abs(r["pe_value"] - r["value"]) < 5e-4, r["program"]


class TestPentagonAttachments:
    def test_three_rows_land_with_pre_ab2025_baseline(self, campaign_db):
        db, _ = campaign_db
        from scorecard_db import baseline_key as bk

        rows = db.conn.execute(
            "SELECT r.status, r.baseline_key, s.source FROM pe_results r"
            " JOIN external_scores s USING (claim_id)"
            " WHERE r.run_id='uk-two-child-pentagon-2026'"
        ).fetchall()
        assert len(rows) == 3
        assert {r["source"] for r in rows} == {
            "resolution_foundation",
            "ukmod",
        }
        pre = bk({"policy": "pre_ab2025"})
        for r in rows:
            assert r["baseline_key"] == pre
            assert r["status"] in ("concept_mismatch", "constructed")

    def test_govt_450k_leg(self, campaign_db):
        db, _ = campaign_db
        row = db.conn.execute(
            "SELECT c.pe_value, c.value, c.pe_status FROM comparisons c"
            " WHERE c.source='resolution_foundation'"
            " AND c.metric='poverty_count_change' AND c.period=2029"
            " AND json_extract(c.conditions,'$.attribution')="
            "'Government estimate cited by RF'"
        ).fetchone()
        assert row["value"] == pytest.approx(-450000)
        assert row["pe_value"] == pytest.approx(-243108, abs=5)
        assert row["pe_status"] == "concept_mismatch"


class TestCPSPDiagnoses:
    def test_levels_carry_descriptive_diagnoses(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT c.diagnosis_class, c.action_link"
            " FROM comparisons c"
            " WHERE c.source='cpsp' AND c.period=2024"
            " AND c.metric='poverty_rate'"
            " AND c.diagnosis_class='methodological_difference'"
        ).fetchall()
        assert len(rows) == 8
        for r in rows:
            assert r["diagnosis_class"] == "methodological_difference"
            assert "populace/issues/593" in r["action_link"]


class TestTwoChildExhibits:
    def test_exhibits_record_the_executed_baseline(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT * FROM pe_exhibits WHERE exhibit='uk-two-child-limit'"
        ).fetchall()
        assert len(rows) == 11
        pre = baseline_key({"policy": "pre_ab2025"})
        for r in rows:
            assert r["baseline_key"] == pre
            reform = json.loads(r["reform_json"])
            assert reform["reform"]["policy"] == "two_child_limit_removal"
            assert reform["baseline"]["policy"] == "pre_ab2025"

    def test_headline_removal_effects(self, campaign_db):
        db, _ = campaign_db

        def delta(takeup, group):
            return db.conn.execute(
                "SELECT delta FROM pe_exhibits"
                " WHERE exhibit='uk-two-child-limit'"
                " AND metric='poverty_count_change'"
                " AND json_extract(conditions,'$.takeup')=?"
                " AND json_extract(conditions,'$.child_definition')=?",
                (takeup, group),
            ).fetchone()["delta"]

        assert delta("calibrated", "hbai_dep") == pytest.approx(-243108, abs=5)
        assert delta("entitlements_basis", "hbai_dep") == pytest.approx(-277287, abs=5)

    def test_registry_covers_every_baseline_in_use(self, campaign_db):
        db, _ = campaign_db
        assert db.unregistered_baselines() == []
