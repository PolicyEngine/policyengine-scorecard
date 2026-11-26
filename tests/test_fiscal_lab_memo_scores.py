"""Fiscal Lab Memo Bill Scores: extract, statuses and ingest gates."""

from __future__ import annotations

import copy
import functools
import hashlib
import importlib.util
import json
import os
import sqlite3
import subprocess
from collections import Counter
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scorecard_db import (
    CalibrationRelationship,
    ComparisonStatus,
    Metric,
    PEResult,
    ScorecardDB,
    TimeBasis,
    UnitConcept,
    signs,
)
from scorecard_db import ingest_fiscal_lab as mod
from scorecard_db.harvest import REPO

ADAPTER_PATH = mod.SOURCE_DIR / "adapter.py"
RAW_DASHBOARD = mod.SOURCE_DIR / "raw" / "dashboard.html"
COMMITTED = {"adapter.py", "source.json", "pe_status.json", "NOTES.md"}
RANGE_ROUNDED = {
    "H_J_Res_189",
    "H_R_3521",
    "H_R_5343",
    "H_R_7920",
    "H_R_7961",
    "S_1096",
}
# The policyengine-us 2.2.2 source the statuses were judged against; set
# FISCAL_LAB_PE_SOURCE to check pe_paths locally (CI has no copy).
PE_SOURCE = os.environ.get("FISCAL_LAB_PE_SOURCE")


@functools.cache
def _adapter():
    spec = importlib.util.spec_from_file_location("fiscal_lab_adapter", ADAPTER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def payload():
    return mod.load_extract()


@pytest.fixture(scope="module")
def status(payload):
    return mod.load_pe_status({r["slug"] for r in payload["bills"]})


@pytest.fixture(scope="module")
def scores():
    return mod.stage_scores()


def test_pinned_hashes_and_census(payload, status):
    assert _sha256(mod.EXTRACT_PATH) == mod.EXTRACT_SHA256
    assert _sha256(mod.PE_STATUS_PATH) == mod.PE_STATUS_SHA256
    bills = payload["bills"]
    assert len(bills) == 110
    assert sum(r["low"] is not None for r in bills) == 69
    assert Counter(r["kind"] for r in bills) == {
        "bill": 102,
        "proposal": 7,
        "resolution": 1,
    }
    assert Counter(r["effect"] for r in bills) == {
        "adds to deficits": 57,
        "no significant effect": 42,
        "reduces deficits": 11,
    }
    assert set(status["bills"]) == {r["slug"] for r in bills}


def test_no_raw_fiscal_lab_file_is_tracked():
    """The terms allow links and short excerpts: the page, the CSV and the
    announcement are recorded by hash in source.json and never committed."""
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "--", str(mod.SOURCE_DIR)],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    names = {p.split("/", 2)[2] for p in tracked}
    assert names <= COMMITTED, sorted(names - COMMITTED)
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(RAW_DASHBOARD)], cwd=REPO, check=False
    ).returncode
    assert ignored == 0, "raw/ must stay git-ignored"
    source = mod.load_source()
    assert {r["id"] for r in source["raw"]} >= {
        "dashboard_20261125",
        "csv_20261125",
        "dashboard_20261121",
        "announcement",
        "terms",
    }
    assert all(r["stored_in_repo"] is False for r in source["raw"])


def test_extract_carries_only_identifiers_labels_values_and_links(payload):
    allowed = set(mod._ROW_FIELDS) | {"superseded", "range_rounded"}
    for row in payload["bills"]:
        assert set(row) <= allowed
        assert row["url"].startswith("https://fiscallab.org/")
        assert row["url"].endswith("#" + row["slug"])
    superseded = [r["slug"] for r in payload["bills"] if "superseded" in r]
    assert superseded == ["H_R_4849"]
    rounded = {r["slug"] for r in payload["bills"] if r.get("range_rounded")}
    assert rounded == RANGE_ROUNDED == _adapter().RANGE_ROUNDED
    figures = sum(
        1
        + 2 * (r["low"] is not None)
        + len(r.get("superseded", {}).keys() & {"central", "low", "high"})
        for r in payload["bills"]
    )
    assert figures == 251


