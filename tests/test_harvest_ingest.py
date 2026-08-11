"""Per-adapter tests for the 2026-08-02 overnight-harvest ingest.

Spot-check values are the COLLATION headliners, re-verified against the
sha256-manifested source artifacts during ingest (see the PR's validation
report). Staged inputs are vendored at sources/harvest-2026-08-02/.
"""

import pytest

from scorecard_db import (
    BASELINE,
    CalibrationRelationship,
    Metric,
    ReformRef,
    ScorecardDB,
    UnitConcept,
)
from scorecard_db.harvest import HARVEST

pytestmark = pytest.mark.skipif(
    not HARVEST.exists(), reason="vendored harvest staging not present"
)


@pytest.fixture(scope="module")
def jct():
    from scorecard_db.ingest_jct import stage_scores

    return stage_scores()


@pytest.fixture(scope="module")
def tf():
    from scorecard_db.ingest_tax_foundation import stage_scores

    return stage_scores()


@pytest.fixture(scope="module")
def pwbm():
    from scorecard_db.ingest_pwbm import stage_scores

    return stage_scores()


@pytest.fixture(scope="module")
def tpc():
    from scorecard_db.ingest_tpc import stage_scores

    return stage_scores()


@pytest.fixture(scope="module")
def cbo():
    from scorecard_db.ingest_cbo import stage_scores

    return stage_scores()


@pytest.fixture(scope="module")
def cpsp():
    from scorecard_db.ingest_cpsp import stage_scores

    return stage_scores()


@pytest.fixture(scope="module")
def bl():
    from scorecard_db.ingest_budget_lab import stage_scores

    return stage_scores()


class TestJCT:
    def test_full_count(self, jct):
        assert len(jct) == 6771

    def test_enacted_title_vii_net_total(self, jct):
        net = [
            s
            for s in jct
            if s.conditions["bill_version"] == "JCX-35-25"
            and s.conditions["provision"] == "NET TOTAL"
            and s.period_start == 2025
            and s.period_end == 2034
        ]
        assert len(net) == 1
        assert net[0].value == pytest.approx(-4_474_972e6)  # the $4.475T

    def test_house_passed_net_total(self, jct):
        net = [
            s
            for s in jct
            if s.conditions["bill_version"] == "JCX-26-25R"
            and s.conditions["provision"] == "NET TOTAL"
            and s.period_end == 2034
        ]
        assert net[0].value == pytest.approx(-3_798_248e6)

    def test_managers_amendment_twins_share_reform(self, jct):
        """JCX-30 (current policy) and JCX-31 (present law) score the same
        text: same reform slug, different ReformRef.baseline."""
        by_jcx = {
            jcx: {
                (s.reform.reform["policy"], s.reform.key())
                for s in jct
                if s.conditions["bill_version"] == jcx
            }
            for jcx in ("JCX-30-25", "JCX-31-25")
        }
        ((slug30, key30),) = by_jcx["JCX-30-25"]
        ((slug31, key31),) = by_jcx["JCX-31-25"]
        assert slug30 == slug31 == "obbba_senate_managers_20250628"
        assert key30 != key31

    def test_current_policy_baseline_is_reform_ref(self, jct):
        cp = [
            s for s in jct if s.conditions["bill_version"] in ("JCX-29-25", "JCX-30-25")
        ]
        assert len(cp) == 2090
        assert all(
            s.reform.baseline == {"policy": "current_policy"}
            and s.conditions["baseline_policy"] == "current_policy"
            for s in cp
        )

    def test_window_rows_follow_convention(self, jct):
        windows = [s for s in jct if s.period_start is not None]
        assert len(windows) == 911
        assert all(s.period == s.period_end for s in windows)
        assert all(s.conditions["window_kind"] == "total" for s in windows)


class TestTaxFoundation:
    def test_count_after_twin_merge(self, tf):
        assert len(tf) == 663
        assert sum(1 for s in tf if "also_published" in s.publication) == 2

    def test_obbba_enacted_ten_year_totals(self, tf):
        totals = {
            s.conditions["scoring"]: s.value
            for s in tf
            if s.reform.reform["policy"] == "obbba_enacted_title_vii"
            and s.period_start == 2025
            and "provision" not in s.conditions
            and "tariff_policy" not in s.conditions
        }
        assert totals["conventional"] == pytest.approx(-5_168.4e9)
        assert totals["dynamic"] == pytest.approx(-4_331.1e9)

    def test_salt_cap_provision_under_tcja_permanence(self, tf):
        salt = {
            s.conditions["scoring"]: s.value
            for s in tf
            if s.conditions.get("provision") == "Limitation on SALT"
        }
        assert salt["conventional"] == pytest.approx(1_020.43e9)
        assert salt["dynamic"] == pytest.approx(782.68e9)

    def test_pct_rows_are_percent_units(self, tf):
        pct = [s for s in tf if s.metric is Metric.PCT_CHANGE_AFTER_TAX_INCOME]
        assert len(pct) == 174
        assert all(s.unit_concept is UnitConcept.PERCENT for s in pct)


