"""PolicyEngine's counterparts for Autumn Budget 2026 claims (#230, tranche 3).

pipeline/stage_uk_ab2026.py pairs each AB2026 claim on a ``pe_modifier``
measure with one cell of the dashboard's Budget-day artifacts, or tallies a
written reason. These tests pin its invariants:

1. every vendored file's bytes hash to MANIFEST.json, each CSV to its
   receipt, and each receipt to the registry, at the pinned commit;
2. the 6.11.1 pair record states what every receipt states about the run;
3. every counterpart traces to one file, column and row, and re-deriving it
   from the CSV gives the same value byte for byte;
4. the accounting closes per measure and in total, against the pin;
5. a sign flip in a claim flips the sign relation and the counterpart's
   sign, and leaves its magnitude alone;
6. two runs give the same output, and so does any order of the claims;
7. no claim gets two computed answers;
8. a database built with the AB2026 ingest and these results shows each
   comparison, and build_db.py calls none of it.

Hypothesis drives 5 and 6.
"""

import copy
import csv
import hashlib
import io
import json
import random
import shutil
import sqlite3
from collections import Counter
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pipeline import stage_uk_ab2026 as S
from pipeline import uk_certified_pairs as pairs
from scorecard_db import ScorecardDB, ingest_campaign, signs
from scorecard_db import ingest_uk_ab2026 as I

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = S.load_manifest()
REGISTRY = S.registry()
MEASURES = S.modifier_measures(REGISTRY)
CLAIMS = S.claims()
ROWS, TALLY, UNANSWERED = S.stage(CLAIMS)
BY_ID = {c["claim_id"]: c for c in CLAIMS}
SETTINGS = settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- 1. the vendored artifacts --------------------------------------------------


def test_every_vendored_file_hashes_to_the_manifest():
    assert MANIFEST["artifacts"] == {
        p: f["sha256"] for p, f in MANIFEST["files"].items()
    }
    for path, sha in MANIFEST["artifacts"].items():
        assert _sha(ROOT / path) == sha, path
    on_disk = {
        str(p.relative_to(ROOT))
        for p in S.ARTIFACTS.rglob("*")
        if p.is_file() and p.parent != S.ARTIFACTS
    }
    assert on_disk == set(MANIFEST["artifacts"])


def test_every_receipt_hashes_to_the_registry_at_the_pinned_commit():
    assert set(MANIFEST["measures"]) == set(MEASURES)
    for key, m in MEASURES.items():
        rec = m["pe_modifier"]["receipt"]
        entry = MANIFEST["measures"][key]
        assert entry["receipt_file_sha256"] == rec["receipt_file_sha256"]
        assert _sha(ROOT / entry["receipt"]) == rec["receipt_file_sha256"]
        assert MANIFEST["files"][entry["receipt"]]["source_path"] == rec["path"]
        assert entry["receipt"] == S.local_path(rec["path"])
    commits = {f["source_commit"] for f in MANIFEST["files"].values()}
    assert commits == {MANIFEST["source"]["commit"]}
    assert commits == {m["pe_modifier"]["receipt"]["commit"] for m in MEASURES.values()}


def test_every_csv_hashes_to_its_receipt_and_is_used():
    used = {r["trace"]["file"] for r in ROWS}
    for key, entry in MANIFEST["measures"].items():
        rec = S.receipt(key)
        for path in entry["files"]:
            name = path.rsplit("/", 1)[1]
            if name == "receipt.json":
                continue
            assert MANIFEST["artifacts"][path] == rec["dashboard"]["files"][name]
            assert path in used, f"{path} is vendored but no counterpart reads it"


def test_a_changed_byte_is_refused(tmp_path, monkeypatch):
    path = next(p for p in MANIFEST["artifacts"] if p.endswith(".csv"))
    copy_root = tmp_path / "root"
    target = copy_root / path
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / path).read_bytes() + b"\n")
    monkeypatch.setattr(S, "ROOT", copy_root)
    with pytest.raises(ValueError, match="differ from MANIFEST"):
        S.read_file(path, MANIFEST)


