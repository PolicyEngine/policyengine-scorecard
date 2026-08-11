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
    assert summary["attached"] == 108
    assert summary["families"] == {
        "cbo_free_joins": 9,
        "cpsp_ctc_2024": 8,
        "jct_obbba_provision4": 1,
        "pwbm_ss_elimination": 2,
        "tpc_t25_0209_t26_0029": 10,
        "urban_subgroup_counts": 78,
    }
    assert summary["exhibits"] == 4
    assert summary["exhibits_deferred"] == []

    conn = sqlite3.connect(db_copy)
    conn.row_factory = sqlite3.Row
    # The claim_id-direct rows attach to urban_sotsn claims only, with
    # exact program x status allocation per the strictness convention
    # (structural denominator gaps on tanf/ssi/housing are
    # concept_mismatch; WIC carries only its u5-subset age bands until
    # pass-2 v3's u5 restriction re-emits the other axes).
    urb = conn.execute(
        """SELECT s.program, r.status, COUNT(*) AS n,
                  SUM(s.source = 'urban_sotsn') AS urban
           FROM pe_results r JOIN external_scores s USING (claim_id)
           WHERE r.run_id = 'campaign-20260802-subgroups'
           GROUP BY 1, 2 ORDER BY 1"""
    ).fetchall()
    assert {(r["program"], r["status"]): r["n"] for r in urb} == {
        ("housing", "concept_mismatch"): 21,
        ("snap", "constructed"): 20,
        ("ssi", "concept_mismatch"): 11,
        ("tanf", "concept_mismatch"): 20,
        ("wic", "constructed"): 6,
    }
    assert all(r["urban"] == r["n"] for r in urb)
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
    # The four TPC marginal-increment exhibits — the top-tail/cap-binding
    # localization evidence — land in pe_exhibits with their pair context
    # and the TPC twin in the note.
    ex = conn.execute(
        "SELECT reform_key, value, conditions, note FROM pe_exhibits"
        " WHERE exhibit = 'campaign:tpc_t25_0209_t26_0029'"
        " ORDER BY reform_key"
    ).fetchall()
    assert [r["reform_key"] for r in ex] == [
        "tpc_t25_0209_ctc_opt2_minus_opt1",
        "tpc_t25_0209_ctc_opt3_minus_opt2",
        "tpc_t25_0209_toprate_opt2_minus_opt1",
        "tpc_t25_0209_toprate_opt3_minus_opt2",
    ]
    top21 = next(
        r for r in ex if r["reform_key"] == "tpc_t25_0209_toprate_opt2_minus_opt1"
    )
    assert top21["value"] == pytest.approx(1.67e9)
    assert json.loads(top21["conditions"])["pair"] == "opt2-opt1 toprate"
    assert "diagnosis carrier" in top21["note"]
    conn.close()


def test_reingest_idempotent(db_copy):
    first = ingest(db_copy)
    again = ingest(db_copy)
    assert again == first
    conn = sqlite3.connect(db_copy)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id LIKE 'campaign-%'"
    ).fetchone()[0]
    n_ex = conn.execute(
        "SELECT COUNT(*) FROM pe_exhibits WHERE run_id LIKE 'campaign-%'"
    ).fetchone()[0]
    conn.close()
    assert n == first["attached"]
    assert n_ex == first["exhibits"]


def test_metaless_exhibit_defers(db_copy, tmp_path):
    # A row marked exhibit without exhibit_meta is deferred and listed,
    # never guessed into pe_exhibits.
    staged = tmp_path / "staged"
    staged.mkdir()
    for p in STAGED_US.glob("*.jsonl"):
        (staged / p.name).write_text(p.read_text())
    tpc = staged / "tpc_t25_0209_t26_0029.jsonl"
    rows = [json.loads(line) for line in tpc.read_text().splitlines()]
    stripped = next(r for r in rows if r.get("exhibit"))
    del stripped["exhibit_meta"]
    tpc.write_text("\n".join(json.dumps(r) for r in rows))

    summary = ingest(db_copy, staged_dir=staged)
    assert summary["exhibits"] == 3
    assert len(summary["exhibits_deferred"]) == 1
    assert "marginal increment" in summary["exhibits_deferred"][0]
    conn = sqlite3.connect(db_copy)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_exhibits WHERE run_id LIKE 'campaign-%'"
    ).fetchone()[0]
    conn.close()
    assert n == 3  # the stripped row's prior exhibit did not linger


def test_exhibit_only_run_replaced_on_meta_loss(db_copy, tmp_path):
    # A run_id carrying ONLY exhibits must still be a deletion key: if its
    # row later loses exhibit_meta (deferred), the stale pe_exhibits row
    # goes away rather than surviving an empty write set.
    staged = tmp_path / "staged"
    staged.mkdir()
    src = next(
        json.loads(line)
        for line in (STAGED_US / "tpc_t25_0209_t26_0029.jsonl").read_text().splitlines()
        if json.loads(line).get("exhibit")
    )
    src["run_id"] = "campaign-test-solo-exhibit"
    solo = staged / "solo_exhibit.jsonl"
    solo.write_text(json.dumps(src))

    def count():
        conn = sqlite3.connect(db_copy)
        n = conn.execute(
            "SELECT COUNT(*) FROM pe_exhibits"
            " WHERE run_id = 'campaign-test-solo-exhibit'"
        ).fetchone()[0]
        conn.close()
        return n

    first = ingest(db_copy, staged_dir=staged)
    assert first["exhibits"] == 1 and count() == 1

    del src["exhibit_meta"]
    solo.write_text(json.dumps(src))
    second = ingest(db_copy, staged_dir=staged)
    assert second["exhibits"] == 0
    assert len(second["exhibits_deferred"]) == 1
    assert count() == 0


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


