"""The populace reform-validation ingest: exact row accounting, claim
periods keyed to what the claim describes, per-row engine pins, one result
per claim per release, OBBBA attachment to the canonical harvest claims,
and the doctrine assignments."""

import json
import sqlite3

import pytest

from scorecard_db import ScorecardDB
from scorecard_db.ingest_reform_validation import (
    OBBBA_PROVISIONS,
    RAW,
    RUN_PREFIX,
    ingest,
)
from scorecard_db.models import (
    ExternalScore,
    Metric,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

L0 = "populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701"
BUILDO = "populace-us-2024-buildo-sparse-rmloss100-22bd902-20260722T232627Z"

# The five artifacts hold 640 rows total; the ingest must account for every
# one: 90 scored OBBBA rows (x2 results, FY2026+FY2027), 495 other results,
# 44 repeal constructions superseded by their direct-level twins, and 11
# null-benchmark skips.
TOTAL_ROWS = 640
EXPECTED = {
    "releases": 5,
    "results": 675,
    "skipped": 11,
    "superseded_repeal_constructions": 44,
}


@pytest.fixture(scope="module")
def summary_and_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("rv") / "scorecard.db"
    return ingest(path), path


@pytest.fixture()
def conn(summary_and_db):
    conn = sqlite3.connect(summary_and_db[1])
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_exact_row_accounting(summary_and_db):
    summary, _ = summary_and_db
    for key, want in EXPECTED.items():
        assert summary[key] == want, key
    # Fresh DB (no harvest): every OBBBA result hangs off a minted
    # fallback claim — 18 provisions x 2 fiscal years.
    assert summary["obbba_attached_results"] == 0
    assert summary["obbba_fallback_claims"] == 36
    assert summary["claims_upserted"] == 205 + 36
    obbba_results = 180  # 90 scored rows x (FY2026 + FY2027)
    obbba_rows = obbba_results // 2
    assert (summary["results"] - obbba_results) + obbba_rows + summary[
        "superseded_repeal_constructions"
    ] + summary["skipped"] == TOTAL_ROWS
    assert TOTAL_ROWS == sum(
        len(json.loads(p.read_text())["reforms"]) for p in RAW.glob("*.json")
    )


def test_one_result_per_claim_per_release(conn):
    total, distinct = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT claim_id || '|' || data_bundle)"
        " FROM pe_results WHERE run_id LIKE ?",
        (f"{RUN_PREFIX}%",),
    ).fetchone()
    assert total == EXPECTED["results"]
    assert distinct == total


def test_claim_periods_key_what_the_claim_describes(conn):
    # GA HB1001's fiscal note scores FY2028 even though PE simulates 2026.
    ga = conn.execute(
        "SELECT period, time_basis FROM external_scores"
        " WHERE source_column = 'state.ga.hb1001'"
    ).fetchall()
    assert [(r["period"], r["time_basis"]) for r in ga] == [(2028, "fiscal_year")]
    # IRS SOI actuals are TY2023 figures, not the 2024 simulation year.
    assert {
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT period FROM external_scores WHERE source='irs_soi'"
        )
    } == {2023}
    # ND HB1388's note quotes a per-year average over the 2025-27 biennium.
    nd = conn.execute(
        "SELECT period, time_basis, period_start, period_end,"
        " json_extract(conditions, '$.window_kind') AS wk"
        " FROM external_scores WHERE source_column = 'state.nd.hb1388'"
    ).fetchone()
    assert tuple(nd) == (2027, "fiscal_year", 2026, 2027, "annual_average")


def test_census_averages_carry_ranges(conn):
    ranged = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source = 'census'"
        " AND period_start = 2022 AND period_end = 2024"
        " AND json_extract(conditions, '$.window_kind') = 'annual_average'"
    ).fetchone()[0]
    assert ranged == 102
    single = conn.execute(
        "SELECT period, period_start FROM external_scores"
        " WHERE source_column = 'spm_poverty_us'"
    ).fetchone()
    assert tuple(single) == (2024, None)