# --- 2. the pair record --------------------------------------------------------


def test_the_pair_record_states_what_every_receipt_states():
    record = pairs.get_record(S.PAIR_ID)
    identity = record["identity"]
    bundle = identity["release_bundle"]
    pin = REGISTRY["engine_pin"]["budget_day_runs"]
    assert identity["packages"]["policyengine"]["version"] == pin["policyengine"]
    assert bundle["model_version"] == REGISTRY["engine_pin"]["policyengine_uk"]
    assert identity["dataset"]["revision"] == pin["dataset_revision"]
    assert identity["dataset"]["sha256"] == pin["dataset_sha256"]
    for key in MEASURES:
        r = S.receipt(key)
        ex = r["execution_receipt"]
        cert, data = ex["certificate"], ex["data"]
        assert ex["wrapper"]["version"] == bundle["policyengine_version"]
        assert cert["bundle_version"] == bundle["policyengine_version"]
        assert (
            ex["model"]["version"] == identity["packages"]["policyengine-uk"]["version"]
        )
        assert (
            ex["core"]["version"]
            == identity["packages"]["policyengine-core"]["version"]
        )
        assert (
            cert["certified_for_model_version"]
            == (record["certification"]["certified_for_model_version"])
        )
        assert cert["certified_for_core_version"] == ex["core"]["version"]
        assert cert["compatibility_basis"] == bundle["compatibility_basis"]
        assert cert["certified_by"] == bundle["certified_by"]
        assert cert["certified_dataset_sha256"] == identity["dataset"]["sha256"]
        assert data["dataset_sha256"] == bundle["certified_data_artifact_sha256"]
        assert data["build_id"] == record["certification"]["data_build_id"]
        assert data["dataset_uri"] == bundle["default_dataset_uri"]
        assert data["data_package"] == bundle["data_package"]
        assert data["dataset"] == bundle["default_dataset"]
        assert data["release_version"] == bundle["data_version"]
        assert data["build_model_version"] == bundle["data_build_model_version"]
        assert r["dashboard"]["dataset_years"] == record["data_years"]
        assert ex["supported_years"] == record["data_years"]
        assert ex["fiscal_year"]["year_label"] == "start_year"
        assert ex["baseline"]["kind"] == "current_law"


# --- 3. traces -----------------------------------------------------------------


def _rederive(row: dict) -> float:
    """The counterpart from the CSV alone, read without the stager."""
    trace = row["trace"]
    text = (ROOT / trace["file"]).read_text()
    hits = [
        r
        for r in csv.DictReader(io.StringIO(text))
        if all(r[k] == v for k, v in trace["where"].items())
    ]
    assert len(hits) == 1, trace
    raw = hits[0][trace["column"]]
    assert raw == trace["cell"]
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    if trace["column"] == "value":
        assert trace["file"].endswith("/budgetary_impact.csv")
        relation, _ = S.sign_relation(claim)
        return (1 if relation == signs.SAME else -1) * float(raw) * 1e9
    assert trace["column"] == "people_directly_affected"
    assert trace["where"]["age_band"] == "all"
    return float(raw)


def test_every_counterpart_traces_to_one_cell_and_rederives_exactly():
    assert ROWS
    for row in ROWS:
        claim = BY_ID[row["external_claim_match"]["claim_id"]]
        assert json.dumps(_rederive(row)) == json.dumps(row["pe_value"])
        folder = MANIFEST["measures"][claim["measure_key"]]["receipt"].rsplit("/", 1)[0]
        assert row["trace"]["file"].startswith(folder + "/")
        assert row["trace"]["where"]["year"] == claim["conditions"]["fy"][:4]
        assert row["engine_version"] == "2.151.0"
        assert row["data_bundle"] == MANIFEST["data_bundle"]
        assert row["baseline_key"] == S.CURRENT_LAW
        assert row["status"] == "constructed"