def test_extract_is_tied_to_the_page_source_json_pins(payload, scores):
    page = {r["id"]: r for r in mod.load_source()["raw"]}[mod.SOURCE_PIN]
    assert payload["source_sha256"] == page["sha256"]
    assert payload["build"] == page["build"]
    assert {s.publication["source_sha256"] for s in scores} == {page["sha256"]}


def test_rounded_ranges_carry_a_note_on_their_low_and_high_claims(scores):
    for s in scores:
        slug = s.publication["url"].rsplit("#", 1)[1]
        noted = "range_note" in s.publication
        assert noted == (
            slug in RANGE_ROUNDED and s.conditions["scenario"] != "central"
        )
        assert s.publication.get("range_rounded", False) is noted
        # the app shows source_column; the claim id does not hash it
        assert ("rounded by Fiscal Lab" in s.source_column) is noted


def test_rebuild_from_the_fetched_page_matches_the_extract():
    if not RAW_DASHBOARD.exists():
        pytest.skip(
            "raw/dashboard.html is never committed, so CI never runs this "
            "rebuild; run `adapter.py fetch` to check it locally"
        )
    adapter = _adapter()
    assert (
        _sha256(RAW_DASHBOARD)
        == adapter.pin(adapter.load_source(), "dashboard_20261125")["sha256"]
    )
    rebuilt = adapter.render(adapter.build(RAW_DASHBOARD, None))
    assert rebuilt == mod.EXTRACT_PATH.read_text()


def test_claim_mapping(scores, payload):
    assert len(scores) == 248
    assert len({s.claim_id() for s in scores}) == 248
    assert Counter(s.conditions["scenario"] for s in scores) == {
        "central": 110,
        "low": 69,
        "high": 69,
    }
    by_url = {r["url"]: r for r in payload["bills"]}
    for s in scores:
        row = by_url[s.publication["url"]]
        scenario = s.conditions["scenario"]
        assert s.source == "fiscal_lab"
        assert s.metric is Metric.PRIMARY_DEFICIT_CHANGE
        assert s.unit_concept is UnitConcept.USD
        assert s.time_basis is TimeBasis.FISCAL_YEAR
        assert (s.period, s.period_start, s.period_end) == (2036, 2027, 2036)
        assert s.conditions["window_kind"] == "total"
        assert s.calibration_relationship is CalibrationRelationship.HELD_OUT
        assert s.reform.baseline is None
        assert s.value == float(Decimal(row[scenario]) * 10**9)
        assert s.publication["publish_without_result"] is True
        assert s.publication["registry"] == mod.REGISTRY_MARK
        assert s.reform.reform["policy"] == mod.policy_slug(row["slug"])


def test_sign_reads_as_policyengine_orientation(scores):
    for s in scores[:3]:
        relation, basis = signs.classify(
            {
                "metric": s.metric.value,
                "conditions": s.conditions,
                "latest": {"annotations": []},
                "country": "US",
                "source": s.source,
            }
        )
        assert (relation, basis) == (signs.SAME, "stated:borrowing:same")


def test_comparison_bills_stay_not_computed(status):
    for slug in mod.COMPARISON_BILLS:
        entry = status["bills"][slug]
        assert entry["status"] == "not_computed"
        assert mod.COMPARISON_REPO in entry["counterpart"]


def test_ingest_writes_claims_gap_rows_and_no_values(tmp_path, monkeypatch, status):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    summary = mod.ingest(path)
    gaps = {s for s, e in status["bills"].items() if e["status"] == "pe_gap"}
    db = ScorecardDB(path)
    try:
        assert db.unregistered_baselines() == []
        n = db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE source = 'fiscal_lab'"
        ).fetchone()[0]
        assert n == summary["claims"] == 248
        results = db.conn.execute(
            "SELECT status, computed_value, run_id, pe_construction FROM pe_results"
        ).fetchall()
        assert {r["status"] for r in results} <= {ComparisonStatus.PE_GAP.value}
        assert all(r["computed_value"] is None for r in results)
        assert {r["pe_construction"].rsplit(":", 1)[1] for r in results} == gaps
        assert db.conn.execute("SELECT COUNT(*) FROM diagnoses").fetchone()[0] == 0
        lane = db.conn.execute(
            "SELECT stage, detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
        ).fetchone()
        assert lane["stage"] == "ingested" == summary["lane_stage"]
        assert "none computed" in lane["detail"]
        assert summary["computed_claims"] == 0
        first = db.conn.execute(
            "SELECT claim_id, value, publication FROM external_scores ORDER BY 1"
        ).fetchall()
    finally:
        db.close()
    assert mod.ingest(path) == summary
    db = ScorecardDB(path)
    try:
        again = db.conn.execute(
            "SELECT claim_id, value, publication FROM external_scores ORDER BY 1"
        ).fetchall()
        assert [tuple(r) for r in again] == [tuple(r) for r in first]
        assert (
            db.conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0]
            == summary["pe_gap_results"]
        )
    finally:
        db.close()


