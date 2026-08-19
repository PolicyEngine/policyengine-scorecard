from dataclasses import replace
import pytest

from scorecard_db import (
    BASELINE,
    ComparisonStatus,
    ExternalScore,
    PEResult,
    ReformRef,
    ScorecardDB,
)


def score(**kw):
    base = dict(
        source="urban_sotsn",
        metric="eligible_count",
        unit_concept="persons",
        period=2023,
        time_basis="average_month",
        value=1000.0,
        conditions={"geography": "US", "program": "snap"},
    )
    base.update(kw)
    return ExternalScore(**base)


class TestReformRef:
    def test_baseline_key_stable(self):
        assert ReformRef().key() == BASELINE.key()

    def test_baseline_rejects_payload(self):
        with pytest.raises(ValueError):
            ReformRef(framework="baseline", reform={"x": 1})

    def test_policyengine_requires_reform_dict(self):
        with pytest.raises(ValueError):
            ReformRef(framework="policyengine_us")

    def test_distinct_reforms_distinct_keys(self):
        a = ReformRef("policyengine_us", reform={"p": {"2025": 1}})
        b = ReformRef("policyengine_us", reform={"p": {"2025": 2}})
        assert a.key() != b.key() != BASELINE.key()

    def test_json_roundtrip(self):
        a = ReformRef("policyengine_us", reform={"p": {"2025": 1}})
        assert ReformRef.from_json(a.to_json()).key() == a.key()

    def test_unknown_framework_rejected(self):
        with pytest.raises(ValueError):
            ReformRef(framework="taxsim")


class TestClaimId:
    def test_condition_order_invariant(self):
        a = score(conditions={"geography": "US", "program": "snap"})
        b = score(conditions={"program": "snap", "geography": "US"})
        assert a.claim_id() == b.claim_id()

    def test_value_invariant(self):
        assert score(value=1.0).claim_id() == score(value=2.0).claim_id()

    def test_reform_changes_id(self):
        r = ReformRef("policyengine_us", reform={"p": {"2025": 1}})
        assert score().claim_id() != score(reform=r).claim_id()

    def test_period_and_condition_change_id(self):
        assert score().claim_id() != score(period=2024).claim_id()
        assert (
            score().claim_id()
            != score(conditions={"geography": "CA", "program": "snap"}).claim_id()
        )


class TestValidation:
    def test_bad_metric_rejected(self):
        with pytest.raises(ValueError):
            score(metric="vibes")

    def test_null_value_requires_suppressed(self):
        with pytest.raises(ValueError):
            score(value=None)
        s = score(value=None, status="suppressed")
        assert s.status == "suppressed"

    def test_conditions_must_be_str_str(self):
        with pytest.raises(ValueError):
            score(conditions={"geography": 6})

    def test_comparable_result_requires_value(self):
        with pytest.raises(ValueError):
            PEResult(
                claim_id="x",
                computed_value=None,
                status="comparable",
                engine_version="1",
                data_bundle="b",
            )
        ok = PEResult(
            claim_id="x",
            computed_value=None,
            status="pe_gap",
            engine_version="1",
            data_bundle="b",
        )
        assert ok.status == ComparisonStatus.PE_GAP


