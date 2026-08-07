"""The campaign day-1 attach: exact-match resolution against ingested
vocabulary, exhibit deferral, idempotency, and provenance fidelity."""

import json
import shutil
import sqlite3

import pytest

from scorecard_db.export_populations import REPO
from scorecard_db.ingest_campaign import STAGED_US, _normalize, ingest

COMMITTED_DB = REPO / "data" / "scorecard.db"


@pytest.fixture()
def db_copy(tmp_path):
    path = tmp_path / "scorecard.db"
    shutil.copy(COMMITTED_DB, path)
    return path


def test_normalizers():
    cond, reform = _normalize(
        "cpsp",
        {
            "conditions": {
                "geography": "us",
                "subgroup": "children_under_18",
                "policy_scenario": "TCJA CTC",
            }
        },
    )
    assert cond == {"geography": "US", "subgroup": "children_under_18"}
    assert reform == "tcja_ctc"

    cond, reform = _normalize(
        "tpc",
        {"conditions": {"provision_row": "X", "option": "Option 2"}},
    )
    assert cond["provision"] == "X"
    assert cond["baseline_policy"] == ("current_law_plus_senate_obbba_title_vii")
    assert reform is None

    cond, _ = _normalize(
        "jct", {"conditions": {"provision": "4.", "baseline": "present_law"}}
    )
    assert "baseline" not in cond
    assert cond["row_kind"] == "provision"

    cond, _ = _normalize(
        "cbo",
        {"conditions": {"note": "outlay_portion_of_refundable_credits"}},
    )
    assert cond["variant"] == "outlay_portion_of_refundable_credits"
    assert "note" not in cond

    with pytest.raises(ValueError, match="no normalizer"):
        _normalize("obr", {"conditions": {}})


def test_full_attach_on_committed_db(db_copy):
    summary = ingest(db_copy)
    assert summary["attached"] == 30
    assert summary["families"] == {
        "cbo_free_joins": 9,
        "cpsp_ctc_2024": 8,
        "jct_obbba_provision4": 1,
        "pwbm_ss_elimination": 2,
        "tpc_t25_0209_t26_0029": 10,
    }
    assert len(summary["exhibits_deferred"]) == 4
    assert all("marginal increment" in e for e in summary["exhibits_deferred"])

    conn = sqlite3.connect(db_copy)
    conn.row_factory = sqlite3.Row
    # Provenance verbatim from the staging: real engine + certified bundle.
    rows = conn.execute(
        "SELECT DISTINCT engine_version, data_bundle FROM pe_results"
        " WHERE run_id LIKE 'campaign-%'"
    ).fetchall()
    assert [tuple(r) for r in rows] == [
        (
            "1.764.6",
            "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z",
        )
    ]
    # The CPSP TCJA-world attach lands on the claim whose reform is the
    # scenario (value 13.3% — the brief's number).
    row = conn.execute(
        """SELECT s.value, r.computed_value FROM pe_results r
           JOIN external_scores s USING (claim_id)
           WHERE r.run_id = 'campaign-20260802-cpsp'
           AND json_extract(s.reform_json, '$.reform.policy') = 'tcja_ctc'
           AND json_extract(s.conditions, '$.subgroup')
               = 'children_under_18'"""
    ).fetchone()
    assert row["value"] == pytest.approx(0.133)
    assert row["computed_value"] == pytest.approx(0.16771, abs=1e-4)
    # The JCT provision-4 claim now stacks the campaign's last-in-stack
    # construction on top of the five per-release RV results.
    n = conn.execute(
        """SELECT COUNT(*) FROM pe_results WHERE claim_id IN
           (SELECT claim_id FROM pe_results
            WHERE run_id = 'campaign-20260802-obbba')"""
    ).fetchone()[0]
    assert n == 6
    # Sign convention: the claim scores the forward extension (negative);
    # the campaign scored the expiry reversal and negated it (exact for
    # the same static world pair). Ratio 1.87 = the known last-in-stack
    # position story, and both sides must be revenue losses.
    jct = conn.execute(
        """SELECT r.computed_value, s.value, r.pe_construction
           FROM pe_results r JOIN external_scores s USING (claim_id)
           WHERE r.run_id = 'campaign-20260802-obbba'"""
    ).fetchone()
    assert jct["computed_value"] == pytest.approx(-91169531318.0)
    assert jct["value"] < 0 and jct["computed_value"] < 0
    assert jct["computed_value"] / jct["value"] == pytest.approx(1.87, abs=0.01)
    assert jct["pe_construction"].startswith("scored as expiry reversal")
    # CBO joins: every row names FY-vs-CY, so none is comparable; the
    # SNAP total attaches the held-out budget-authority claim and says so.
    statuses = {
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT status FROM pe_results"
            " WHERE run_id = 'campaign-20260802-us-joins'"
        )
    }
    assert statuses == {"constructed", "concept_mismatch"}
    snap = conn.execute(
        """SELECT r.pe_construction FROM pe_results r
           JOIN external_scores s USING (claim_id)
           WHERE r.run_id = 'campaign-20260802-us-joins'
           AND s.metric = 'benefit_cost'
           AND json_extract(s.conditions, '$.program') = 'snap'"""
    ).fetchone()
    assert "BUDGET AUTHORITY" in snap["pe_construction"]
    conn.close()


