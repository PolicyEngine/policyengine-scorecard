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
    assert (
        (summary["results"] - obbba_results)
        + obbba_rows
        + summary["superseded_repeal_constructions"]
        + summary["skipped"]
        == TOTAL_ROWS
    )
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
    assert [(r["period"], r["time_basis"]) for r in ga] == [
        (2028, "fiscal_year")
    ]
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


def test_l0_state_reform_rows_keep_their_own_engine_pin(conn):
    # The l0-refit artifact documents its State-reform rows were scored at
    # policyengine-us 1.729.0; everything else in that release at 1.752.2.
    rows = conn.execute(
        """SELECT s.source LIKE '%_fiscal_note' AS fiscal, r.engine_version,
                  COUNT(*) AS n
           FROM pe_results r JOIN external_scores s USING (claim_id)
           WHERE r.data_bundle = ? GROUP BY 1, 2""",
        (L0,),
    ).fetchall()
    assert {(bool(r["fiscal"]), r["engine_version"]): r["n"] for r in rows} == {
        (True, "1.729.0"): 8,
        (False, "1.752.2"): 119,
    }


def test_obbba_results_attach_to_harvest_claims(tmp_path):
    # With the harvested JCX-35-25 claims present, the registry's OBBBA
    # computations attach to them (issue #15: harvest is canonical) — both
    # fiscal years — and no duplicate jct claims are minted.
    path = tmp_path / "scorecard.db"
    db = ScorecardDB(path)
    buildo = json.loads((RAW / f"{BUILDO}.json").read_text())
    salt = next(r for r in buildo["reforms"] if r["id"] == "obbba_salt_limit")
    harvest_ids = {}
    for fy, value in (
        (2026, salt["jct"]["score"]),
        (2027, salt["jct"]["score_fy2027"]),
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
                "provision": OBBBA_PROVISIONS["obbba_salt_limit"],
            },
            reform=ReformRef(
                framework="policy_ref",
                reform={"policy": "obbba_enacted_title_vii"},
            ),
            publication={"title": "JCX-35-25"},
            value_kind="usd",
        )
        harvest_ids[fy] = claim.claim_id()
        db.upsert_scores([claim])
    db.close()

    summary = ingest(path)
    assert summary["obbba_attached_results"] == 10  # 5 releases x 2 FYs
    assert summary["obbba_fallback_claims"] == 34  # the other 17 provisions

    conn = sqlite3.connect(path)
    for fy, cid in harvest_ids.items():
        rows = conn.execute(
            "SELECT pe_construction FROM pe_results WHERE claim_id = ?"
            " ORDER BY computed_at",
            (cid,),
        ).fetchall()
        assert len(rows) == 5
        modes = [r[0].split(":")[2] for r in rows]
        assert modes == [
            "isolated", "isolated", "jcx_stacked", "jcx_stacked",
            "jcx_stacked",
        ]
        assert all(r[0].endswith(f"cy2026_for_fy{fy}") for r in rows)
    # No registry-minted SALT claim shadows the harvest ones.
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE source_column = 'obbba_salt_limit'"
    ).fetchone()[0]
    assert n == 0
    conn.close()


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
        " FROM external_scores"
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
    n_claims = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
    ).fetchone()[0]
    conn.close()
    assert n_results == first["results"]
    assert n_claims == first["claims_upserted"]