def test_unknown_claim_id_aborts(db_copy, tmp_path):
    staged = tmp_path / "staged"
    staged.mkdir()
    src = json.loads(
        (STAGED_US / "urban_subgroup_counts.jsonl").read_text().splitlines()[0]
    )
    src["external_claim_match"] = {"claim_id": "deadbeef00000000dead"}
    (staged / "urban_subgroup_counts.jsonl").write_text(json.dumps(src))
    with pytest.raises(ValueError, match="not in the DB"):
        ingest(db_copy, staged_dir=staged)


# Exhaustive-partition axes in the Urban subgroup vocabulary: every
# staged subgroup batch must have equal PE totals across whichever of
# these it fully covers. This is the invariant the WIC wrong-universe
# rows violated — an ALL-AGES race partition summing 35% above the u5
# AGE partition — so the age partitions themselves are axes here (the
# coarse pair for the all-age programs, the u5 pair for WIC): a
# demographic axis computed on the wrong universe disagrees with the
# age axis and fails.
PARTITION_AXES = {
    "race": {
        "race_white",
        "race_black",
        "race_hispanic",
        "race_aapi",
        "race_multi_other",
    },
    "disability": {"disability_yes", "disability_no"},
    "earners": {"fam_earners_yes", "fam_earners_no"},
    "citizenship": {"status_citizen", "status_noncitizen"},
    "age_coarse": {"age_0thr17", "age_18plus"},
    "age_u5": {"age_0thr3", "age_4"},
}


def _assert_partitions_agree(db_path, run_id="campaign-20260802-subgroups"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT s.program, s.metric,
                  json_extract(s.conditions, '$.subgroup') AS subgroup,
                  r.computed_value AS v
           FROM pe_results r JOIN external_scores s USING (claim_id)
           WHERE r.run_id = ?""",
        (run_id,),
    ).fetchall()
    conn.close()
    by_pm: dict[tuple, dict] = {}
    for r in rows:
        by_pm.setdefault((r["program"], r["metric"]), {})[r["subgroup"]] = r["v"]
    checked = 0
    for (program, metric), subs in by_pm.items():
        sums = {
            axis: sum(subs[s] for s in slugs)
            for axis, slugs in PARTITION_AXES.items()
            if slugs <= set(subs)
        }
        if len(sums) < 2:
            continue
        checked += 1
        lo, hi = min(sums.values()), max(sums.values())
        assert hi - lo <= 0.005 * hi, (
            f"{program}/{metric}: partition sums disagree {sums}"
        )
    return checked


def test_subgroup_partitions_agree(db_copy):
    ingest(db_copy)
    # Several programs carry race + age_coarse (+ disability/earners/
    # citizenship on snap); WIC's u5 age pair arms once its other axes
    # return with v3.
    assert _assert_partitions_agree(db_copy) >= 4


def test_partition_check_catches_wrong_universe(db_copy, tmp_path):
    # Reinjecting all-ages WIC race rows (the original defect: values
    # summing to the 12.66M all-age total against u5 claims) must fail
    # the invariant against the u5 age partition.
    conn = sqlite3.connect(db_copy)
    race_ids = [
        r[0]
        for r in conn.execute(
            """SELECT claim_id FROM external_scores
               WHERE source = 'urban_sotsn' AND program = 'wic'
               AND metric = 'eligible_count'
               AND json_extract(conditions, '$.subgroup') LIKE 'race_%'
               AND json_extract(conditions, '$.geography') = 'US'"""
        )
    ]
    conn.close()
    assert len(race_ids) == 5
    staged = tmp_path / "staged"
    staged.mkdir()
    lines = (STAGED_US / "urban_subgroup_counts.jsonl").read_text().splitlines()
    template = json.loads(lines[0])
    bad_rows = []
    for cid, share in zip(race_ids, (0.4, 0.25, 0.2, 0.1, 0.05)):
        row = dict(template)
        row["external_claim_match"] = {"claim_id": cid}
        row["pe_value"] = 12_655_357.569 * share  # the all-age total
        bad_rows.append(json.dumps(row))
    (staged / "urban_subgroup_counts.jsonl").write_text("\n".join(lines + bad_rows))
    ingest(db_copy, staged_dir=staged)
    with pytest.raises(AssertionError, match="partition sums disagree"):
        _assert_partitions_agree(db_copy)


def test_mixed_match_form_rejected(db_copy, tmp_path):
    # claim_id plus descriptor fields could contradict silently — refused.
    staged = tmp_path / "staged"
    staged.mkdir()
    src = json.loads(
        (STAGED_US / "urban_subgroup_counts.jsonl").read_text().splitlines()[0]
    )
    src["external_claim_match"]["metric"] = "eligible_count"
    (staged / "urban_subgroup_counts.jsonl").write_text(json.dumps(src))
    with pytest.raises(ValueError, match="must be exactly"):
        ingest(db_copy, staged_dir=staged)


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