class TestDB:
    @pytest.fixture()
    def db(self, tmp_path):
        d = ScorecardDB(tmp_path / "t.db")
        yield d
        d.close()

    def test_upsert_idempotent(self, db):
        assert db.upsert_scores([score(), score(value=5.0)]) == 2
        n = db.conn.execute("SELECT COUNT(*) c FROM external_scores").fetchone()["c"]
        assert n == 1  # same claim_id -> replaced, not duplicated

    def test_latest_result_wins_in_view(self, db):
        s = score()
        db.upsert_scores([s])
        cid = s.claim_id()
        mk = lambda v, t: PEResult(  # noqa: E731
            claim_id=cid,
            computed_value=v,
            status="comparable",
            engine_version="1.764.6",
            data_bundle="buildp",
            computed_at=t,
        )
        db.add_results([mk(900.0, "2026-08-01T00:00"), mk(950.0, "2026-08-02T00:00")])
        row = db.comparisons(source="urban_sotsn")[0]
        assert row["pe_value"] == 950.0
        assert row["delta"] == pytest.approx(-50.0)
        assert row["ratio"] == pytest.approx(0.95)

    def test_held_out_filter(self, db):
        consumed = score(
            conditions={"geography": "US", "program": "eitc"},
            calibration_relationship="consumed_as_target",
        )
        held = score()
        db.upsert_scores([consumed, held])
        assert len(db.comparisons()) == 2
        rows = db.comparisons(held_out_only=True)
        assert len(rows) == 1
        assert rows[0]["program"] == "snap"

    def test_condition_json_query(self, db):
        sub = score(
            conditions={
                "geography": "US",
                "program": "snap",
                "subgroup": "age_0thr3",
            }
        )
        db.upsert_scores([score(), sub])
        rows = db.comparisons(condition=("subgroup", "age_0thr3"))
        assert len(rows) == 1

    def test_lane_upsert_and_diagnose(self, db):
        s = score()
        db.upsert_scores([s])
        db.set_lane("urban_sotsn/safety-net", "ingested", at="t1")
        db.set_lane("urban_sotsn/safety-net", "computed", at="t2")
        lane = db.conn.execute("SELECT * FROM lanes").fetchone()
        assert lane["stage"] == "computed"
        db.diagnose(s.claim_id(), "concept_mismatch", "annual vs avg-month")
        row = db.comparisons()[0]
        assert row["diagnosis_class"] == "concept_mismatch"

    def test_coverage_counts(self, db):
        a, b = score(), score(period=2024)
        db.upsert_scores([a, b])
        db.add_results(
            [
                PEResult(
                    claim_id=a.claim_id(),
                    computed_value=1.0,
                    status="comparable",
                    engine_version="1",
                    data_bundle="b",
                    computed_at="t",
                )
            ]
        )
        cov = db.coverage()
        assert cov["claims"] == 2
        assert cov["computed"] == 1
        assert cov["held_out_computed"] == 1


class TestUrbanIngest:
    @pytest.fixture(scope="class")
    def ingested(self, tmp_path_factory):
        from scorecard_db.ingest_urban import COMPARISON_DIR, ingest

        if not (COMPARISON_DIR / "urban_tidy.csv").exists():
            pytest.skip("comparison files not present")
        db_path = tmp_path_factory.mktemp("db") / "s.db"
        stats = ingest(db_path)
        return ScorecardDB(db_path), stats

    def test_counts(self, ingested):
        db, stats = ingested
        assert stats["scores"] > 29000
        assert stats["results"] > 500
        assert stats["computed"] == stats["results"]

    def test_known_snap_claim(self, ingested):
        db, _ = ingested
        rows = db.comparisons(program="snap", geography="US")
        elig = [
            r
            for r in rows
            if r["metric"] == "eligible_count" and r["pe_value"] is not None
        ]
        assert len(elig) == 1
        assert elig[0]["value"] == pytest.approx(69_128_000)
        assert elig[0]["pe_value"] == pytest.approx(66_363_630, rel=1e-3)
        assert 0.9 < elig[0]["ratio"] < 1.0

    def test_fullpart_rows_are_reform_keyed(self, ingested):
        db, _ = ingested
        from scorecard_db.models import BASELINE

        keys = {
            r["reform_key"]
            for r in db.conn.execute("SELECT DISTINCT reform_key FROM external_scores")
        }
        assert BASELINE.key() in keys
        assert len(keys) == 2  # baseline + fullpart

    def test_suppressed_rows_carry_status(self, ingested):
        db, _ = ingested
        n = db.conn.execute(
            "SELECT COUNT(*) c FROM external_scores WHERE status='suppressed'"
            " AND value IS NULL"
        ).fetchone()["c"]
        assert n > 0