class TestPWBM:
    def test_full_count(self, pwbm):
        assert len(pwbm) == 717

    def test_signed_bill_deficit_headline(self, pwbm):
        totals = {
            s.conditions["scoring"]: s.value
            for s in pwbm
            if s.metric is Metric.PRIMARY_DEFICIT_CHANGE
            and s.period_start == 2025
            and s.reform.reform["policy"] == "obbba_enacted_pl119_21"
        }
        assert totals["conventional"] == pytest.approx(3_211e9)
        assert totals["dynamic"] == pytest.approx(3_631e9)

    def test_tcja_extension_baseline_rows(self, pwbm):
        vs_tcja = [s for s in pwbm if s.reform.baseline == {"policy": "tcja_extension"}]
        assert len(vs_tcja) == 154
        assert all(s.conditions["baseline_policy"] == "tcja_extension" for s in vs_tcja)

    def test_fractions_normalized_to_percent(self, pwbm):
        pct = [s for s in pwbm if s.metric is Metric.PCT_CHANGE_AFTER_TAX_INCOME]
        assert all(s.unit_concept is UnitConcept.PERCENT for s in pct)
        # First staged distribution row: -0.011 fraction -> -1.1 percent.
        q1 = [
            s
            for s in pct
            if s.period == 2027
            and s.conditions.get("income_group") == "first_quintile"
            and s.conditions.get("statistic") == "group_aggregate"
            and s.reform.reform["policy"] == "obbba_enacted_pl119_21"
        ]
        assert q1[0].value == pytest.approx(-1.1)

    def test_dollar_averages_are_per_household(self, pwbm):
        avg = [
            s
            for s in pwbm
            if s.metric
            in (
                Metric.AVG_TAX_CHANGE_USD,
                Metric.AVG_CHANGE_AFTER_TAX_INCOME_USD,
            )
        ]
        assert len(avg) == 108
        assert all(s.unit_concept is UnitConcept.USD_PER_HOUSEHOLD for s in avg)


