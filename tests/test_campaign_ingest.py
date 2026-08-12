"""Campaign compute-batch ingest tests (2026-08-02).

End-to-end against a session-scoped scratch DB: US harvest + UK harvest
claims ingested first, then the campaign results joined on top. Checks
the join surfaces (every family lands with exactly the expected counts),
the #13 baseline recording (executed baselines on results and the
pre_ab2025 exhibits), the descriptive-register statuses/diagnoses, and
idempotency.
"""

import json

import pytest

from scorecard_db import ScorecardDB, baseline_key

pytestmark = pytest.mark.filterwarnings("ignore")


@pytest.fixture(scope="module")
def campaign_db(tmp_path_factory):
    from scorecard_db import ingest_campaign, ingest_harvest, ingest_uk

    path = tmp_path_factory.mktemp("campaign") / "scorecard.db"
    ingest_harvest.ingest(path)
    ingest_uk.ingest(path)
    stats = ingest_campaign.ingest(path)
    db = ScorecardDB(path)
    yield db, stats
    db.close()


class TestJoinCounts:
    def test_every_family_lands(self, campaign_db):
        _, stats = campaign_db
        assert stats["results"] == {
            "uk_reckoner": 23,
            "uk_free_joins": 25,
            "uk_obr_measures": 10,
            "uk_uprating": 6,
            "tpc": 14,
            "pwbm": 2,
            "cpsp": 8,
            "jct_obbba": 1,
            "cbo_free_joins": 88,
            "total": 177,
        }
        assert stats["exhibits"] == 11
        assert stats["diagnoses"] == 8

    def test_only_the_two_honest_skips(self, campaign_db):
        _, stats = campaign_db
        assert len(stats["skipped"]) == 2
        assert any("LCWRA" in s for s in stats["skipped"])
        assert any("LHA" in s for s in stats["skipped"])

    def test_idempotent_reingest(self, campaign_db, tmp_path):
        db, _ = campaign_db
        from scorecard_db import ingest_campaign

        before = db.conn.execute(
            "SELECT COUNT(*) FROM pe_results"
        ).fetchone()[0]
        ingest_campaign.ingest(db.path)
        after = db.conn.execute(
            "SELECT COUNT(*) FROM pe_results"
        ).fetchone()[0]
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
        assert row["pe_baseline_key"] == baseline_key(
            {"policy": "current_law"}
        )
        assert row["data_bundle"].startswith("populace-uk-2023")

    def test_all_23_runs_joined(self, campaign_db):
        db, _ = campaign_db
        n = db.conn.execute(
            "SELECT COUNT(*) FROM pe_results WHERE run_id="
            "'uk-reckoner-2026'"
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
            assert "external anchor = sum of the measure's" in (
                r["annotations"]
            )


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


class TestTPCJoins:
    def test_afa_floor_bound_is_two_results_on_one_claim(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT r.computed_value FROM pe_results r"
            " JOIN external_scores s USING (claim_id)"
            " WHERE s.source='tpc'"
            " AND json_extract(s.conditions,'$.provision')="
            "'American Family Act' AND r.run_id LIKE 'tpc-t26-0029%'"
        ).fetchall()
        assert len(rows) == 2
        values = sorted(r["computed_value"] for r in rows)
        assert values[0] == pytest.approx(-132.5e9, rel=0.01)
        assert values[1] == pytest.approx(-130.7e9, rel=0.01)

    def test_view_guard_names_the_baseline_mismatch(self, campaign_db):
        """TPC's CTC options claims are scored vs current law + Senate
        Title VII; the PE runs executed enacted current law — both
        labels visible, effective status never plain agreement."""
        db, _ = campaign_db
        row = db.conn.execute(
            "SELECT claim_baseline_label, pe_baseline_label,"
            " pe_status_effective FROM comparisons"
            " WHERE source='tpc' AND period=2026"
            " AND json_extract(conditions,'$.option')='Option 2'"
            " AND json_extract(conditions,'$.provision') LIKE"
            " 'Increase CTC amount%' AND pe_value IS NOT NULL"
        ).fetchone()
        assert (
            row["claim_baseline_label"]
            == "current_law_plus_senate_obbba_title_vii"
        )
        assert row["pe_baseline_label"] == "current_law"
        assert row["pe_status_effective"] == "constructed"


class TestCPSPJoins:
    def test_levels_join_with_descriptive_diagnoses(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT c.pe_value, c.value, c.diagnosis_class, c.action_link"
            " FROM comparisons c"
            " WHERE c.source='cpsp' AND c.period=2024"
            " AND c.pe_value IS NOT NULL AND c.metric='poverty_rate'"
        ).fetchall()
        assert len(rows) == 8
        for r in rows:
            assert r["diagnosis_class"] == "methodological_difference"
            assert "populace/issues/593" in r["action_link"]
            # The documented level gap: PE above CPSP, bounded.
            assert 0 < r["pe_value"] - r["value"] < 0.06


class TestJCTAndPWBM:
    def test_ctc_extension_direction_and_scale(self, campaign_db):
        db, _ = campaign_db
        row = db.conn.execute(
            "SELECT r.computed_value, s.value FROM pe_results r"
            " JOIN external_scores s USING (claim_id)"
            " WHERE r.run_id='obbba-family-ctc-ext-2026'"
        ).fetchone()
        assert row["value"] == pytest.approx(-48.769e9)
        # PE marginal-vs-current-law runs larger than JCT's sequential
        # stack leg (named convention delta); direction must match.
        assert -120e9 < row["computed_value"] < -40e9

    def test_pwbm_ss_years(self, campaign_db):
        db, _ = campaign_db
        rows = db.conn.execute(
            "SELECT r.computed_value, s.period FROM pe_results r"
            " JOIN external_scores s USING (claim_id)"
            " WHERE r.run_id LIKE 'pwbm-ss-notax-%' ORDER BY s.period"
        ).fetchall()
        assert [r["period"] for r in rows] == [2025, 2026]
        assert rows[0]["computed_value"] == pytest.approx(
            -102.1e9, rel=0.01
        )


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

        assert delta("calibrated", "hbai_dep") == pytest.approx(
            -243108, abs=5
        )
        assert delta("entitlements_basis", "hbai_dep") == pytest.approx(
            -277287, abs=5
        )

    def test_registry_covers_every_baseline_in_use(self, campaign_db):
        db, _ = campaign_db
        assert db.unregistered_baselines() == []