class TestEffectiveRelationship:
    """The tautology labels (issue #1 point 2) are assigned, not defaulted."""

    def test_snap_participation_is_consumed(self):
        from scorecard_db.models import CalibrationRelationship, Metric
        from scorecard_db.relationships import effective_relationship

        rel, basis = effective_relationship("snap", Metric.PARTICIPATION_RATE)
        assert rel is CalibrationRelationship.CONSUMED_AS_TARGET
        assert "FNS" in basis

    def test_snap_eligibility_held_out(self):
        from scorecard_db.models import CalibrationRelationship, Metric
        from scorecard_db.relationships import effective_relationship

        rel, _ = effective_relationship("snap", Metric.ELIGIBLE_COUNT)
        assert rel is CalibrationRelationship.HELD_OUT

    def test_tanf_participation_is_seeded(self):
        from scorecard_db.models import CalibrationRelationship, Metric
        from scorecard_db.relationships import effective_relationship

        rel, basis = effective_relationship("tanf", Metric.PARTICIPATION_RATE)
        assert rel is CalibrationRelationship.SEED_SOURCE
        assert "ASPE" in basis

    def test_wic_all_held_out(self):
        from scorecard_db.models import CalibrationRelationship, Metric
        from scorecard_db.relationships import effective_relationship

        for m in (
            Metric.ELIGIBLE_COUNT,
            Metric.PARTICIPATION_RATE,
            Metric.PARTICIPATION_GAP_COUNT,
        ):
            rel, _ = effective_relationship("wic", m)
            assert rel is CalibrationRelationship.HELD_OUT


class TestInputOverrideFramework:
    def test_inputs_framework_accepted(self):
        r = ReformRef(
            framework="policyengine_us_inputs",
            reform={"takes_up_snap_if_eligible": True},
        )
        assert r.key() != BASELINE.key()

    def test_inputs_framework_requires_dict(self):
        with pytest.raises(ValueError):
            ReformRef(framework="policyengine_us_inputs")

    def test_fullpart_reform_is_input_override(self):
        from scorecard_db.ingest_urban import FULLPART_REFORM

        assert FULLPART_REFORM.framework == "policyengine_us_inputs"
        # No fabricated parameter paths: descriptor keys are variables.
        assert all("." not in k for k in FULLPART_REFORM.reform), (
            "input-override descriptors must not look like parameter paths"
        )


class TestClaimIdBackCompat:
    """2026-08-02 schema extensions must not move existing identities:
    the DB on disk keys 30k urban claims by these hashes."""

    def test_fixture_claim_id_unchanged(self):
        assert score().claim_id() == "157243b61838075381ed"

    def test_baseline_reform_key_unchanged(self):
        assert BASELINE.key() == "03395a10966bb849"


class TestPeriodRange:
    def window(self, **kw):
        base = dict(period=2034, period_start=2025, period_end=2034)
        base.update(kw)
        return score(**base)

    def test_start_and_end_come_together(self):
        with pytest.raises(ValueError):
            score(period_start=2025)
        with pytest.raises(ValueError):
            score(period_end=2034)

    def test_start_before_end(self):
        with pytest.raises(ValueError):
            self.window(period_start=2034)

    def test_period_equals_end(self):
        with pytest.raises(ValueError):
            self.window(period=2025)
        assert self.window().period == 2034

    def test_window_id_distinct_from_single_year(self):
        assert self.window().claim_id() != score(period=2034).claim_id()

    def test_db_roundtrip(self, tmp_path):
        db = ScorecardDB(tmp_path / "t.db")
        w = self.window()
        db.upsert_scores([w])
        row = db.comparisons()[0]
        assert (row["period_start"], row["period_end"]) == (2025, 2034)
        db.close()


class TestPolicyRef:
    def test_requires_policy_slug(self):
        with pytest.raises(ValueError):
            ReformRef(framework="policy_ref")
        with pytest.raises(ValueError):
            ReformRef(framework="policy_ref", reform={"law": "PL 119-21"})

    def test_baseline_descriptor_needs_slug(self):
        with pytest.raises(ValueError):
            ReformRef(
                framework="policy_ref",
                reform={"policy": "obbba"},
                baseline={"note": "current policy"},
            )

    def test_rulespec_rejected(self):
        with pytest.raises(ValueError):
            ReformRef(
                framework="policy_ref",
                reform={"policy": "obbba"},
                rulespec_ref="x",
            )

    def test_baseline_variant_changes_key(self):
        plain = ReformRef(framework="policy_ref", reform={"policy": "o"})
        vs_cp = ReformRef(
            framework="policy_ref",
            reform={"policy": "o"},
            baseline={"policy": "current_policy"},
        )
        assert plain.key() != vs_cp.key()
        assert ReformRef.from_json(vs_cp.to_json()).key() == vs_cp.key()