class TestTPC:
    def test_counts_and_drops(self, tpc):
        scores, dropped = tpc
        assert len(scores) == 1057
        assert dropped == {"benefit_family": 468}

    def test_family_first_act_unrounded_twin(self, tpc):
        scores, _ = tpc
        ff = [
            s
            for s in scores
            if s.publication["table_id"] == "T26-0016"
            and s.conditions.get("income_group") == "Lowest Quintile"
            and s.metric is Metric.PCT_CHANGE_AFTER_TAX_INCOME
        ]
        assert ff[0].value == pytest.approx(1.1)
        assert ff[0].publication["value_unrounded"] == pytest.approx(1.05)

    def test_ctc_options_baseline_is_senate_title_vii(self, tpc):
        scores, _ = tpc
        opts = [
            s
            for s in scores
            if s.reform.reform["policy"] == "obbba_senate_ctc_top_rate_options"
        ]
        assert {s.reform.reform["option"] for s in opts} == {
            "Option 1",
            "Option 2",
            "Option 3",
        }
        assert all(
            s.reform.baseline == {"policy": "current_law_plus_senate_obbba_title_vii"}
            for s in opts
        )

    def test_t26_0010_keyed_off_workbook_not_page(self, tpc):
        """The T26-0010 page says CTC options; the manifested workbook is
        the April-2026 tariff table. The registry follows the file."""
        scores, _ = tpc
        rows = [s for s in scores if s.publication["table_id"] == "T26-0010"]
        assert len(rows) == 44
        assert all(
            s.reform.reform["policy"] == "trump_tariffs_announced_20250120_20260402"
            and s.reform.baseline == {"policy": "current_law_pre_2025_tariffs"}
            for s in rows
        )

    def test_t26_0009_by_race_coverage(self, tpc):
        """The re-parsed by-racial/ethnic-group set: 5 sheets x 9 income
        groups x 3 metrics, race as a subgroup condition (absent on the
        all-tax-units sheet), one reform world (enacted Title VII vs the
        explicit pre-OBBBA baseline)."""
        scores, _ = tpc
        rows = [s for s in scores if s.publication["table_id"] == "T26-0009"]
        assert len(rows) == 135
        by_subgroup = {}
        for s in rows:
            by_subgroup.setdefault(s.conditions.get("subgroup"), []).append(s)
        assert set(by_subgroup) == {
            None,
            "white_non_hispanic",
            "black_non_hispanic",
            "hispanic",
            "additional_races",
        }
        assert all(len(g) == 27 for g in by_subgroup.values())
        assert all(
            s.reform.reform == {"policy": "obbba_enacted_title_vii"}
            and s.reform.baseline == {"policy": "pre_obbba_law"}
            and s.conditions["baseline_policy"] == "pre_obbba_law"
            and s.conditions["income_axis"] == "Expanded Cash Income Percentile"
            and s.period == 2026
            for s in rows
        )

    def test_t26_0009_values_match_workbook(self, tpc):
        """Spot values hand-transcribed from the sha256-manifested
        workbook (sheet!cell in comments), covering every sheet and all
        three metrics."""
        scores, _ = tpc
        val = {
            (
                s.conditions.get("subgroup"),
                s.conditions["income_group"],
                s.metric,
            ): s.value
            for s in scores
            if s.publication["table_id"] == "T26-0009"
        }
        pct = Metric.PCT_CHANGE_AFTER_TAX_INCOME
        cut = Metric.SHARE_WITH_TAX_CUT
        avg = Metric.AVG_TAX_CHANGE_USD
        assert val[(None, "All", pct)] == pytest.approx(2.8)  # All!K20
        assert val[(None, "All", cut)] == pytest.approx(85.0)  # All!C20
        assert val[(None, "All", avg)] == pytest.approx(-2860)  # All!O20
        assert val[(None, "Top Quintile", avg)] == pytest.approx(-12200)  # All!O19
        assert val[("white_non_hispanic", "Top Quintile", avg)] == pytest.approx(
            -12710
        )  # White!O19
        assert val[("black_non_hispanic", "Lowest Quintile", cut)] == pytest.approx(
            57.3
        )  # Black!C15
        assert val[("black_non_hispanic", "Lowest Quintile", avg)] == pytest.approx(
            -160
        )  # Black!O15
        assert val[("hispanic", "Top 5 Percent", pct)] == pytest.approx(
            4.0
        )  # Hispanic!K25
        assert val[("additional_races", "All", pct)] == pytest.approx(
            2.9
        )  # Additional Races!K20

    def test_t26_0009_pct_and_dollar_columns_separated(self, tpc):
        """The original staging leaked baseline-panel dollar cells into
        percent metrics (All!K37 = 1020, an average federal tax burden in
        dollars, staged as a percent change). Percent-unit rows must stay
        on the percent scale, dollar rows carry the per-tax-unit unit,
        and the baseline panel stays out entirely."""
        scores, _ = tpc
        rows = [s for s in scores if s.publication["table_id"] == "T26-0009"]
        for s in rows:
            if s.metric is Metric.AVG_TAX_CHANGE_USD:
                assert s.unit_concept is UnitConcept.USD_PER_TAX_UNIT
            else:
                assert s.unit_concept is UnitConcept.PERCENT
                assert -10 <= s.value <= 100
        assert 1020.0 not in {
            s.value for s in rows if s.unit_concept is UnitConcept.PERCENT
        }


class TestCBO:
    def test_full_count(self, cbo):
        assert len(cbo) == 931

    def test_staged_consumed_as_target_honored(self, cbo):
        consumed = [
            s
            for s in cbo
            if s.calibration_relationship is CalibrationRelationship.CONSUMED_AS_TARGET
        ]
        assert len(consumed) == 317

    def test_snap_fy2026_outlays(self, cbo):
        snap = [
            s
            for s in cbo
            if s.conditions.get("program") == "snap"
            and s.metric is Metric.BENEFIT_COST
            and s.conditions.get("component") == "total_outlays"
            and s.period == 2026
        ]
        assert snap[0].value == pytest.approx(100_053e6)

    def test_tfp_cap_reform_pair(self, cbo):
        """SNAP avg benefit 2034: $213 under the PL 119-21 TFP cap vs
        $227 baseline, both on the Jan-2025 baseline vintage — distinct
        from the Feb-2026 workbook's 2034 row ($219.86)."""
        rows = {
            (s.reform.framework, s.value)
            for s in cbo
            if s.metric is Metric.AVERAGE_MONTHLY_BENEFIT
            and s.period == 2034
            and s.conditions.get("program") == "snap"
        }
        assert rows == {
            ("policy_ref", 213.0),
            ("baseline", 227.0),
            ("baseline", 219.86),
        }
        vintaged = [
            s
            for s in cbo
            if s.conditions.get("data_vintage") == "january_2025_baseline"
        ]
        assert len(vintaged) == 2