def test_feed_shows_every_claim_before_any_result(tmp_path, monkeypatch):
    from scorecard_db.export_populations import export

    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    db_path = tmp_path / "scorecard.db"
    out = tmp_path / "populations.json"
    mod.ingest(db_path)
    stats = export(db_path, out_path=out, built="2026-11-26")
    feed = json.loads(out.read_text())
    assert stats["rows"] == 248
    assert feed["summary"]["by_source"] == {"fiscal_lab": 248}
    assert set(feed["summary"]["by_latest_status"]) <= {"not_computed", "pe_gap"}
    assert all(row["latest"]["value"] is None for row in feed["rows"])
    assert all(row["url"].startswith("https://fiscallab.org/") for row in feed["rows"])


# Mutation gates: a single changed cell must fail validation.


def _mutate(payload, fn):
    bad = copy.deepcopy(payload)
    fn(bad)
    with pytest.raises(ValueError):
        mod.validate_extract(bad, mod.load_source())


def _row(p, slug):
    return next(r for r in p["bills"] if r["slug"] == slug)


def test_validation_rejects_drift(payload):
    def flip_effect(p):
        row = next(r for r in p["bills"] if r["effect"] == "adds to deficits")
        row["effect"] = "reduces deficits"

    def unbracket(p):
        row = next(r for r in p["bills"] if r["low"] is not None)
        row["low"] = str(Decimal(row["central"]) + 1)

    def extra_field(p):
        p["bills"][0]["summary"] = "prose"

    def drop_bill(p):
        p["bills"].pop()

    def relink(p):
        p["bills"][0]["url"] = "https://example.org/"

    def blank_title(p):
        p["bills"][0]["title"] = " "

    def blank_model(p):
        p["bills"][0]["models"] = [""]

    def relabel(p):
        row = next(r for r in p["bills"] if r["bill"] is not None)
        row["bill"] = "H.R. 1"

    def supersede_another(p):
        other = next(r for r in p["bills"] if r["slug"] != "H_R_4849" and r["low"])
        other["superseded"] = copy.deepcopy(_row(p, "H_R_4849")["superseded"])

    def bad_superseded_value(p):
        _row(p, "H_R_4849")["superseded"]["central"] = "2008.1"

    def rebuild(p):
        p["build"] = "November 21, 2026"

    def repin(p):
        p["source_sha256"] = "0" * 64

    def reunit(p):
        p["unit"] = "millions of dollars"

    def drop_congress(p):
        row = next(r for r in p["bills"] if r["version"] == "introduced")
        row["congress"] = None
        row["bill_url"] = None

    def round_a_point(p):
        row = next(r for r in p["bills"] if r["low"] is None)
        row["range_rounded"] = True

    def rekind(p):
        _row(p, "H_R_4849")["kind"] = "resolution"

    for fn in (
        flip_effect,
        unbracket,
        extra_field,
        drop_bill,
        relink,
        blank_title,
        blank_model,
        relabel,
        supersede_another,
        bad_superseded_value,
        rebuild,
        repin,
        reunit,
        drop_congress,
        round_a_point,
        rekind,
    ):
        _mutate(payload, fn)