def test_l0_offline_rows_keep_their_own_engine_pin(conn):
    # The l0-refit backfill note documents 33 rows scored offline at
    # policyengine-us 1.729.0 — 8 State-reform rows, the 18-row
    # federal-EITC-by-state suite, and the populace#345 expansion's 7
    # program levels; everything else in that release at 1.752.2.
    by_engine = {
        r[0]: r[1]
        for r in conn.execute(
            "SELECT engine_version, COUNT(*) FROM pe_results"
            " WHERE data_bundle = ? GROUP BY 1",
            (L0,),
        )
    }
    assert by_engine == {"1.729.0": 33, "1.752.2": 94}
    offline = {
        r[0]
        for r in conn.execute(
            """SELECT s.source_column FROM pe_results r
               JOIN external_scores s USING (claim_id)
               WHERE r.data_bundle = ? AND r.engine_version = '1.729.0'""",
            (L0,),
        )
    }
    # Stated literally (not imported from the module under test): the
    # backfill note's "VA/OH/MO/SC EITC-family, CO FAC, ID/UT CTC".
    program_levels = {
        "state_va_eitc_cli",
        "state_oh_eitc",
        "state_mo_wftc",
        "state_sc_eitc",
        "state_co_fac",
        "state_id_ctc",
        "state_ut_ctc",
    }
    assert program_levels <= offline
    fed_eitc = {c for c in offline if c.startswith("fed_eitc_")}
    fiscal = {c for c in offline if c.startswith("state.")}
    assert len(fed_eitc) == 18
    assert len(fiscal) == 8
    assert offline == fed_eitc | fiscal | program_levels


def _plant_harvest(path, rows):
    """Insert JCX-35-25 harvest claims for the given scored OBBBA rows;
    returns {(row_id, fy): claim_id}."""
    db = ScorecardDB(path)
    planted = {}
    for r in rows:
        for fy, value in (
            (2026, r["jct"]["score"]),
            (2027, r["jct"]["score_fy2027"]),
        ):
            claim = ExternalScore(
                source="jct",
                metric=Metric.REVENUE_CHANGE,
                unit_concept=UnitConcept.USD,
                period=fy,
                time_basis=TimeBasis.FISCAL_YEAR,
                value=float(value),
                conditions={
                    "bill_version": "JCX-35-25",
                    "geography": "US",
                    "provision": OBBBA_PROVISIONS[r["id"]],
                },
                reform=ReformRef(
                    framework="policy_ref",
                    reform={"policy": "obbba_enacted_title_vii"},
                ),
                publication={"title": "JCX-35-25"},
                value_kind="usd",
            )
            planted[(r["id"], fy)] = claim.claim_id()
            db.upsert_scores([claim])
    db.close()
    return planted


def _scored_obbba(artifact):
    return [
        r
        for r in artifact["reforms"]
        if r["category"] == "OBBBA" and r["jct"].get("score") is not None
    ]


def test_obbba_results_attach_to_harvest_claims(tmp_path):
    # With the harvested JCX-35-25 claims present, the registry's OBBBA
    # computations attach to them (issue #15: harvest is canonical) — both
    # fiscal years — and no jct claims are minted at all.
    path = tmp_path / "scorecard.db"
    buildo = json.loads((RAW / f"{BUILDO}.json").read_text())
    planted = _plant_harvest(path, _scored_obbba(buildo))
    assert len(planted) == 36  # 18 provisions x 2 fiscal years

    summary = ingest(path)
    assert summary["obbba_attached_results"] == 180  # 90 scored rows x 2
    assert summary["obbba_fallback_claims"] == 0
    assert summary["claims_upserted"] == 205

    conn = sqlite3.connect(path)
    for fy in (2026, 2027):
        cid = planted[("obbba_salt_limit", fy)]
        rows = conn.execute(
            "SELECT pe_construction FROM pe_results WHERE claim_id = ?"
            " ORDER BY computed_at",
            (cid,),
        ).fetchall()
        assert len(rows) == 5
        modes = [r[0].split(":")[2] for r in rows]
        # f0af251's own totals chain (a stack of its own construction);
        # l0-refit scored in isolation; buildi onward stack per JCX.
        assert modes == [
            "stacked_chained",
            "isolated",
            "jcx_stacked",
            "jcx_stacked",
            "jcx_stacked",
        ]
        assert all(r[0].endswith(f"cy2026_for_fy{fy}") for r in rows)
    # No registry-minted SALT claim shadows the harvest ones.
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source_column = 'obbba_salt_limit'"
    ).fetchone()[0]
    assert n == 0
    conn.close()