class TestCPSP:
    def test_full_count(self, cpsp):
        assert len(cpsp) == 1033

    def test_monthly_series_head(self, cpsp):
        jan24 = [
            s
            for s in cpsp
            if s.conditions.get("month") == "2024-01"
            and s.reform is BASELINE
            and "subgroup" not in s.conditions
            and "income_concept" not in s.conditions
        ]
        assert jan24[0].value == pytest.approx(0.182)

    def test_erratum_claim_staged_at_body_value(self, cpsp):
        from scorecard_db.ingest_cpsp import erratum_claim

        e = erratum_claim(cpsp)
        assert e.value == pytest.approx(0.114)  # not the 16.6% key finding

    def test_ctc_counterfactual_worlds_pair_correctly(self, cpsp):
        afa_vs_tcja = [
            s
            for s in cpsp
            if s.reform.reform
            and s.reform.reform.get("policy") == "afa_ctc"
            and s.reform.baseline
            and s.reform.baseline["policy"] == "tcja_ctc"
        ]
        assert afa_vs_tcja
        assert all(
            s.metric in (Metric.POVERTY_RATE_CHANGE, Metric.POVERTY_COUNT_CHANGE)
            and s.conditions["baseline_policy"] == "tcja_ctc"
            for s in afa_vs_tcja
        )

    def test_tfp_revocation_rides_trim3_vintage(self, cpsp):
        tfp = [
            s
            for s in cpsp
            if s.reform.reform
            and s.reform.reform.get("policy") == "snap_tfp_2021_revoked"
        ]
        assert len(tfp) == 463
        assert all(
            s.conditions["data_vintage"] == "TRIM3-adjusted CPS-ASEC pooled 2015-2019"
            for s in tfp
        )

    def test_geographies_normalized(self, cpsp):
        geos = {s.conditions["geography"] for s in cpsp}
        assert "US" in geos and "CA" in geos
        assert not any(g in geos for g in ("us", "California"))


class TestBudgetLab:
    def test_count_after_twin_merge(self, bl):
        assert len(bl) == 1229

    def test_reconciliation_distribution_medicaid_q1(self, bl):
        rows = [
            s
            for s in bl
            if s.conditions.get("provision_component") == "Changes to Medicaid"
            and s.conditions.get("income_group") == "Quintile 1"
            and s.reform.reform["policy"] == "obbba_house_passed_20250522"
        ]
        assert rows[0].value == pytest.approx(-1.53846, rel=1e-4)
        assert (rows[0].period_start, rows[0].period_end) == (2026, 2034)
        assert rows[0].conditions["window_kind"] == "annual_average"

    def test_finance_title_not_conflated_with_whole_bill(self, bl):
        totals = {
            s.conditions.get("bill_component"): s.value
            for s in bl
            if s.reform.reform["policy"] == "obbba_enacted_pl119_21"
            and s.period_start == 2025
            and s.period_end == 2034
            and s.metric is Metric.REVENUE_CHANGE
            and s.conditions.get("bill_component")
            in ("Total", "Title VII. Finance / Total")
        }
        assert totals["Total"] == pytest.approx(-3_062e9)
        assert totals["Title VII. Finance / Total"] == pytest.approx(-3_296e9)

    def test_ctc_option_vs_option1_baseline(self, bl):
        rel = [
            s
            for s in bl
            if s.reform.baseline and s.reform.baseline.get("policy") == "bl_ctc_option"
        ]
        assert len(rel) == 15
        assert all(s.reform.baseline["option"] == "1. TCJA CTC" for s in rel)

    def test_label_only_decade_windows_stay_conditions(self, bl):
        labels = [s for s in bl if "period_window" in s.conditions]
        assert len(labels) == 6
        assert all(s.period_start is None for s in labels)
        assert {s.conditions["period_window"] for s in labels} == {
            "Budget Window",
            "Second Decade",
            "Third Decade",
        }