def test_the_committed_staging_is_this_run():
    assert S.STAGED.read_text() == S.dumps_jsonl(ROWS)
    assert S.UNANSWERED.read_text() == S.dumps_jsonl(UNANSWERED)
    assert json.loads(S.TALLY.read_text()) == TALLY


# --- 4. the accounting ---------------------------------------------------------


def test_the_accounting_closes_per_measure_and_in_total():
    S.check(TALLY)
    assert TALLY["claims"] == len(CLAIMS)
    for key, bm in TALLY["by_measure"].items():
        mine = [c for c in CLAIMS if c["measure_key"] == key]
        assert bm["claims"] == len(mine)
        assert bm["claims"] == bm["computed"] + sum(bm["reasons"].values())
    computed = {r["external_claim_match"]["claim_id"] for r in ROWS}
    tallied = {u["claim_id"] for u in UNANSWERED}
    assert not computed & tallied
    assert computed | tallied == set(BY_ID)
    assert Counter(u["reason"] for u in UNANSWERED) == Counter(TALLY["reasons"])


def test_every_reason_is_written_out():
    for reason in TALLY["reasons"]:
        assert len(S.REASONS[reason]) > 80, reason


def test_a_claim_no_rule_names_raises():
    claim = copy.deepcopy(CLAIMS[0])
    claim["metric"] = "gini_change"
    with pytest.raises(S.Unmatched):
        S.classify(claim)


def test_drifted_accounting_raises():
    tally = copy.deepcopy(TALLY)
    tally["computed"] -= 1
    tally["reasons"]["typical_bill"] = tally["reasons"].get("typical_bill", 0) + 1
    with pytest.raises(ValueError, match="drifted"):
        S.check(tally)


# --- 5. signs ------------------------------------------------------------------

EXCHEQUER = [r for r in ROWS if r["metric"] == "revenue_change"]
FLIPPED = {
    signs.SAME: "positive = cost to the Exchequer",
    signs.OPPOSITE: "positive = yield to the Exchequer",
}


@SETTINGS
@given(i=st.integers(min_value=0, max_value=len(EXCHEQUER) - 1))
def test_a_sign_flip_flips_the_relation_and_keeps_the_magnitude(i):
    row = EXCHEQUER[i]
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    relation, _ = S.sign_relation(claim)
    flipped = copy.deepcopy(claim)
    flipped["conditions"]["sign_convention"] = FLIPPED[relation]
    flipped["value"] = -claim["value"]
    other, _ = S.sign_relation(flipped)
    assert {relation, other} == {signs.SAME, signs.OPPOSITE}
    again = S.counterpart(flipped, "exchequer", MANIFEST)
    assert again["pe_value"] == -row["pe_value"]
    assert abs(again["pe_value"]) == abs(row["pe_value"])
    # the comparison's relation: the claim's value and the counterpart, both
    # in the claim's orientation, keep their ratio when both flip
    if row["pe_value"] and claim["value"]:
        assert again["pe_value"] / flipped["value"] == pytest.approx(
            row["pe_value"] / claim["value"]
        )


def test_an_exported_counterpart_reads_as_oriented_to_its_claim():
    for row in EXCHEQUER:
        claim = BY_ID[row["external_claim_match"]["claim_id"]]
        exported = {
            "metric": claim["metric"],
            "conditions": claim["conditions"],
            "country": "UK",
            "source": claim["source"],
            "latest": {"annotations": row["annotations"]},
        }
        assert signs.classify(exported) == (signs.SAME, "result_oriented_to_claim")


# --- 6. determinism ------------------------------------------------------------


def test_two_runs_give_the_same_output():
    assert S.stage(S.claims()) == (ROWS, TALLY, UNANSWERED)


@SETTINGS
@given(seed=st.integers(min_value=0, max_value=2**32 - 1))
def test_any_order_of_the_claims_gives_the_same_output(seed):
    shuffled = list(CLAIMS)
    random.Random(seed).shuffle(shuffled)
    rows, tally, unanswered = S.stage(shuffled, MANIFEST)
    assert S.dumps_jsonl(rows) == S.dumps_jsonl(ROWS)
    assert tally == TALLY
    assert unanswered == UNANSWERED


