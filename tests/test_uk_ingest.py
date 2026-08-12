"""UK-harvest adapter tests (2026-08-02 population).

Staging-level: every test reads the vendored gzipped staging through the
adapters' stage() functions (module-cached — OBR is 25k rows) and checks
the load-bearing decisions: FY normalization, ledger routing, verified
calibration relationships, reform worlds, and full-accounting against
the staged row counts (33,943 across seven sources).
"""

import pytest

from scorecard_db import (
    BASELINE,
    CalibrationRelationship,
    Metric,
    ScorecardDB,
)
from scorecard_db.uk import (
    ledger_row,
    parse_fy,
    parse_fy_window,
    slugify,
    write_ledger_staging,
)

CR = CalibrationRelationship


@pytest.fixture(scope="module")
def obr():
    from scorecard_db.ingest_uk_obr import stage

    return stage()


@pytest.fixture(scope="module")
def dwp():
    from scorecard_db.ingest_uk_dwp import stage

    return stage()


@pytest.fixture(scope="module")
def hmrc():
    from scorecard_db.ingest_uk_hmrc import stage

    return stage()


@pytest.fixture(scope="module")
def hmt():
    from scorecard_db.ingest_uk_hmt import stage

    return stage()


@pytest.fixture(scope="module")
def ukmod_jrf():
    from scorecard_db.ingest_uk_ukmod_jrf import stage

    return stage()


@pytest.fixture(scope="module")
def ifs():
    from scorecard_db.ingest_uk_ifs import stage

    return stage()


@pytest.fixture(scope="module")
def rf():
    from scorecard_db.ingest_uk_rf import stage

    return stage()


class TestFiscalYears:
    """period = FY START year, derived from the verbatim label."""

    def test_start_year_forms(self):
        assert parse_fy("2026-27") == (2026, "2026-27")
        assert parse_fy("2023/24") == (2023, "2023-24")
        assert parse_fy("1970-71") == (1970, "1970-71")

    def test_fye_is_end_year_convention(self):
        assert parse_fy("FYE 2010") == (2009, "2009-10")
        assert parse_fy("FYE 2025") == (2024, "2024-25")

    def test_century_wrap_fixes_the_1900_defect(self):
        # Staged as period=1900 upstream; the label is authoritative.
        assert parse_fy("1999/00") == (1999, "1999-00")

    def test_non_contiguous_rejected(self):
        with pytest.raises(ValueError):
            parse_fy("2026-28")
        with pytest.raises(ValueError):
            parse_fy("not a year")

    def test_windows(self):
        assert parse_fy_window("2025-26 to 2029-30") == (
            2025, 2029, "2025-26 to 2029-30",
        )
        assert parse_fy_window("2021/22-2023/24") == (
            2021, 2023, "2021-22 to 2023-24",
        )


class TestFullAccounting:
    """scores + ledger + deliberate drops (+ merged twins) == staged."""

    def test_obr(self, obr):
        scores, ledger = obr
        assert len(scores) == 25425
        assert len(ledger) == 133
        assert len(scores) + len(ledger) == 25558

    def test_dwp(self, dwp):
        scores, ledger = dwp
        assert len(scores) == 1952
        assert len(ledger) == 102
        assert len(scores) + len(ledger) == 2054

    def test_hmrc(self, hmrc):
        scores, ledger = hmrc
        assert len(scores) == 987
        assert len(ledger) == 1855
        assert len(scores) + len(ledger) == 2842

    def test_hmt(self, hmt):
        scores, ledger = hmt
        assert (len(scores), len(ledger)) == (1368, 0)

    def test_ukmod_jrf(self, ukmod_jrf):
        scores, ledger, dropped_mis = ukmod_jrf
        merged = sum(
            1 for s in scores if "also_published" in s.publication
        )
        assert dropped_mis == 88
        assert merged == 2
        assert len(scores) + dropped_mis + merged == 1782

    def test_ifs(self, ifs):
        scores, ledger = ifs[0], ifs[1]
        assert (len(scores), len(ledger)) == (268, 0)

    def test_rf(self, rf):
        scores, _, dropped = rf
        assert len(scores) == 70
        assert dropped == 1  # price-index-only row, out of model scope


