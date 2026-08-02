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
            != score(
                conditions={"geography": "CA", "program": "snap"}
            ).claim_id()
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
        n = db.conn.execute(
            "SELECT COUNT(*) c FROM external_scores"
        ).fetchone()["c"]
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
            for r in db.conn.execute(
                "SELECT DISTINCT reform_key FROM external_scores"
            )
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