@SETTINGS
@given(data=st.data())
def test_any_sample_of_the_claims_closes_its_accounting(data):
    picks = data.draw(st.sets(st.sampled_from(sorted(BY_ID)), max_size=60))
    sample = [BY_ID[i] for i in sorted(picks)]
    rows, tally, unanswered = S.stage(sample, MANIFEST)
    assert tally["claims"] == len(sample)
    assert tally["claims"] == tally["computed"] + sum(tally["reasons"].values())
    want = {r["external_claim_match"]["claim_id"]: r for r in ROWS}
    for r in rows:
        assert r == want[r["external_claim_match"]["claim_id"]]


# --- 7. one answer per claim, and 8. the database ------------------------------


def test_no_claim_gets_two_computed_answers_in_the_staging():
    ids = [r["external_claim_match"]["claim_id"] for r in ROWS]
    assert len(ids) == len(set(ids))
    assert not any(c["conditions"].get("obr_measure_key") for c in CLAIMS)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("ab2026")
    db_path = tmp / "t.db"
    ScorecardDB(db_path).close()
    feed = tmp / "lanes.json"  # a copy: never the committed feed
    shutil.copy(ROOT / "data" / "lanes.json", feed)
    I.ingest(db_path, feed)
    I.ingest_verdicts(db_path)
    attached = ingest_campaign.ingest(db_path, I.STAGED_COUNTERPARTS)
    lanes = I.advance_lanes(db_path, feed)
    I.advance_lanes(db_path, feed)  # idempotent
    return db_path, feed, attached, lanes


def test_a_built_database_shows_each_comparison(built):
    db_path, _, attached, _ = built
    assert attached["attached"] == len(ROWS)
    conn = sqlite3.connect(db_path)
    got = {
        cid: (value, status, bk, run)
        for cid, value, status, bk, run in conn.execute(
            "SELECT claim_id, computed_value, status, baseline_key, run_id"
            " FROM pe_results WHERE run_id = ?",
            (S.RUN_ID,),
        )
    }
    assert got == {
        r["external_claim_match"]["claim_id"]: (
            r["pe_value"],
            "constructed",
            S.CURRENT_LAW,
            S.RUN_ID,
        )
        for r in ROWS
    }
    # each claim holds at most one counterpart, and none holds a pe_gap
    # verdict beside it
    many = conn.execute(
        "SELECT claim_id, COUNT(*) FROM pe_results GROUP BY claim_id"
        " HAVING COUNT(*) > 1"
    ).fetchall()
    assert many == []
    conn.close()


def test_advance_lanes_moves_only_the_lanes_with_counterparts(built):
    db_path, feed, _, lanes = built
    answered = Counter()
    families = {f: lane for f, (lane, _) in I.FAMILIES.items()}
    conn = sqlite3.connect(db_path)
    for row in ROWS:
        fam = conn.execute(
            "SELECT json_extract(publication, '$.family') FROM external_scores"
            " WHERE claim_id = ?",
            (row["external_claim_match"]["claim_id"],),
        ).fetchone()[0]
        answered[families[fam]] += 1
    stages = dict(
        conn.execute("SELECT lane, stage FROM lanes WHERE lane LIKE 'uk-ab2026-%'")
    )
    conn.close()
    for lane in I.LANES:
        assert lanes[lane]["answered"] == answered[lane]
        assert stages[lane] == ("computed" if answered[lane] else "ingested")
    fed = {lane["id"]: lane for lane in json.loads(feed.read_text())["lanes"]}
    assert {lane: fed[lane]["stage"] for lane in I.LANES} == stages


def test_build_db_calls_none_of_tranche_3():
    text = (ROOT / "scorecard_db" / "build_db.py").read_text()
    assert "ingest_uk_ab2026" not in text
    assert "stage_uk_ab2026" not in text
    assert "staged_ab2026" not in text