class TestLedgerRouting:
    """Admin outturn facts never enter external_scores (Max 2026-08-02)."""

    def test_no_outturn_reaches_scores(self, obr, dwp, hmrc):
        for scores, _ledger, *rest in (obr, dwp, hmrc):
            for s in scores:
                assert s.conditions.get("basis") not in (
                    "outturn", "provisional",
                ), s.conditions

    def test_ledger_rows_carry_provenance_and_ids(self, hmrc):
        _, ledger = hmrc
        for row in ledger[:10]:
            assert row["fact_id"].startswith("uk:uk_hmrc:")
            assert "routing rule" in row["routed_because"]
            assert row["staged"]["conditions"]["basis"] in (
                "outturn", "provisional",
            )

    def test_survey_outcomes_stay_scorecard_side(self, dwp):
        scores, _ = dwp
        hbai = [s for s in scores if s.source_model == "dwp_hbai_frs"]
        assert len(hbai) == 1040  # HBAI is a survey outcome, not admin

    def test_staging_file_is_deterministic(self, tmp_path):
        rows = [
            ledger_row("uk_x", {"a": 1}, "test"),
            ledger_row("uk_x", {"a": 2}, "test"),
        ]
        p = tmp_path / "ledger.jsonl"
        assert write_ledger_staging(rows, p) == 2
        first = p.read_text()
        write_ledger_staging(list(reversed(rows)), p)
        assert p.read_text() == first  # sorted by fact id

    def test_duplicate_fact_ids_raise(self, tmp_path):
        rows = [ledger_row("uk_x", {"a": 1}, "test")] * 2
        with pytest.raises(ValueError, match="duplicate"):
            write_ledger_staging(rows, tmp_path / "ledger.jsonl")

    def test_identical_cells_in_different_sections_stay_distinct(self):
        staged = {"value": 1.0, "conditions": {"line_item": "DWP"}}
        a = ledger_row("uk_obr", staged, "r", derived={"section": "cap"})
        b = ledger_row("uk_obr", staged, "r", derived={"section": "total"})
        assert a["fact_id"] != b["fact_id"]


class TestOBR:
    def test_consumed_lines_match_pe_uk_data_exactly(self, obr):
        scores, _ = obr
        consumed = [
            s
            for s in scores
            if s.calibration_relationship is CR.CONSUMED_AS_TARGET
        ]
        # 25 line-families (12 receipts/CT/NICs heads incl. the 3.4/3.8
        # twins + 13 welfare (line, section) pairs) × 6 forecast years.
        assert len(consumed) == 150
        assert all(s.conditions["basis"] == "forecast" for s in consumed)
        assert all(
            "calibration_basis" in s.publication for s in consumed
        )
        welfare = {
            (s.conditions["line_item"], s.conditions["section"])
            for s in consumed
            if s.conditions["table"] == "4.9"
        }
        assert ("Universal credit", "welfare_cap") in welfare
        assert ("Universal credit", "outside_welfare_cap") in welfare
        assert ("State pension", "outside_welfare_cap") in welfare

    def test_measures_are_reform_worlds_with_verbatim_titles(self, obr):
        scores, _ = obr
        measures = [
            s
            for s in scores
            if s.source_model == "hmt_scorecard_obr_database"
        ]
        assert len(measures) == 24304
        for s in measures[:50]:
            assert s.reform.framework == "policy_ref"
            assert s.reform.reform["policy"].startswith("uk_obr_measure:")
            assert "measure" in s.conditions
            assert "fiscal_event" in s.conditions

    def test_duplicate_titled_components_disambiguated(self, obr):
        scores, _ = obr
        pa95 = [
            s
            for s in scores
            if s.conditions.get("fiscal_event") == "Budget 1995"
            and s.conditions.get("measure") == "Increase PA"
            and s.conditions["fy"] == "1996-97"
        ]
        assert len(pa95) == 3
        assert {s.conditions.get("component_seq") for s in pa95} == {
            None, "2", "3",
        }
        # Same measure world — the database's unit of identity is the
        # titled line; components are conditions axes.
        assert len({s.reform.key() for s in pa95}) == 1

    def test_efo_vintage_split(self, obr):
        scores, _ = obr
        efo = [s for s in scores if s.source_model == "obr_efo_forecast"]
        vintages = {
            (s.conditions["table"], s.conditions["data_vintage"])
            for s in efo
        }
        assert ("3.4", "march_2026_efo") in vintages
        assert ("4.9", "november_2025_efo") in vintages
        assert ("4.9", "march_2026_efo") not in vintages