class TestMigration:
    """Opening a pre-window-schema file adds the new columns in place."""

    _OLD_DDL = """
    CREATE TABLE external_scores (
        claim_id TEXT PRIMARY KEY, source TEXT NOT NULL,
        source_model TEXT, ledger_fact TEXT, source_column TEXT,
        publication TEXT NOT NULL DEFAULT '{}',
        reform_key TEXT NOT NULL, reform_json TEXT NOT NULL,
        metric TEXT NOT NULL, unit_concept TEXT NOT NULL,
        period INTEGER NOT NULL, time_basis TEXT NOT NULL,
        conditions TEXT NOT NULL DEFAULT '{}',
        geography TEXT, program TEXT, value REAL,
        value_kind TEXT NOT NULL, status TEXT NOT NULL,
        calibration_relationship TEXT NOT NULL
    );
    """

    def test_old_file_gains_period_columns(self, tmp_path):
        import sqlite3

        path = tmp_path / "old.db"
        conn = sqlite3.connect(path)
        conn.executescript(self._OLD_DDL)
        conn.close()
        db = ScorecardDB(path)
        cols = {
            r["name"] for r in db.conn.execute("PRAGMA table_info(external_scores)")
        }
        assert {"period_start", "period_end"} <= cols
        db.upsert_scores([score(period=2034, period_start=2025, period_end=2034)])
        assert db.comparisons()[0]["period_start"] == 2025
        db.close()


class TestPlatformProbe:
    """ingest_platform must rebuild ingest_urban's claim identities exactly."""

    def _tidy_claim(self, **kw):
        base = dict(
            source="urban_sotsn",
            metric="participation_rate",
            unit_concept="share",
            period=2023,
            time_basis="average_month",
            value=0.575,
            conditions={
                "geography": "US",
                "program": "snap",
                "rate_unit": "pop",
            },
        )
        base.update(kw)
        return ExternalScore(**base)

    def test_rate_row_roundtrip(self):
        from scorecard_db.ingest_platform import _probe

        row = {
            "program": "snap",
            "metric": "participation_rate",
            "subgroup": "total",
            "variant": None,
            "geography": "US",
            "unit_concept": "persons",
        }
        assert _probe(row).claim_id() == self._tidy_claim().claim_id()

    def test_variant_embeds_into_subgroup(self):
        from scorecard_db.ingest_platform import _probe

        row = {
            "program": "tanf",
            "metric": "participation_rate",
            "subgroup": "total",
            "variant": "no_SSF",
            "geography": "US",
            "unit_concept": "families",
        }
        claim = self._tidy_claim(
            conditions={
                "geography": "US",
                "program": "tanf",
                "rate_unit": "units",
                "subgroup": "total_no_SSF",
            },
        )
        assert _probe(row).claim_id() == claim.claim_id()

    def test_fullpart_poverty_row(self):
        from scorecard_db.ingest_platform import _probe
        from scorecard_db.ingest_urban import FULLPART_REFORM

        row = {
            "program": "spm_poverty",
            "metric": "poverty_rate_fullpart",
            "subgroup": "child",
            "variant": None,
            "geography": "AK",
            "unit_concept": "children",
        }
        claim = self._tidy_claim(
            metric="poverty_rate",
            conditions={"geography": "AK", "subgroup": "child"},
            reform=FULLPART_REFORM,
        )
        assert _probe(row).claim_id() == claim.claim_id()


