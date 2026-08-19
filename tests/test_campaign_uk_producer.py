"""Tests for the UK campaign staging producer (archive -> resolved)."""

import json
import shutil

import pytest

from scorecard_db import ScorecardDB
from scorecard_db.produce_campaign_uk import ARCHIVE, RUNS, produce

DB = ARCHIVE.parent.parent.parent / "data" / "scorecard.db"

pytestmark = pytest.mark.skipif(
    not (ARCHIVE.exists() and DB.exists()),
    reason="campaign archive or committed DB not present",
)


def test_produce_resolves_reckoner_and_blocks_the_rest(tmp_path):
    summary = produce(DB, out_dir=tmp_path)
    assert summary["resolved"] == {"hmrc_reckoner_t2": 14}
    assert set(summary["blocked"]) == {
        "free_joins",
        "obr_measures",
        "two_child",
        "uprating_april2026",
    }
    # only the resolved family lands in the staging dir
    assert [p.name for p in sorted(tmp_path.glob("*.jsonl"))] == [
        "hmrc_reckoner_t2.jsonl"
    ]

    rows = [
        json.loads(line)
        for line in (tmp_path / "hmrc_reckoner_t2.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 14
    db = ScorecardDB(DB)
    cids = set()
    for r in rows:
        match = r["external_claim_match"]
        # the strict claim_id-direct form, nothing else
        assert set(match) == {"claim_id"}
        cids.add(match["claim_id"])
        hit = db.conn.execute(
            "SELECT source, metric FROM external_scores WHERE claim_id = ?",
            (match["claim_id"],),
        ).fetchone()
        assert hit is not None
        assert (hit["source"], hit["metric"]) == ("uk_hmrc", "revenue_change")
        # everything else preserved verbatim from the archive
        assert r["run_id"] == "campaign-20260802-reckoner-t2"
        assert r["status"] == "constructed"
    db.close()
    assert len(cids) == 14  # no two rows share a claim

    # the archive itself is untouched (frozen by #70) — descriptors there
    # still carry the under-specified conditions form
    archived = [
        json.loads(line)
        for line in (ARCHIVE / "hmrc_reckoner_t2.jsonl").read_text().splitlines()
    ]
    assert all("claim_id" not in a["external_claim_match"] for a in archived)


def _composition(name):
    rows = [
        json.loads(line)
        for line in (ARCHIVE / f"{name}.jsonl").read_text().splitlines()
        if line.strip()
    ]
    tally: dict[str, int] = {}
    for r in rows:
        if r.get("exhibit") and "external_claim_match" not in r:
            key = "metaless_exhibit"
        else:
            m = r["external_claim_match"]
            key = f"{m['source']}:{m['metric']}"
        tally[key] = tally.get(key, 0) + 1
    return tally


def test_blocked_dispositions_match_the_archive_exactly():
    """The stated reasons are per-row accurate (round-1 gate: the first
    reasons generalized each family from its first row — free_joins is
    NOT just OBR receipts). A re-frozen archive that changes any
    family's composition fails here and forces a new disposition."""
    assert _composition("free_joins") == {
        "obr:revenue_level": 7,
        "uk_dwp:benefit_cost": 7,
        "metaless_exhibit": 2,
    }
    assert _composition("obr_measures") == {
        "obr:revenue_change": 9,
        "metaless_exhibit": 1,
    }
    assert _composition("two_child") == {
        "resolution_foundation:poverty_count_change": 1,
        "resolution_foundation:reform_fiscal_cost": 1,
        "ukmod:poverty_count_change": 1,
        "metaless_exhibit": 1,
    }
    assert _composition("uprating_april2026") == {
        "resolution_foundation:benefit_uprating_pct": 3,
        "metaless_exhibit": 1,
    }


def test_blocked_targets_have_no_claims_yet():
    """'Genuinely blocked' is machine-checked: zero DB claims exist for
    every blocked target shape. When a future lane stages one of these
    (OBR receipts, DWP expenditure forecasts, the OBR costings DB, RF,
    a UKMOD 2CL-reform claim), this fails and forces the deliberate
    unblock instead of a silent one."""
    db = ScorecardDB(DB)

    def n(sql, *args):
        return db.conn.execute(sql, args).fetchone()[0]

    assert (
        n(
            "SELECT COUNT(*) FROM external_scores WHERE source='obr'"
            " AND metric IN ('revenue_level', 'revenue_change')"
        )
        == 0
    )
    for source in ("uk_dwp", "resolution_foundation"):
        assert n("SELECT COUNT(*) FROM external_scores WHERE source=?", source) == 0
    assert (
        n(
            "SELECT COUNT(*) FROM external_scores WHERE source='ukmod'"
            " AND metric='poverty_count_change'"
        )
        == 0
    )
    db.close()


def test_resolution_chain_is_closed(tmp_path, monkeypatch):
    """A construction the archived runs never executed must fail the
    produce, never guess a claim."""
    import scorecard_db.produce_campaign_uk as mod

    bad_dir = tmp_path / "uk"
    bad_dir.mkdir()
    for p in ARCHIVE.glob("*.jsonl"):
        shutil.copy(p, bad_dir / p.name)
    target = bad_dir / "hmrc_reckoner_t2.jsonl"
    rows = [json.loads(line) for line in target.read_text().splitlines()]
    rows[0]["pe_construction"] = "gov.made.up.parameter: 1 -> 2 | heads income_tax"
    target.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    monkeypatch.setattr(mod, "ARCHIVE", bad_dir)
    with pytest.raises(ValueError, match="matches no"):
        produce(DB, out_dir=tmp_path / "out")


def test_new_archive_family_needs_a_disposition(tmp_path, monkeypatch):
    """Every archived family must be resolved, copied, or blocked-with-
    reason — a new family cannot be silently skipped."""
    import scorecard_db.produce_campaign_uk as mod

    new_dir = tmp_path / "uk"
    new_dir.mkdir()
    for p in ARCHIVE.glob("*.jsonl"):
        shutil.copy(p, new_dir / p.name)
    (new_dir / "brand_new_family.jsonl").write_text("{}\n")
    monkeypatch.setattr(mod, "ARCHIVE", new_dir)
    with pytest.raises(ValueError, match="without a disposition"):
        produce(DB, out_dir=tmp_path / "out")


def test_attach_round_trip(tmp_path):
    """Resolved staging attaches through ingest_campaign's strict
    claim_id-direct form: 14 results land and re-ingest is idempotent."""
    from scorecard_db.ingest_campaign import ingest

    db_copy = tmp_path / "scorecard.db"
    shutil.copy(DB, db_copy)
    staged = tmp_path / "uk_resolved"
    produce(db_copy, out_dir=staged)

    summary = ingest(db_copy, staged_dir=staged)
    assert summary["attached"] == 14
    assert summary["exhibits"] == 0
    assert summary["exhibits_deferred"] == []

    again = ingest(db_copy, staged_dir=staged)
    assert again["attached"] == 14

    db = ScorecardDB(db_copy)
    n = db.conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id = ?",
        ("campaign-20260802-reckoner-t2",),
    ).fetchone()[0]
    assert n == 14
    # every attached result rides a claim in the reckoner family and the
    # result side executed a current-law PE baseline (stamped by the
    # campaign ingest), distinct from the claim's indexed HMRC baseline —
    # the cross-world guard is what keeps these 'constructed'
    cross = db.conn.execute(
        "SELECT COUNT(*) FROM pe_results r JOIN external_scores s USING"
        " (claim_id) WHERE r.run_id = 'campaign-20260802-reckoner-t2'"
        " AND s.baseline_key = r.baseline_key"
    ).fetchone()[0]
    assert cross == 0
    db.close()


def test_collation_hints_match_db_options_exactly():
    """The resolution key: HMRC's verbatim change label in the t2
    collation equals the ingested claim's option string, character for
    character, for every resolved row."""
    import csv

    with open(RUNS / "t2_collation.csv") as f:
        hints = {r["key"]: r["hmrc_hint"] for r in csv.DictReader(f)}
    db = ScorecardDB(DB)
    options = {
        r[0]
        for r in db.conn.execute(
            "SELECT DISTINCT json_extract(conditions, '$.option')"
            " FROM external_scores WHERE source='uk_hmrc'"
            " AND metric='revenue_change'"
        )
    }
    db.close()
    missing = {k: h for k, h in hints.items() if h not in options}
    assert not missing, missing
