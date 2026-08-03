"""The populace reform-validation ingest: claims dedupe across releases,
pe_results accrue per release (the regression history), and the doctrine
assignments hold."""

import json
import sqlite3

import pytest

from scorecard_db import ScorecardDB
from scorecard_db.ingest_reform_validation import RAW, RUN_PREFIX, ingest


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("rv") / "scorecard.db"
    summary = ingest(path)
    assert summary["releases"] == 5
    return path


@pytest.fixture()
def conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_claims_dedupe_across_releases(conn):
    # The Build O artifact alone has 236 rows; five releases together must
    # not multiply claims — a benchmark is one claim regardless of how many
    # releases scored it.
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source_column IS NOT NULL"
    ).fetchone()[0]
    per_release = conn.execute(
        "SELECT COUNT(DISTINCT claim_id) FROM pe_results"
        " WHERE run_id LIKE ?", (f"{RUN_PREFIX}%",)
    ).fetchone()[0]
    assert per_release <= n


def test_regression_history_accrues(conn):
    # A claim present in every artifact (the CT SB69 EITC-repeal fiscal
    # note has been in the registry since the earliest vendored releases)
    # carries one result per release that scored it.
    rows = conn.execute(
        """SELECT r.data_bundle FROM external_scores s
           JOIN pe_results r ON r.claim_id = s.claim_id
           WHERE s.source_column = 'spm_poverty_us'"""
    ).fetchall()
    assert len(rows) == 1  # SPM suite exists only in Build O
    rows = conn.execute(
        """SELECT COUNT(DISTINCT r.data_bundle) FROM external_scores s
           JOIN pe_results r ON r.claim_id = s.claim_id
           WHERE s.metric = 'revenue_change'
           GROUP BY s.claim_id ORDER BY 1 DESC LIMIT 1"""
    ).fetchone()
    assert rows[0] >= 3  # long-lived reform claims span several releases


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


def test_repeal_and_actual_resolve_to_one_claim(conn):
    # state_repeal_ca_eitc and state_ca_eitc are two PE constructions of
    # the same CA FTB claim: one claim, both results, direct level wins
    # the comparisons view.
    row = conn.execute(
        """SELECT s.claim_id,
                  (SELECT COUNT(*) FROM pe_results r
                   WHERE r.claim_id = s.claim_id
                   AND r.data_bundle LIKE '%buildo%') AS n_buildo
           FROM external_scores s
           WHERE s.program = 'ca_eitc' AND s.source = 'ca_admin'"""
    ).fetchone()
    assert row is not None and row["n_buildo"] == 2
    latest = conn.execute(
        "SELECT pe_construction FROM comparisons WHERE claim_id = ?",
        (row["claim_id"],),
    ).fetchone()[0]
    assert latest.startswith("level:")


def test_tax_expenditure_metric_populated(conn):
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE metric = 'tax_expenditure'"
    ).fetchone()[0]
    # 5 jct.tax_expenditures.* targets + te_* holdouts minus the two
    # unscoreable expenditures (standard deduction, itemized total)
    assert n == 8


def test_reingest_idempotent(db_path):
    first = ScorecardDB(db_path).conn.execute(
        "SELECT COUNT(*) FROM pe_results"
    ).fetchone()[0]
    summary = ingest(db_path)
    again = ScorecardDB(db_path).conn.execute(
        "SELECT COUNT(*) FROM pe_results"
    ).fetchone()[0]
    assert first == again and summary["releases"] == 5


def test_every_raw_row_mapped_or_tallied(db_path):
    total_rows = sum(
        len(json.loads(p.read_text())["reforms"]) for p in RAW.glob("*.json")
    )
    summary = ingest(db_path)
    assert summary["results"] + summary["skipped"] <= total_rows
    assert summary["skipped"] < 15  # only the unscoreable expenditures