class TestPermanentHoldout:
    """Poverty metrics may never become calibration targets (2026-08-02)."""

    def test_poverty_metrics_never_calibrate(self):
        from scorecard_db.models import CalibrationRelationship, Metric
        from scorecard_db.relationships import (
            effective_relationship,
            never_calibrate,
        )

        for m in (
            Metric.POVERTY_RATE,
            Metric.POVERTY_RATE_CHANGE,
            Metric.POVERTY_COUNT_CHANGE,
        ):
            assert never_calibrate(m)
            for program in ("base", "fullpart", "snap", "anything"):
                rel, basis = effective_relationship(program, m)
                assert rel is CalibrationRelationship.HELD_OUT
                assert "PERMANENT" in basis

    def test_admin_metrics_unaffected(self):
        from scorecard_db.models import Metric
        from scorecard_db.relationships import never_calibrate

        assert not never_calibrate(Metric.PARTICIPATION_RATE)
        assert not never_calibrate(Metric.ELIGIBLE_COUNT)


class TestBaselineRegistry:
    """Baseline as a first-class attribute of every score (issue #13)."""

    def test_null_baseline_keys_current_law(self):
        from scorecard_db import CURRENT_LAW_DESCRIPTOR, baseline_key

        assert BASELINE.baseline_key() == baseline_key(CURRENT_LAW_DESCRIPTOR)
        pe = ReformRef("policyengine_us", reform={"p": {"2025": 1}})
        assert pe.baseline_key() == BASELINE.baseline_key()

    def test_non_current_law_baseline_distinct(self):
        r = ReformRef(
            framework="policy_ref",
            reform={"policy": "obbba"},
            baseline={"policy": "tcja_extension"},
        )
        assert r.baseline_key() != BASELINE.baseline_key()

    def test_descriptor_requires_policy_slug(self):
        from scorecard_db import baseline_key

        with pytest.raises(ValueError):
            baseline_key({"label": "nope"})

    def test_claim_id_unchanged_by_baseline_key_projection(self):
        # Additive projection only: the #13 columns must not move ids.
        assert score().claim_id() == "157243b61838075381ed"

    def test_scores_carry_baseline_key(self, tmp_path):
        db = ScorecardDB(tmp_path / "t.db")
        db.upsert_scores([score()])
        row = db.conn.execute("SELECT baseline_key FROM external_scores").fetchone()
        assert row["baseline_key"] == BASELINE.baseline_key()
        db.close()

    def test_registry_seeding_and_unregistered_detection(self, tmp_path):
        from scorecard_db.baselines import register_baselines

        db = ScorecardDB(tmp_path / "t.db")
        db.upsert_scores([score()])
        register_baselines(db)
        assert db.unregistered_baselines() == []
        row = db.comparisons()[0]
        assert row["claim_baseline_label"] == "current_law"

        alien = score(
            conditions={"geography": "US", "program": "wic"},
            reform=ReformRef(
                framework="policy_ref",
                reform={"policy": "x"},
                baseline={"policy": "never_registered_world"},
            ),
        )
        db.upsert_scores([alien])
        with pytest.raises(ValueError, match="never_registered"):
            register_baselines(db)
        db.close()

    def test_view_guard_downgrades_cross_baseline_agreement(self, tmp_path):
        """comparable vs a different executed baseline can never render as
        plain agreement — pe_status_effective says constructed."""
        from scorecard_db import baseline_key

        db = ScorecardDB(tmp_path / "t.db")
        s = score()
        db.upsert_scores([s])
        db.add_results(
            [
                PEResult(
                    claim_id=s.claim_id(),
                    computed_value=999.0,
                    status=ComparisonStatus.COMPARABLE,
                    engine_version="x",
                    data_bundle="y",
                    baseline_key=baseline_key({"policy": "pre_ab2025"}),
                )
            ]
        )
        row = db.comparisons()[0]
        assert row["pe_status"] == "comparable"
        assert row["pe_status_effective"] == "constructed"
        db.close()

    def test_view_guard_passes_same_baseline(self, tmp_path):
        db = ScorecardDB(tmp_path / "t.db")
        s = score()
        db.upsert_scores([s])
        db.add_results(
            [
                PEResult(
                    claim_id=s.claim_id(),
                    computed_value=999.0,
                    status=ComparisonStatus.COMPARABLE,
                    engine_version="x",
                    data_bundle="y",
                    baseline_key=BASELINE.baseline_key(),
                )
            ]
        )
        row = db.comparisons()[0]
        assert row["pe_status_effective"] == "comparable"
        db.close()

    def test_legacy_results_pass_through_only_on_current_law(self, tmp_path):
        # A legacy run (no recorded executed baseline) against a
        # current-law claim keeps its status; against any non-current-law
        # world its agreement is unverifiable — never plain.
        db = ScorecardDB(tmp_path / "t.db")
        s = score()
        db.upsert_scores([s])
        legacy = PEResult(
            claim_id=s.claim_id(),
            computed_value=999.0,
            status=ComparisonStatus.COMPARABLE,
            engine_version="x",
            data_bundle="y",
        )
        db.add_results([legacy])
        assert db.comparisons()[0]["pe_status_effective"] == "comparable"

        world = score(
            reform=ReformRef(
                framework="policy_ref",
                reform={"policy": "opt"},
                baseline={"policy": "tcja_extension"},
            ),
            source_column="world_claim",
        )
        db.upsert_scores([world])
        db.add_results([replace(legacy, claim_id=world.claim_id())])
        row = next(r for r in db.comparisons() if r["source_column"] == "world_claim")
        assert row["pe_status_effective"] == "baseline_unvalidated"
        db.close()