def test_reingest_idempotent(db_copy):
    first = ingest(db_copy)
    again = ingest(db_copy)
    assert again == first
    conn = sqlite3.connect(db_copy)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id LIKE 'campaign-%'"
    ).fetchone()[0]
    conn.close()
    assert n == first["attached"]


def test_reingest_spares_other_campaign_directories(db_copy):
    # Deletion is scoped to the run_ids in THIS staged directory: results
    # another campaign directory (e.g. the UK families) ingested under
    # campaign-prefixed run_ids of their own must survive a US rerun.
    ingest(db_copy)
    conn = sqlite3.connect(db_copy)
    any_claim = conn.execute("SELECT claim_id FROM external_scores LIMIT 1").fetchone()[
        0
    ]
    conn.execute(
        "INSERT INTO pe_results (claim_id, computed_value, status,"
        " engine_version, data_bundle, pe_construction, run_id,"
        " computed_at, annotations)"
        " VALUES (?, 1.0, 'constructed', '2.89.2', 'populace-uk-test',"
        " 'sentinel', 'campaign-20260802-ukfake', '2026-08-06', '[]')",
        (any_claim,),
    )
    conn.commit()
    conn.close()

    ingest(db_copy)
    conn = sqlite3.connect(db_copy)
    survived = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id = 'campaign-20260802-ukfake'"
    ).fetchone()[0]
    conn.close()
    assert survived == 1


def test_zero_match_aborts_with_nothing_written(db_copy, tmp_path):
    def campaign_rows():
        conn = sqlite3.connect(db_copy)
        n = conn.execute(
            "SELECT COUNT(*) FROM pe_results WHERE run_id LIKE 'campaign-%'"
        ).fetchone()[0]
        conn.close()
        return n

    before = campaign_rows()
    staged = tmp_path / "staged"
    staged.mkdir()
    for p in STAGED_US.glob("*.jsonl"):
        (staged / p.name).write_text(p.read_text())
    bad = staged / "pwbm_ss_elimination.jsonl"
    rows = [json.loads(line) for line in bad.read_text().splitlines()]
    rows[0]["external_claim_match"]["conditions"]["provision"] = "nonsense"
    bad.write_text("\n".join(json.dumps(r) for r in rows))

    with pytest.raises(ValueError, match="0 claims match"):
        ingest(db_copy, staged_dir=staged)
    # The abort happens before the write transaction: any pre-existing
    # campaign rows (the committed DB carries them) survive untouched.
    assert campaign_rows() == before