class TestDWP:
    def test_period_derived_from_fy(self, dwp):
        scores, _ = dwp
        assert min(s.period for s in scores) == 1994  # not 1900
        with_fy = [s for s in scores if "fy" in s.conditions]
        for s in with_fy[:200]:
            assert s.conditions["fy"].startswith(str(s.period))

    def test_pc_takeup_seed_source(self, dwp):
        scores, _ = dwp
        pc = [
            s
            for s in scores
            if s.source_model == "dwp_takeup_estimates"
            and s.conditions.get("program") == "pension_credit"
        ]
        assert pc and all(
            s.calibration_relationship is CR.SEED_SOURCE for s in pc
        )

    def test_hb_takeup_held_out_comparator(self, dwp):
        scores, _ = dwp
        hb = [
            s
            for s in scores
            if s.source_model == "dwp_takeup_estimates"
            and s.conditions.get("program") == "housing_benefit"
        ]
        assert hb and all(
            s.calibration_relationship is CR.HELD_OUT for s in hb
        )

    def test_becl_consumption_exact(self, dwp):
        scores, _ = dwp
        becl_cost = [
            s
            for s in scores
            if s.source_model == "dwp_becl"
            and s.metric is Metric.BENEFIT_COST
        ]
        consumed = {
            s.conditions["program"]
            for s in becl_cost
            if s.calibration_relationship is CR.CONSUMED_AS_TARGET
        }
        assert consumed == {
            "state_pension", "universal_credit", "pension_credit",
            "attendance_allowance", "child_benefit",
        }
        # Components of the consumed DLA+PIP aggregate stay held out,
        # and caseloads too (obr.py parses expenditure only).
        for s in becl_cost:
            if s.conditions["program"] in ("dla", "pip"):
                assert s.calibration_relationship is CR.HELD_OUT
        for s in scores:
            if (
                s.source_model == "dwp_becl"
                and s.metric is Metric.CASELOAD
            ):
                assert s.calibration_relationship is CR.HELD_OUT

    def test_uc_admin_consumed(self, dwp):
        scores, _ = dwp
        uc = [s for s in scores if s.source_model == "dwp_uc_admin"]
        assert len(uc) == 5
        assert all(
            s.calibration_relationship is CR.CONSUMED_AS_TARGET for s in uc
        )

    def test_hbai_editions_and_permanent_holdout(self, dwp):
        scores, _ = dwp
        hbai = [s for s in scores if s.source_model == "dwp_hbai_frs"]
        assert {s.conditions["edition"] for s in hbai} == {
            "fye_2025", "fye_2024",
        }
        assert all(
            s.calibration_relationship is CR.HELD_OUT for s in hbai
        )
        assert all(
            "income_concept" in s.conditions
            and "poverty_measure" in s.conditions
            for s in hbai
        )


class TestHMRC:
    def test_ready_reckoner_join_surface(self, hmrc):
        scores, _ = hmrc
        rr = [s for s in scores if s.source_model == "hmrc"]
        assert len(rr) == 225
        slug = (
            "uk_hmrc_rr:income_tax_rates:"
            f"{slugify('Change basic rate by 1p')}"
        )
        basic = [
            s
            for s in rr
            if s.reform.reform["policy"] == slug and s.period == 2026
        ]
        assert len(basic) == 1
        assert basic[0].conditions["fy"] == "2026-27"

    def test_spi_family_seeded(self, hmrc):
        scores, _ = hmrc
        spi = [s for s in scores if s.source_model == "hmrc_spi"]
        seeded = [
            s
            for s in spi
            if s.calibration_relationship is CR.SEED_SOURCE
        ]
        consumed = [
            s
            for s in spi
            if s.calibration_relationship is CR.CONSUMED_AS_TARGET
        ]
        assert len(seeded) == 726
        assert len(consumed) == 36
        for s in consumed:
            assert s.metric is Metric.TAX_LIABILITY
            assert s.conditions["band"].lower() in (
                "all", "total", "all taxpayers",
            )


class TestHMT:
    def test_counts_and_suppression(self, hmt):
        scores, _ = hmt
        assert len(scores) == 1368
        assert sum(1 for s in scores if s.status == "suppressed") == 31
        costings = [
            s
            for s in scores
            if s.source_model == "hmt_costing_obr_certified"
        ]
        assert all(
            s.metric is Metric.EXCHEQUER_IMPACT for s in costings
        )
        assert all(
            s.reform.framework == "policy_ref" for s in costings
        )

    def test_da_income_concept_verbatim(self, hmt):
        scores, _ = hmt
        da = [
            s
            for s in scores
            if s.source_model == "hmt_distributional_analysis_igotm"
        ]
        assert len(da) == 150
        assert all("equivalisation" in s.conditions for s in da)