class TestDescriptiveRegister:
    """Issue #9 latest ruling: normative classes gated on citable issues."""

    def test_gated_classes_require_action_link(self, tmp_path):
        db = ScorecardDB(tmp_path / "t.db")
        s = score()
        db.upsert_scores([s])
        for cls in ("pe_gap", "external_issue"):
            with pytest.raises(ValueError, match="citable"):
                db.diagnose(s.claim_id(), cls, "divergence looks big")
        db.diagnose(
            s.claim_id(),
            "pe_gap",
            "EHS at engine-default take-up",
            action_link="https://github.com/PolicyEngine/populace/issues/593",
        )
        db.close()

    def test_methodological_difference_is_descriptive(self, tmp_path):
        db = ScorecardDB(tmp_path / "t.db")
        s = score()
        db.upsert_scores([s])
        db.diagnose(
            s.claim_id(),
            "methodological_difference",
            "Populace calculates benefits and recalibrates where ASEC "
            "carries reported attributes.",
        )
        assert db.comparisons()[0]["diagnosis_class"] == "methodological_difference"
        db.close()

    def test_old_diagnoses_table_migrates_to_new_check(self, tmp_path):
        import sqlite3 as s3

        path = tmp_path / "old.db"
        conn = s3.connect(path)
        conn.executescript(
            """
            CREATE TABLE external_scores (
                claim_id TEXT PRIMARY KEY, source TEXT NOT NULL,
                source_model TEXT, ledger_fact TEXT, source_column TEXT,
                publication TEXT NOT NULL DEFAULT '{}',
                reform_key TEXT NOT NULL, reform_json TEXT NOT NULL,
                metric TEXT NOT NULL, unit_concept TEXT NOT NULL,
                period INTEGER NOT NULL, time_basis TEXT NOT NULL,
                conditions TEXT NOT NULL DEFAULT '{}',
                geography TEXT, program TEXT, value REAL,
                value_kind TEXT NOT NULL, status TEXT NOT NULL,
                calibration_relationship TEXT NOT NULL
            );
            CREATE TABLE diagnoses (
                claim_id TEXT PRIMARY KEY,
                diagnosis_class TEXT NOT NULL CHECK (diagnosis_class IN (
                    'pe_gap','external_issue','concept_mismatch','vintage',
                    'undiagnosed'
                )),
                rationale TEXT NOT NULL DEFAULT '',
                action_link TEXT NOT NULL DEFAULT ''
            );
            INSERT INTO diagnoses VALUES ('c1', 'vintage', 'r', '');
            """
        )
        conn.close()
        db = ScorecardDB(path)
        db.upsert_scores([score()])
        db.diagnose(score().claim_id(), "methodological_difference", "ok")
        kept = db.conn.execute(
            "SELECT diagnosis_class FROM diagnoses WHERE claim_id='c1'"
        ).fetchone()
        assert kept["diagnosis_class"] == "vintage"
        db.close()