def test_partial_harvest_refused(tmp_path):
    # A harvest holding only some provisions would split OBBBA results
    # between canonical claims and minted fallbacks — the ingest refuses
    # the mixed state instead of silently producing it.
    path = tmp_path / "scorecard.db"
    buildo = json.loads((RAW / f"{BUILDO}.json").read_text())
    salt = [r for r in _scored_obbba(buildo) if r["id"] == "obbba_salt_limit"]
    _plant_harvest(path, salt)
    with pytest.raises(ValueError, match="partial JCX-35-25 harvest"):
        ingest(path)


def test_fresh_db_fallback_uses_latest_benchmark(conn):
    # Early artifacts carry superseded benchmark columns (the 7/06 audit:
    # mortgage FY2027 3,398M -> 3,110M). Fallback claims — same claim_id
    # across releases — must store the newest artifact's value.
    value = conn.execute(
        "SELECT value FROM external_scores"
        " WHERE source_column = 'obbba_mortgage_interest_limit'"
        " AND period = 2027"
    ).fetchone()[0]
    assert value == pytest.approx(3110000000.0)


def test_failed_ingest_leaves_db_untouched(tmp_path):
    # All parsing and validation happens before any write: an unparseable
    # artifact aborts the run with the DB exactly as it was.
    path = tmp_path / "scorecard.db"
    first = ingest(path)

    bad_raw = tmp_path / "raw"
    bad_raw.mkdir()
    for p in RAW.glob("*.json"):
        (bad_raw / p.name).write_text(p.read_text())
    bad_path = bad_raw / f"{BUILDO}.json"
    artifact = json.loads(bad_path.read_text())
    ga = next(r for r in artifact["reforms"] if r["id"] == "state.ga.hb1001")
    ga["jct"]["window"] = "not a window"
    bad_path.write_text(json.dumps(artifact))

    with pytest.raises(ValueError, match="cannot parse claim period"):
        ingest(path, raw_dir=bad_raw)

    _assert_unchanged(path, first)


def _assert_unchanged(path, first):
    conn = sqlite3.connect(path)
    n_results = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id LIKE ?",
        (f"{RUN_PREFIX}%",),
    ).fetchone()[0]
    n_claims = conn.execute("SELECT COUNT(*) FROM external_scores").fetchone()[0]
    conn.close()
    assert n_results == first["results"]
    assert n_claims == first["claims_upserted"]


def test_write_phase_failure_rolls_back(tmp_path, monkeypatch):
    # The replacement is one transaction: a failure MID-WRITE (after the
    # deletes, during the result inserts) must roll everything back — not
    # leave claims without results.
    path = tmp_path / "scorecard.db"
    first = ingest(path)

    real = ScorecardDB.result_row
    calls = {"n": 0}

    def sabotaged(r):
        row = real(r)
        calls["n"] += 1
        if calls["n"] == 300:  # deep in the batch
            return row[:2] + ("bogus_status",) + row[3:]
        return row

    monkeypatch.setattr(ScorecardDB, "result_row", staticmethod(sabotaged))
    with pytest.raises(sqlite3.IntegrityError):
        ingest(path)
    monkeypatch.undo()

    _assert_unchanged(path, first)
    # And the DB is still healthy: a clean re-ingest works.
    assert ingest(path) == first