class TestCrossSource:
    def test_enacted_title_vii_key_shared_jct_tpc_tf(self, jct, tpc, tf):
        """Current-law-baseline scorings of the enacted text share one
        key across sources. TPC's post-enactment by-race set (T26-0009)
        scores the same slug against its explicitly stated pre-OBBBA
        baseline, so it rides the same policy with a second key."""
        scores, _ = tpc
        jct_keys = {
            s.reform.key() for s in jct if s.conditions["bill_version"] == "JCX-35-25"
        }
        tpc_by_baseline = {}
        for s in scores:
            if s.reform.reform["policy"] == "obbba_enacted_title_vii":
                tpc_by_baseline.setdefault(
                    (s.reform.baseline or {}).get("policy"), set()
                ).add(s.reform.key())
        tf_keys = {
            s.reform.key()
            for s in tf
            if s.reform.reform["policy"] == "obbba_enacted_title_vii"
        }
        assert set(tpc_by_baseline) == {None, "pre_obbba_law"}
        tpc_keys = tpc_by_baseline[None]
        assert jct_keys == tpc_keys == tf_keys and len(jct_keys) == 1
        assert len(tpc_by_baseline["pre_obbba_law"]) == 1
        assert tpc_by_baseline["pre_obbba_law"].isdisjoint(tpc_keys)

    def test_managers_amendment_key_shared_jct_tpc_bl(self, jct, tpc, bl):
        scores, _ = tpc
        jct31 = {
            s.reform.key() for s in jct if s.conditions["bill_version"] == "JCX-31-25"
        }
        tpc_managers = {
            s.reform.key()
            for s in scores
            if s.reform.reform == {"policy": "obbba_senate_managers_20250628"}
        }
        bl_managers = {
            s.reform.key()
            for s in bl
            if s.reform.reform == {"policy": "obbba_senate_managers_20250628"}
        }
        assert jct31 == tpc_managers == bl_managers and len(jct31) == 1

    def test_kypa_and_watca_shared_pwbm_bl(self, pwbm, bl):
        for slug in ("kypa_full_package", "watca"):
            keys = {
                s.reform.key()
                for s in [*pwbm, *bl]
                if s.reform.reform and s.reform.reform.get("policy") == slug
            }
            assert len(keys) == 1, slug


class TestFullIngest:
    @pytest.fixture(scope="class")
    def ingested(self, tmp_path_factory):
        import json
        import shutil

        from scorecard_db.harvest import REPO
        from scorecard_db.ingest_harvest import ADAPTERS, sync_lane_feed

        tmp = tmp_path_factory.mktemp("harvest")
        db_path = tmp / "s.db"
        stats = {name: adapter.ingest(db_path) for name, adapter in ADAPTERS.items()}
        feed_path = tmp / "lanes.json"
        shutil.copy(REPO / "data" / "lanes.json", feed_path)
        db = ScorecardDB(db_path)
        sync_lane_feed(db, feed_path, "2026-08-02")
        feed = json.loads(feed_path.read_text())
        yield db, stats, feed
        db.close()

    def test_claim_totals(self, ingested):
        db, stats, _ = ingested
        by_source = {
            r["source"]: r["n"]
            for r in db.conn.execute(
                "SELECT source, COUNT(*) n FROM external_scores GROUP BY source"
            )
        }
        assert by_source == {
            "jct": 6771,
            "tpc": 1057,
            "budget_lab": 1229,
            "cpsp": 1033,
            "cbo": 931,
            "pwbm": 717,
            "tax_foundation": 663,
        }
        # 12,937 staged (12,850 harvested - 48 defective T26-0009 rows
        # + 135 re-parsed) = claims + twin merges (2+48+18) + the TPC
        # benefit-family drop.
        assert sum(by_source.values()) + 2 + 48 + 18 + 468 == 12_937

    def test_lanes_ingested_and_feed_synced(self, ingested):
        db, _, feed = ingested
        lanes = {
            r["lane"]: r["stage"]
            for r in db.conn.execute("SELECT lane, stage FROM lanes")
        }
        expected = {
            "jct-reform-scores",
            "tpc-distribution",
            "cbo-baseline",
            "cbo-cost-estimates",
            "pwbm-reform-scores",
            "tax-foundation-scores",
            "budget-lab-scores",
            "cpsp-poverty",
        }
        assert {k for k, v in lanes.items() if v == "ingested"} == expected
        feed_stages = {lane["id"]: lane["stage"] for lane in feed["lanes"]}
        assert all(feed_stages[lane] == "ingested" for lane in expected)

    def test_erratum_diagnosis_seeded(self, ingested):
        db, _, _ = ingested
        rows = db.conn.execute(
            "SELECT diagnosis_class, rationale FROM diagnoses"
        ).fetchall()
        assert any(
            r["diagnosis_class"] == "external_issue" and "16.6" in r["rationale"]
            for r in rows
        )

    def test_reform_json_round_trips_from_db(self, ingested):
        db, _, _ = ingested
        row = db.conn.execute(
            "SELECT reform_json FROM external_scores WHERE source='jct' LIMIT 1"
        ).fetchone()
        ref = ReformRef.from_json(row["reform_json"])
        assert ref.framework == "policy_ref"