def test_status_validation_rejects_a_gap_without_a_reason(payload, status):
    slugs = {r["slug"] for r in payload["bills"]}
    bad = copy.deepcopy(status)
    gap = next(s for s, e in bad["bills"].items() if e["status"] == "pe_gap")
    bad["bills"][gap]["reason"] = " "
    with pytest.raises(ValueError):
        mod.validate_pe_status(bad, slugs)
    bad = copy.deepcopy(status)
    bad["bills"]["H_R_4849"]["status"] = "pe_gap"
    with pytest.raises(ValueError):
        mod.validate_pe_status(bad, slugs)
    bad = copy.deepcopy(status)
    bad["judged"] = "2026-11-25"
    with pytest.raises(ValueError):
        mod.validate_pe_status(bad, slugs)
    for quoted in (
        "costs $3 billion",
        "about 1.2B a year",
        "a 300 mn line",
        "4bn",
        "12B a year",
        "a 300M line",
        "4,000 dollars",
        "USD 4,000",
    ):
        bad = copy.deepcopy(status)
        bad["bills"][gap]["reason"] = f"PolicyEngine misses {quoted}."
        with pytest.raises(ValueError):
            mod.validate_pe_status(bad, slugs)


@pytest.mark.parametrize("name", ["340B", "H-1B", "Part B", "Title 42", "Sec. 71116"])
def test_program_names_are_not_read_as_dollar_figures(name):
    assert not mod._quotes_dollars(f"PolicyEngine has no {name} rule.")


def test_pe_paths_exist_in_the_judged_source(status):
    if not PE_SOURCE:
        pytest.skip(
            "set FISCAL_LAB_PE_SOURCE to the policyengine-us 2.2.2 source "
            "directory (the one holding policyengine_us/) to check pe_paths"
        )
    root = Path(PE_SOURCE)
    missing = sorted(
        (slug, path)
        for slug, entry in status["bills"].items()
        for path in entry["pe_paths"]
        if not (root / path).exists()
    )
    assert missing == []


# Refresh: a rerun prunes only stale claims, keeps other runs' attachments,
# leaves other registries alone and sets the lane the way the NZ ingest does.


def _result(score, *, run_id="counterpart-run", status=None, when="2026-12-01"):
    return PEResult(
        claim_id=score.claim_id(),
        computed_value=1.0 if status is None else None,
        status=status or ComparisonStatus.CONSTRUCTED,
        engine_version="test-engine",
        data_bundle="test-bundle",
        run_id=run_id,
        computed_at=when,
        baseline_key=score.reform.baseline_key(),
    )


def _count(db, table, claim_id):
    return db.conn.execute(
        f"SELECT COUNT(*) FROM {table} WHERE claim_id = ?", (claim_id,)
    ).fetchone()[0]


def _lane(db):
    return db.conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane = ?", (mod.LANE_ID,)
    ).fetchone()


def test_refresh_prunes_stale_claims_and_keeps_other_attachments(
    tmp_path, monkeypatch, scores
):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    kept = next(s for s in scores if s.publication["url"].endswith("#H_R_4849"))
    stale = replace(
        kept,
        conditions={**kept.conditions, "scenario": "stale_scenario"},
        publication={**kept.publication, "name": "stale"},
    )
    other = replace(
        kept,
        source="other_source",
        publication={"registry": "other_registry", "name": "unrelated"},
    )
    db = ScorecardDB(path)
    db.upsert_scores([stale, other])
    db.add_results([_result(kept), _result(stale), _result(other)])
    for score in (kept, stale, other):
        db.diagnose(score.claim_id(), "vintage", "test")
    db.close()

    summary = mod.ingest(path)
    assert summary["computed_claims"] == 1
    assert summary["lane_stage"] == "computed"
    db = ScorecardDB(path)
    try:
        for table in ("external_scores", "pe_results", "diagnoses"):
            assert _count(db, table, kept.claim_id()) == 1
            assert _count(db, table, stale.claim_id()) == 0
            assert _count(db, table, other.claim_id()) == 1
        lane = _lane(db)
        assert lane["stage"] == "computed"
        assert "1 of 248 claims computed" in lane["detail"]
    finally:
        db.close()


def test_a_status_flip_removes_that_bills_gap_rows(tmp_path, monkeypatch, status):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    gap = next(
        s
        for s, e in status["bills"].items()
        if e["status"] == "pe_gap" and e["pe_paths"]
    )
    flipped = copy.deepcopy(status)
    flipped["bills"][gap].update(status="not_computed", scope="partial")
    monkeypatch.setattr(mod, "load_pe_status", lambda slugs, **k: flipped)

    def gap_rows_for(db, slug):
        return db.conn.execute(
            "SELECT COUNT(*) FROM pe_results WHERE pe_construction LIKE ?",
            (f"%:{slug}",),
        ).fetchone()[0]

    db = ScorecardDB(path)
    before = gap_rows_for(db, gap)
    db.close()
    assert before >= 1
    summary = mod.ingest(path)
    db = ScorecardDB(path)
    try:
        assert gap_rows_for(db, gap) == 0
        total = db.conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0]
        assert total == summary["pe_gap_results"]
    finally:
        db.close()