def test_il_repeal_bundle_is_its_own_claim(conn):
    # il_ctc is defined as a share of il_eitc, so the repeal benchmark
    # quotes the combined actuals — a distinct claim from either program's
    # direct level, with a constructed repeal-delta result.
    claims = {
        r["program"]: r
        for r in conn.execute(
            "SELECT program, value, claim_id FROM external_scores"
            " WHERE source = 'il_admin'"
        )
    }
    assert claims["il_eitc"]["value"] == pytest.approx(437387169.0)
    assert claims["il_ctc"]["value"] == pytest.approx(50000000.0)
    assert claims["il_eitc+il_ctc"]["value"] == pytest.approx(487387169.0)
    rows = conn.execute(
        "SELECT status, pe_construction FROM pe_results WHERE claim_id = ?",
        (claims["il_eitc+il_ctc"]["claim_id"],),
    ).fetchall()
    assert len(rows) == 4  # l0-refit + buildi/j/o carry the repeal suite
    assert all(
        r["status"] == "constructed"
        and r["pe_construction"].startswith("repeal_delta:")
        for r in rows
    )
    # The bundle sums an IDOR TY2023 EITC actual with GOMB's TY2024 CTC
    # budget estimate — the mixed vintage rides on the claim.
    vintage = conn.execute(
        "SELECT json_extract(conditions, '$.data_vintage')"
        " FROM external_scores WHERE claim_id = ?",
        (claims["il_eitc+il_ctc"]["claim_id"],),
    ).fetchone()[0]
    assert vintage == "ty2023_eitc_actual+ty2024_ctc_estimate"


def test_ut_ctc_is_a_concept_flag(conn):
    # UT Tax Commission counts amount CLAIMED (pre-offset); PE's ut_ctc is
    # the nonrefundable liability-capped credit. The artifact: "treat
    # large errors as a concept flag first."
    rows = conn.execute(
        """SELECT r.status,
                  json_extract(s.conditions, '$.benchmark_concept') AS bc
           FROM pe_results r JOIN external_scores s USING (claim_id)
           WHERE s.source = 'ut_admin' AND s.program = 'ut_ctc'""",
    ).fetchall()
    assert len(rows) == 4  # l0-refit + buildi/j/o
    assert all(
        r["status"] == "concept_mismatch" and r["bc"] == "amount_claimed_pre_offset"
        for r in rows
    )


def test_approximate_windows_are_constructed(conn):
    # MI HB4170's fiscal note hedges its own window ("annual
    # (approximate)") — never comparable.
    rows = conn.execute(
        """SELECT r.status FROM pe_results r
           JOIN external_scores s USING (claim_id)
           WHERE s.source_column = 'state.mi.hb4170'""",
    ).fetchall()
    assert len(rows) == 4
    assert all(r[0] == "constructed" for r in rows)


def test_ks_hb2629_declares_its_data_vintage(conn):
    # KDOR's benchmark simulates TY2026 policy on TY2024 data.
    row = conn.execute(
        "SELECT json_extract(conditions, '$.data_vintage')"
        " FROM external_scores WHERE source_column = 'state.ks.hb2629'"
    ).fetchone()
    assert row[0] == "ty2024_data"


def test_matching_repeal_constructions_superseded_by_levels(conn):
    # state_repeal_ca_eitc's benchmark equals the CA FTB actual, so the
    # direct level is the claim's only (and better) construction.
    rows = conn.execute(
        """SELECT r.pe_construction FROM external_scores s
           JOIN pe_results r USING (claim_id)
           WHERE s.program = 'ca_eitc' AND s.source = 'ca_admin'""",
    ).fetchall()
    assert len(rows) == 4  # one per release that scored it, no duplicates
    assert all(r[0].startswith("level:") for r in rows)


def test_fiscal_year_and_shifted_claims_are_constructed(conn):
    bad = conn.execute(
        """SELECT COUNT(*) FROM pe_results r
           JOIN external_scores s USING (claim_id)
           WHERE r.run_id LIKE ? AND r.status = 'comparable'
           AND (s.time_basis = 'fiscal_year' OR s.period_start IS NOT NULL)""",
        (f"{RUN_PREFIX}%",),
    ).fetchone()[0]
    assert bad == 0


def test_census_spm_held_out(conn):
    rows = conn.execute(
        "SELECT calibration_relationship FROM external_scores"
        " WHERE source = 'census' AND metric = 'poverty_rate'"
    ).fetchall()
    assert rows and all(r[0] == "held_out" for r in rows)


def test_soi_and_jct_te_targets_marked_consumed(conn):
    rows = conn.execute(
        "SELECT calibration_relationship FROM external_scores"
        " WHERE source = 'irs_soi'"
        " OR source_column LIKE 'jct.tax_expenditures%'"
    ).fetchall()
    assert rows and all(r[0] == "consumed_as_target" for r in rows)


