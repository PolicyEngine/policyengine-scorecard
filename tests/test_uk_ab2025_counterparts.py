"""The tranche-3 PolicyEngine counterparts for Autumn Budget 2025 claims
(#136), as facts of the committed artifacts and the built database.

The run is the certified bundle at the pinned engine, every artifact says so
and hashes to what the manifest recorded; the staged counterparts are
re-derivable from the artifacts and the database byte for byte; the executed
worlds are registered; and no claim carries two computed answers — the
OBR costings lane owns the claims that carry ``obr_measure_key`` and this
lane never touches them.
"""

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from pipeline import compute_uk_ab2025 as comp
from pipeline import stage_uk_ab2025 as stg
from scorecard_db.baselines import BASELINES
from scorecard_db.models import baseline_key

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "scorecard.db"
ARTIFACTS = ROOT / "results" / "uk" / "ab2025"
MANIFEST = json.loads((ARTIFACTS / "RUN_MANIFEST.json").read_text())
CERTIFIED = json.loads((ROOT / "data" / "uk" / "certified_bundle.json").read_text())
INDEX = comp.load_registry()
REGISTERED = {baseline_key(b[0]): b[1] for b in BASELINES}
STAGED = [json.loads(line) for line in stg.STAGED.read_text().splitlines()]
TALLY = json.loads(stg.TALLY.read_text())

pytestmark = pytest.mark.skipif(not DB.exists(), reason="built database absent")


def _artifacts() -> dict[tuple[str, int], dict]:
    return stg.load_artifacts()


# --- the run ------------------------------------------------------------------


def test_the_run_is_the_certified_bundle_at_the_pinned_engine():
    pin = next(
        s["specifier"]
        for s in CERTIFIED["compatible_model_packages"]
        if s["name"] == "policyengine-uk"
    ).lstrip("=")
    assert MANIFEST["engine_version"] == pin
    assert MANIFEST["data_bundle"] == CERTIFIED["revision"]
    assert MANIFEST["artifact_sha256"] == CERTIFIED["sha256"]
    assert MANIFEST["years"] == [2026, 2027, 2028, 2029, 2030]


def test_every_computable_measure_has_an_artifact_per_year_and_nothing_else():
    computable = {k for k, w in comp.computable(INDEX).items() if "alias_of" not in w}
    assert set(MANIFEST["measures"]) == computable
    assert MANIFEST["not_computable"] == comp.not_computable(INDEX)
    assert MANIFEST["aliases"] == {
        k: w["alias_of"] for k, w in comp.computable(INDEX).items() if "alias_of" in w
    }
    on_disk = _artifacts()
    assert set(on_disk) == {(k, y) for k in computable for y in MANIFEST["years"]}
    assert len(MANIFEST["artifacts"]) == len(on_disk)


def test_every_artifact_hashes_to_the_manifest_and_names_the_same_run():
    for rel, digest in MANIFEST["artifacts"].items():
        path = ROOT / rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, rel
        a = json.loads(path.read_text())
        assert a["run_id"] == MANIFEST["run_id"]
        assert a["engine_version"] == MANIFEST["engine_version"]
        assert a["data_bundle"] == MANIFEST["data_bundle"]
        assert (
            a["dataset_sha256_before"]
            == a["dataset_sha256_after"]
            == MANIFEST["artifact_sha256"]
        ), rel


# --- the staging --------------------------------------------------------------


def test_staging_reproduces_the_committed_counterparts_byte_for_byte():
    rows, tally = stg.stage(DB)
    assert rows == STAGED
    assert tally == TALLY


def test_every_counterpart_names_a_registered_executed_world_and_its_claim():
    arts = _artifacts()
    conn = sqlite3.connect(DB)
    alias = {
        k: str(m["construction"]).removeprefix("same_lever_as_")
        for k, m in INDEX.items()
        if str(m.get("construction", "")).startswith("same_lever_as_")
    }
    for r in STAGED:
        assert r["status"] == "constructed"
        assert r["run_id"] == MANIFEST["run_id"]
        assert r["baseline_key"] in REGISTERED, r["measure_key"]
        cid = r["external_claim_match"]["claim_id"]
        row = conn.execute(
            "SELECT conditions FROM external_scores WHERE claim_id = ?", (cid,)
        ).fetchone()
        assert row is not None, cid
        cond = json.loads(row[0])
        assert not cond.get("obr_measure_key"), "OBR costings lane claim attached"
        fy = int(cond["fy"][:4])
        target = alias.get(r["measure_key"], r["measure_key"])
        assert r["baseline_key"] == stg.executed_world_key(target, arts[(target, fy)])
    conn.close()


def test_no_claim_carries_two_computed_answers():
    """The #56 / #140 rule as a fact of the built database: a claim answered
    by this run has no other comparable or constructed result, and the OBR
    costings lane's claims (obr_measure_key) are never answered here."""
    conn = sqlite3.connect(DB)
    twice = conn.execute(
        "SELECT r1.claim_id, r2.run_id FROM pe_results r1"
        " JOIN pe_results r2 ON r2.claim_id = r1.claim_id AND r2.run_id != r1.run_id"
        " WHERE r1.run_id = ? AND r2.status IN ('comparable', 'constructed')",
        (MANIFEST["run_id"],),
    ).fetchall()
    assert twice == []
    obr = conn.execute(
        "SELECT COUNT(*) FROM pe_results r JOIN external_scores s ON s.claim_id = r.claim_id"
        " WHERE r.run_id = ? AND json_extract(s.conditions, '$.obr_measure_key') IS NOT NULL",
        (MANIFEST["run_id"],),
    ).fetchone()[0]
    assert obr == 0
    assert TALLY["owned_elsewhere"] > 0
    conn.close()


def test_the_attached_rows_are_in_the_database_and_the_lanes_read_computed():
    conn = sqlite3.connect(DB)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id = ?", (MANIFEST["run_id"],)
    ).fetchone()[0]
    assert n == len(STAGED) == TALLY["attached"]
    answered = {
        lane: conn.execute(
            "SELECT COUNT(DISTINCT s.claim_id) FROM external_scores s"
            " JOIN pe_results r ON r.claim_id = s.claim_id AND r.run_id = ?"
            " JOIN lanes l ON l.lane = ?"
            " WHERE json_extract(s.publication, '$.registry') = 'uk_ab2025'",
            (MANIFEST["run_id"], lane),
        ).fetchone()[0]
        for lane in ("uk-ab2025-official", "uk-ab2025-microsim")
    }
    conn.close()
    feed = {
        l["id"]: l
        for l in json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    }
    for lane, k in answered.items():
        assert k > 0
        assert feed[lane]["stage"] == "computed", lane
        assert "PolicyEngine counterpart" in feed[lane]["note"]