def test_lane_keeps_later_stages_and_regresses_when_results_go(
    tmp_path, monkeypatch, scores
):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    score = next(s for s in scores if s.publication["url"].endswith("#H_R_1428"))
    db = ScorecardDB(path)
    db.add_results([_result(score, when="2026-12-01")])
    db.close()
    assert mod.ingest(path)["lane_stage"] == "computed"

    db = ScorecardDB(path)
    db.add_results(
        [
            _result(
                score,
                run_id="newer-run",
                status=ComparisonStatus.NOT_COMPUTED,
                when="2026-12-02",
            )
        ]
    )
    db.close()
    summary = mod.ingest(path)
    assert (summary["lane_stage"], summary["computed_claims"]) == ("regressed", 0)
    db = ScorecardDB(path)
    try:
        assert "0 of 248 claims retain results" in _lane(db)["detail"]
        db.conn.execute(
            "UPDATE lanes SET stage = 'published' WHERE lane = ?", (mod.LANE_ID,)
        )
        db.conn.commit()
    finally:
        db.close()
    assert mod.ingest(path)["lane_stage"] == "published"


@pytest.mark.parametrize("stage", ["diagnosing", "published", "regressed"])
def test_a_refresh_never_rolls_back_a_later_lane_stage(tmp_path, monkeypatch, stage):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    db = ScorecardDB(path)
    db.conn.execute("UPDATE lanes SET stage = ? WHERE lane = ?", (stage, mod.LANE_ID))
    db.conn.commit()
    db.close()
    assert mod.ingest(path)["lane_stage"] == stage


@pytest.mark.parametrize(
    "when, counted",
    [("2026-11-25", False), ("2026-11-26", False), ("2026-12-01", True)],
)
def test_lane_counts_a_counterpart_only_where_the_feed_shows_it(
    tmp_path, monkeypatch, scores, status, when, counted
):
    """On a pe_gap claim the feed shows the latest row by (computed_at, id).
    This module's own row is dated 2026-11-26T00:00 and re-inserted on each
    run, so an earlier or same-day counterpart sits behind it; the lane must
    not count what the feed does not show."""
    from scorecard_db.export_populations import export

    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    mod.ingest(path)
    slug = next(s for s, e in status["bills"].items() if e["status"] == "pe_gap")
    score = next(s for s in scores if s.publication["url"].endswith("#" + slug))
    db = ScorecardDB(path)
    db.add_results([_result(score, when=when)])
    db.close()
    summary = mod.ingest(path)
    assert summary["computed_claims"] == int(counted)
    out = tmp_path / "populations.json"
    export(path, out_path=out, built="2026-11-26")
    row = next(
        r
        for r in json.loads(out.read_text())["rows"]
        if r["claim_id"] == score.claim_id()
    )
    assert (row["latest"]["status"] != "pe_gap") is counted


def test_lane_mirror_failure_is_recoverable_by_idempotent_retry(tmp_path, monkeypatch):
    path = tmp_path / "scorecard.db"

    def fail_sync(*args, **kwargs):
        raise OSError("simulated lane mirror failure")

    monkeypatch.setattr(mod, "sync_lane_feed", fail_sync)
    with pytest.raises(OSError, match="lane mirror failure"):
        mod.ingest(path)
    db = ScorecardDB(path)
    try:
        n = db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE source = 'fiscal_lab'"
        ).fetchone()[0]
        assert n == 248
        assert _lane(db)["stage"] == "ingested"
    finally:
        db.close()
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    assert mod.ingest(path)["claims"] == 248