class TestIFS:
    def test_steady_state_baseline_world(self, ifs):
        scores = ifs[0]
        with_baseline = [
            s for s in scores if s.reform.baseline is not None
        ]
        assert len(with_baseline) == 108
        for s in with_baseline:
            assert s.reform.baseline == {
                "policy": "ifs_2cl_fp_removal_rolled_out"
            }
            assert (
                s.conditions["baseline_policy"]
                == "ifs_2cl_fp_removal_rolled_out"
            )
            assert s.conditions["horizon"] == "steady_state"

    def test_pentagon_leg_is_reform_keyed(self, ifs):
        scores = ifs[0]
        two_child = [
            s
            for s in scores
            if s.conditions.get("measure") == "Remove two-child limit"
            and s.metric is Metric.POVERTY_COUNT_CHANGE
        ]
        children = [
            s
            for s in two_child
            if s.unit_concept.value == "children_under_18"
        ]
        assert [s.value for s in children] == [-540000.0]


class TestUKMODJRF:
    def test_validation_series_axis(self, ukmod_jrf):
        scores, _, _ = ukmod_jrf
        series = {
            s.conditions.get("series")
            for s in scores
            if s.source == "ukmod"
        }
        assert {
            "ukmod_simulated", "official_estimate", "input_data", "hbai",
        } <= series

    def test_cempa_package_world(self, ukmod_jrf):
        scores, _, _ = ukmod_jrf
        pkg = [
            s
            for s in scores
            if s.reform.framework == "policy_ref"
            and s.reform.reform["policy"]
            == "uk_autumn_budget_2025_package_cempa"
        ]
        assert len(pkg) == 209
        assert {s.conditions["scenario"] for s in pkg} == {
            "reform", "reform_minus_baseline",
        }

    def test_persistent_poverty_windows(self, ukmod_jrf):
        scores, _, _ = ukmod_jrf
        windows = [s for s in scores if s.period_start is not None]
        assert len(windows) == 28
        for s in windows:
            assert (s.period_start, s.period_end) == (2021, 2023)
            assert s.conditions["window_kind"] == "annual_average"

    def test_amount_basis_remap(self, ukmod_jrf):
        scores, _, _ = ukmod_jrf
        assert not any(
            s.conditions.get("basis") for s in scores
        )  # weekly/annual lives in amount_basis, basis keeps UK meaning
        assert any(
            s.conditions.get("amount_basis") == "weekly" for s in scores
        )


class TestRF:
    def test_attribution_rows_distinct(self, rf):
        scores, _, _ = rf
        attributed = [s for s in scores if "attribution" in s.conditions]
        assert len(attributed) == 8

    def test_uprating_parameter_checks(self, rf):
        scores, _, _ = rf
        uprating = [
            s for s in scores if s.metric is Metric.BENEFIT_UPRATING
        ]
        assert len(uprating) == 11
        assert all("program" in s.conditions for s in uprating)


class TestUKPermanentHoldouts:
    def test_poverty_counts_never_calibrate(self):
        from scorecard_db.relationships import never_calibrate

        assert never_calibrate(Metric.POVERTY_COUNT)
        assert never_calibrate(Metric.PERSISTENT_POVERTY_RATE)


class TestUKIngestIntoDB:
    """One thin end-to-end check: a small adapter lands in SQLite with
    baseline keys registered and lanes set (the big ones are covered by
    staging tests; the runner's DB path is shared machinery)."""

    def test_ifs_ingest_roundtrip(self, tmp_path):
        from scorecard_db.baselines import register_baselines
        from scorecard_db.ingest_uk_ifs import ingest

        db_path = tmp_path / "uk.db"
        stats = ingest(db_path)
        assert stats["scores"] == 268
        db = ScorecardDB(db_path)
        register_baselines(db)
        row = db.conn.execute(
            "SELECT COUNT(*) n FROM external_scores"
            " WHERE source='ifs' AND baseline_key != ?",
            (BASELINE.baseline_key(),),
        ).fetchone()
        assert row["n"] == 108  # the steady-state-baseline block
        label = db.conn.execute(
            "SELECT label FROM baselines b JOIN external_scores s"
            " ON s.baseline_key = b.baseline_key"
            " WHERE s.source='ifs' AND b.label != 'current_law' LIMIT 1"
        ).fetchone()
        assert label["label"] == "ifs_2cl_fp_removal_rolled_out"
        db.close()
