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
    assert MANIFEST["certified_dataset_sha256"] == CERTIFIED["sha256"]
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
            == MANIFEST["certified_dataset_sha256"]
        ), rel


# --- the staging --------------------------------------------------------------


UNANSWERED = [json.loads(line) for line in stg.UNANSWERED.read_text().splitlines()]


def test_staging_reproduces_the_committed_counterparts_byte_for_byte():
    rows, tally, unanswered = stg.stage(DB)
    assert rows == STAGED
    assert tally == TALLY
    assert unanswered == UNANSWERED


def test_every_unanswered_claim_has_one_receipt_and_the_tally_adds_up():
    """The receipts are the tally: one line per claim not answered, whose
    reasons sum to the tally's counts, per measure and overall; an attached
    claim has no receipt; the inert measures are the ones identical in every
    year of the run, and a pre-commencement zero is attached, annotated."""
    attached = {r["external_claim_match"]["claim_id"] for r in STAGED}
    ids = [u["claim_id"] for u in UNANSWERED]
    assert len(ids) == len(set(ids)) and not attached & set(ids)
    from collections import Counter

    by_reason = Counter(u["reason"] for u in UNANSWERED)
    assert by_reason[stg.INERT] == TALLY["unmapped"][stg.INERT]
    assert (
        sum(by_reason.values())
        == sum(TALLY["unmapped"].values()) + TALLY["owned_elsewhere"]
    )
    for key, bm in TALLY["by_measure"].items():
        assert sum(bm["reasons"].values()) == bm["claims"] - bm["attached"], key
    arts = _artifacts()
    commences = {
        k: m["commences_fy"] for k, m in INDEX.items() if m.get("commences_fy")
    }
    assert set(TALLY["inert_measures"]) == stg.inert_measures(
        arts, MANIFEST["years"], commences
    )
    for key in TALLY["inert_measures"]:
        assert all(stg.identical_worlds(a) for (k, _), a in arts.items() if k == key)
    zeros = [
        r for r in STAGED if any("not yet in force" in n for n in r["annotations"])
    ]
    assert zeros and all(r["measure_key"] not in TALLY["inert_measures"] for r in zeros)


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
    """Per lane: the claims answered by this run, counted from the database
    through the lane's own families, equal the figure the lane's feed note
    prints, and the lane reads computed."""
    import re

    from scorecard_db.ingest_uk_ab2025 import FAMILIES, LANES

    conn = sqlite3.connect(DB)
    n = conn.execute(
        "SELECT COUNT(*) FROM pe_results WHERE run_id = ?", (MANIFEST["run_id"],)
    ).fetchone()[0]
    assert n == len(STAGED) == TALLY["attached"]
    feed = {
        lane["id"]: lane
        for lane in json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    }
    checked = 0
    for lane in LANES:
        fams = [f for f, (l, _) in FAMILIES.items() if l == lane]
        marks = ",".join("?" * len(fams))
        answered = conn.execute(
            "SELECT COUNT(DISTINCT s.claim_id) FROM external_scores s"
            " JOIN pe_results r ON r.claim_id = s.claim_id AND r.run_id = ?"
            " WHERE json_extract(s.publication, '$.registry') = 'uk_ab2025'"
            f" AND json_extract(s.publication, '$.family') IN ({marks})",
            (MANIFEST["run_id"], *fams),
        ).fetchone()[0]
        note = feed[lane]["note"]
        m = re.search(r"(\d+) claims with a PolicyEngine counterpart", note)
        if answered == 0:
            assert m is None and feed[lane]["stage"] != "computed", lane
            continue
        assert m and int(m.group(1)) == answered, (lane, note, answered)
        assert feed[lane]["stage"] == "computed", lane
        checked += 1
    conn.close()
    assert checked >= 2


def test_a_zero_is_attached_only_before_a_recorded_commencement():
    """Every attached counterpart whose worlds are identical sits in a fiscal
    year before its measure's recorded commencement, and — the converse, a
    fact of a static model — every year before a recorded commencement has
    identical worlds (a difference there is a construction error, as the
    engine's April 2027 class 4 uprating was before the pre-Budget world
    pinned it)."""
    arts = _artifacts()
    alias = {
        k: str(m["construction"]).removeprefix("same_lever_as_")
        for k, m in INDEX.items()
        if str(m.get("construction", "")).startswith("same_lever_as_")
    }
    conn = sqlite3.connect(DB)
    fys = dict(
        conn.execute(
            "SELECT claim_id, json_extract(conditions, '$.fy') FROM external_scores"
            " WHERE json_extract(conditions, '$.measure_key') LIKE 'ab2025%'"
        ).fetchall()
    )
    conn.close()
    zeros = 0
    for r in STAGED:
        target = alias.get(r["measure_key"], r["measure_key"])
        fy = fys[r["external_claim_match"]["claim_id"]]
        assert fy not in INDEX[target].get("non_comparable_fys", {}), (
            r["measure_key"],
            fy,
        )
        if stg.identical_worlds(arts[(target, int(fy[:4]))]):
            c = INDEX[target].get("commences_fy")
            assert c and fy < c, (r["measure_key"], fy, c)
            assert any("not yet in force" in n for n in r["annotations"])
            zeros += 1
    assert zeros > 0
    for key, m in INDEX.items():
        c = m.get("commences_fy")
        if not c or (key, MANIFEST["years"][0]) not in arts:
            continue
        for y in MANIFEST["years"]:
            if f"{y}-{(y + 1) % 100:02d}" < c:
                assert stg.identical_worlds(arts[(key, y)]), (key, y)