def test_write_failure_rolls_back_the_whole_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "sync_lane_feed", lambda *a, **k: 1)
    path = tmp_path / "scorecard.db"
    first_summary = mod.ingest(path)

    def snapshot():
        db = ScorecardDB(path)
        try:
            return [
                tuple(r)
                for r in db.conn.execute(
                    "SELECT claim_id, value, publication FROM external_scores "
                    "ORDER BY claim_id"
                )
            ] + [
                tuple(r)
                for r in db.conn.execute(
                    "SELECT claim_id, status, run_id FROM pe_results ORDER BY claim_id"
                )
            ]
        finally:
            db.close()

    first = snapshot()
    real = ScorecardDB.result_row
    calls = {"n": 0}

    def sabotaged(result):
        row = real(result)
        calls["n"] += 1
        if calls["n"] == 5:
            raise sqlite3.IntegrityError("simulated write failure")
        return row

    monkeypatch.setattr(ScorecardDB, "result_row", staticmethod(sabotaged))
    with pytest.raises(sqlite3.IntegrityError):
        mod.ingest(path)
    assert snapshot() == first
    monkeypatch.setattr(ScorecardDB, "result_row", staticmethod(real))
    assert mod.ingest(path) == first_summary


# The adapter on synthetic data: the CSV it rebuilds, the footer it reads
# from the page's code and each QC gate.


def _bill(**overrides):
    bill = {
        "slug": "H_R_1",
        "label": "H.R. 1",
        "title": "A test bill, with a comma",
        "sponsor": None,
        "section_no": "II",
        "section": "Test section",
        "timing": None,
        "is_concept": False,
        "glance": {
            "deficit": [1.0] * 10,
            "direct": [1.5] * 10,
            "revenue": [0.5] * 10,
            "notes": "",
        },
        "figure": 10.0,
        "low": 9.0,
        "high": 11.0,
        "has_range": True,
        "zero": False,
        "t2": {
            "rows": [
                {
                    "label": "line",
                    "low": 9.0,
                    "central": 10.0,
                    "high": 11.0,
                    "total": False,
                },
                {
                    "label": "Total",
                    "low": 9.0,
                    "central": 10.0,
                    "high": 11.0,
                    "total": True,
                },
            ]
        },
    }
    bill.update(overrides)
    return bill


def test_summary_csv_rebuilds_the_pages_layout():
    adapter = _adapter()
    concept = _bill(
        slug="Concept_X",
        label="Concept X",
        is_concept=True,
        section_no=None,
        figure=0.0,
        zero=True,
        has_range=False,
        low=None,
        high=None,
        glance={"deficit": [0.0] * 10, "direct": [0.0] * 10, "revenue": [0.0] * 10},
    )
    data = {"years": list(range(2027, 2037)), "bills": [concept, _bill()]}
    out = adapter.summary_csv(data, 'Footer, "quoted"')
    assert out.startswith("\ufeff".encode())
    lines = out.decode("utf-8")[1:].split("\r\n")
    assert lines[0].startswith("Bill,Title,Sponsor,Memo section,Memo timing,FY2027,")
    assert lines[0].endswith(",FY2036,FY2027-2036,Low,High,Effect")
    # memo order puts section II ahead of the unnumbered proposal
    assert lines[1] == (
        'H.R. 1,"A test bill, with a comma",,II. Test section,,'
        + ",".join(["1.000"] * 10)
        + ",10.000,9.000,11.000,adds to deficits"
    )
    assert lines[2].startswith("Proposal,")
    assert lines[2].endswith(",0.000,,,no significant effect")
    assert lines[3:] == ["", '"Footer, ""quoted"""', ""]


def test_csv_footer_is_read_from_the_pages_code():
    adapter = _adapter()
    html = (
        "function summaryCsv() {\n"
        '  lines.push("", q(`Estimates as of ${DATA.built}. `\n'
        "    + `Second part.`));\n"
        "}\n"
    )
    assert adapter.csv_footer(html, "May 1") == "Estimates as of May 1. Second part."
    for broken in (
        html.replace("${DATA.built}", "${DATA.other}"),
        html.replace("`Second part.`", "`Second ${DATA.built}`"),
        html.replace("+ `Second part.`", ", `Second part.`"),
    ):
        with pytest.raises(ValueError):
            adapter.csv_footer(broken, "May 1")


@pytest.mark.parametrize(
    "value, text",
    [
        (0.0625, "0.063"),
        (-0.0625, "-0.063"),
        (-0.0001, "-0.000"),
        (-0.0, "0.000"),
        (1.0005, "1.000"),
        (None, ""),
    ],
)
def test_to_fixed3_matches_javascript_on_ties_and_signs(value, text):
    assert _adapter().to_fixed3(value) == text