def test_cbo_option_declares_pre_obbba_baseline(conn):
    row = conn.execute(
        "SELECT json_extract(reform_json, '$.baseline.policy'),"
        " json_extract(conditions, '$.baseline_policy')"
        " FROM external_scores JOIN reforms USING (reform_key)"
        " WHERE source_column = 'federal.cbo_rates_plus_1pt'"
    ).fetchone()
    assert tuple(row) == ("pre_obbba_current_law", "pre_obbba_current_law")


def test_tax_expenditure_metric_populated(conn):
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE metric = 'tax_expenditure'"
    ).fetchone()[0]
    # 5 jct.tax_expenditures.* targets + te_* holdouts minus the two
    # unscoreable expenditures (standard deduction, itemized total)
    assert n == 8


def test_reingest_idempotent(summary_and_db):
    first, path = summary_and_db
    again = ingest(path)
    assert again == first
    conn = sqlite3.connect(path)
    n_results = conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0]
    n_claims = conn.execute("SELECT COUNT(*) FROM external_scores").fetchone()[0]
    conn.close()
    assert n_results == first["results"]
    assert n_claims == first["claims_upserted"]


def test_results_carry_executed_baselines_per_mode(summary_and_db):
    # Level/reform/repeal rows executed current law; isolated OBBBA
    # rows the shared pre_obbba_expiry_2026 world; stacked OBBBA rows
    # one registered world per (chain, provision). NULL provenance on
    # a clean ingest is a defect.
    _, path = summary_and_db
    import sqlite3

    from scorecard_db.ingest_reform_validation import (
        _CURRENT_LAW_KEY,
        _ISOLATED_KEY,
        OBBBA_PROVISIONS,
        _obbba_baseline_key,
    )

    conn = sqlite3.connect(path)
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM pe_results WHERE run_id LIKE ?"
            " AND baseline_key IS NULL",
            (f"{RUN_PREFIX}%",),
        ).fetchone()[0]
        == 0
    )
    by_key = dict(
        conn.execute(
            "SELECT baseline_key, COUNT(*) FROM pe_results"
            " WHERE run_id LIKE ? GROUP BY 1",
            (f"{RUN_PREFIX}%",),
        )
    )
    conn.close()
    assert by_key[_ISOLATED_KEY] == 36
    assert by_key[_CURRENT_LAW_KEY] == 675 - 180
    # Stacked runs: one distinct executed world per (chain, provision) —
    # f0af251's chain carries 2 results per provision (both FYs), the
    # buildi+ producer chain 6 (3 releases x 2 FYs). Never a collapsed
    # family key.
    f0_keys = {
        _obbba_baseline_key("stacked_chained", pid): pid for pid in OBBBA_PROVISIONS
    }
    producer_keys = {
        _obbba_baseline_key("jcx_stacked", pid): pid for pid in OBBBA_PROVISIONS
    }
    assert all(by_key[k] == 2 for k in f0_keys)
    assert all(by_key[k] == 6 for k in producer_keys)
    assert (
        36
        + (675 - 180)
        + sum(by_key[k] for k in f0_keys)
        + sum(by_key[k] for k in producer_keys)
        == 675
    )


def test_chain_ordinals_are_raw_and_stacked_only(summary_and_db):
    # f0af251's CDCC sits at RAW chain position 17 — after the unscored
    # senior-deduction link that feeds its baseline — and isolated rows
    # carry no position token (their world is the shared expiry
    # baseline).
    _, path = summary_and_db
    import sqlite3

    conn = sqlite3.connect(path)
    cdcc = conn.execute(
        """SELECT r.pe_construction FROM pe_results r
           JOIN external_scores s USING (claim_id)
           WHERE r.data_bundle LIKE '%f0af251%'
           AND s.source_column = 'obbba_cdcc'
           LIMIT 1"""
    ).fetchone()[0]
    assert ":chain_pos17:" in cdcc
    stray = conn.execute(
        "SELECT COUNT(*) FROM pe_results"
        " WHERE pe_construction LIKE '%isolated%chain_pos%'"
    ).fetchone()[0]
    conn.close()
    assert stray == 0