def test_qc_bill_rejects_each_broken_identity():
    adapter = _adapter()
    adapter.qc_bill(_bill())
    deficit = [1.0] * 9 + [2.0]
    broken = [
        _bill(figure=10.5),
        _bill(glance={**_bill()["glance"], "deficit": deficit}, figure=11.0, high=12.0),
        _bill(low=10.5),
        _bill(zero=True),
    ]
    for bill in broken:
        with pytest.raises(ValueError):
            adapter.qc_bill(bill)


def test_qc_range_table_flags_rounding_and_rejects_drift():
    adapter = _adapter()

    def with_total(low, central, high):
        rows = [
            {
                "label": "Total",
                "low": low,
                "central": central,
                "high": high,
                "total": True,
            }
        ]
        return {"rows": rows}

    assert adapter.qc_range_table(_bill()) is False
    assert adapter.qc_range_table(_bill(t2=with_total(9.04, 10.0, 10.96))) is True
    assert (
        adapter.qc_range_table(_bill(has_range=False, low=None, high=None, t2={}))
        is False
    )
    for t2 in (
        with_total(9.0, 10.1, 11.0),  # central disagrees
        with_total(9.06, 10.0, 11.0),  # more than a rounding away
        {},  # a range with no total row
        {
            "rows": [
                with_total(9.0, 10.0, 11.0)["rows"][0],
                {"label": "x", "total": False},
            ]
        },
    ):
        with pytest.raises(ValueError):
            adapter.qc_range_table(_bill(t2=t2))
    with pytest.raises(ValueError):
        adapter.qc_range_table(_bill(low=9.02, t2=with_total(9.04, 10.0, 11.0)))


def test_qc_superseded_and_release_check_the_changelog_and_the_old_page():
    adapter = _adapter()
    sup = adapter.SUPERSEDED["H_R_4849"]
    row = {
        "slug": "H_R_4849",
        "bill": "H.R. 4849",
        "central": "2100.000",
        "low": "1600.000",
        "high": "2300.000",
    }
    entry = {
        "id": sup["changelog_id"],
        "bill": "H.R. 4849",
        "before": {"central": 2008.1, "low": 1551.1, "high": 2225.4},
        "after": {"central": 2100.0, "low": 1600.0, "high": 2300.0},
    }
    adapter.qc_superseded({"changelog": [entry]}, [row])
    for bad in (
        {**entry, "after": {**entry["after"], "central": 2200.0}},
        {**entry, "before": {**entry["before"], "low": 1500.0}},
        {**entry, "bill": "H.R. 1"},
        {**entry, "after": {"central": 2100.0}},
    ):
        with pytest.raises(ValueError):
            adapter.qc_superseded({"changelog": [bad]}, [row])
    with pytest.raises(ValueError):
        adapter.qc_superseded({"changelog": []}, [row])

    old = {"slug": "H_R_4849", "figure": 2008.089, "low": 1551.1, "high": 2225.425}
    page = "const DATA = " + json.dumps({"bills": [old]}) + ";"
    adapter.qc_release(page)
    with pytest.raises(ValueError):
        adapter.qc_release(page.replace("2008.089", "2008.0"))


@settings(max_examples=300, deadline=None)
@given(
    st.decimals(
        min_value=Decimal(-100000),
        max_value=Decimal(100000),
        places=6,
        allow_nan=False,
        allow_infinity=False,
    )
)
def test_to_fixed3_matches_half_up_and_reparses(value):
    adapter = _adapter()
    text = adapter.to_fixed3(float(value))
    assert mod._VALUE.match(text)
    assert abs(Decimal(text) - Decimal(float(value))) <= Decimal("0.0005")
    if Decimal(text) != 0:
        assert mod._sign(text) == (1 if value > 0 else -1)


@given(
    st.sampled_from(["H_R_4849", "H_J_Res_189", "S_1105", "Concept_Medicare_for_Kids"])
)
def test_policy_slug_is_stable_and_namespaced(slug):
    out = mod.policy_slug(slug)
    assert out.startswith("federal.")
    assert out == out.lower()
    assert mod.policy_slug(slug) == out
