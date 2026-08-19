"""The re-homed backfill automation (calibration-diagnostics #112 -> here):
registering a harvested artifact into the source tree, and ingesting a
genuinely-new release whose engine pin is carried in the artifact rather than
hand-coded in ENGINE_VERSIONS."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from scorecard_db.ingest_reform_validation import (
    ENGINE_VERSIONS,
    RAW,
    RUN_PREFIX,
    _non_rv_fingerprint,
    ingest,
)

TOOLS = Path(__file__).resolve().parent.parent / "tools" / "reform_validation"
sys.path.insert(0, str(TOOLS))
import register_release  # noqa: E402

BUILDO = "populace-us-2024-buildo-sparse-rmloss100-22bd902-20260722T232627Z"
# A plausible next release: not in ENGINE_VERSIONS / OBBBA_SCORING_MODE, with a
# parseable trailing timestamp.
NEW_RELEASE = "populace-us-2024-buildp-sparse-rmloss100-deadbeef-20260801T000000Z"


def _new_release_artifact() -> dict:
    """The buildo artifact re-stamped as a brand-new release that carries its
    own engine pin (as the updated backfill.py now emits)."""
    artifact = json.loads((RAW / f"{BUILDO}.json").read_text())
    artifact["release_id"] = NEW_RELEASE
    artifact["engine"] = {
        "policyengine_us": "1.799.9",
        "policyengine_core": "3.0.0",
    }
    # backfill.py stamps the scoring mode explicitly; the ingest fails loudly
    # without it (no silent default).
    artifact["obbba_scoring_mode"] = "jcx_stacked"
    # The ingest consumes the attestation for a non-historical release and
    # rejects a missing/unknown one (blocker 6), so a valid block is required.
    artifact["_attestation"] = {
        "release_id": NEW_RELEASE,
        "producer_commit": "abc1234",
        "driver_commit": "def5678",
        "h5_sha256": "0" * 64,
        "policyengine_us": "1.799.9",
        "policyengine_core": "3.0.0",
    }
    return artifact


# --------------------------------------------------------------------------- #
# register_release
# --------------------------------------------------------------------------- #
def _source_json(tmp_path: Path, releases: list[str]) -> Path:
    p = tmp_path / "source.json"
    p.write_text(
        json.dumps({"id": "x", "releases": releases}, indent=2) + "\n",
        encoding="utf-8",
    )
    return p


def test_register_release_lands_artifact_and_orders_releases(tmp_path):
    raw_dir = tmp_path / "raw"
    artifact_path = tmp_path / "in.json"
    artifact_path.write_text(json.dumps(_new_release_artifact()))
    # An existing older release already registered; the new one sorts after it.
    source_json = _source_json(tmp_path, [BUILDO])

    summary = register_release.register(
        NEW_RELEASE, artifact_path, raw_dir=raw_dir, source_json=source_json
    )

    assert (raw_dir / f"{NEW_RELEASE}.json").exists()
    assert summary["added_to_source"] is True
    # Ordered oldest-first by release timestamp (buildo 2026-07-22 < new 08-01).
    assert json.loads(source_json.read_text())["releases"] == [BUILDO, NEW_RELEASE]


def test_register_release_is_idempotent(tmp_path):
    raw_dir = tmp_path / "raw"
    artifact_path = tmp_path / "in.json"
    artifact_path.write_text(json.dumps(_new_release_artifact()))
    source_json = _source_json(tmp_path, [BUILDO, NEW_RELEASE])

    summary = register_release.register(
        NEW_RELEASE, artifact_path, raw_dir=raw_dir, source_json=source_json
    )
    assert summary["added_to_source"] is False
    assert json.loads(source_json.read_text())["releases"] == [BUILDO, NEW_RELEASE]


def test_register_release_rejects_id_mismatch(tmp_path):
    artifact_path = tmp_path / "in.json"
    artifact_path.write_text(json.dumps(_new_release_artifact()))
    with pytest.raises(SystemExit):
        register_release.register(
            "some-other-release-20260101T000000Z",
            artifact_path,
            raw_dir=tmp_path / "raw",
            source_json=_source_json(tmp_path, []),
        )


# --------------------------------------------------------------------------- #
# Ingesting a new release without a hand-coded engine pin
# --------------------------------------------------------------------------- #
def test_new_release_ingests_using_the_artifacts_engine_block(tmp_path):
    # The whole point of the automation: a release the code has never seen
    # ingests without a SystemExit, taking its engine pin from the artifact.
    assert NEW_RELEASE not in ENGINE_VERSIONS
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / f"{NEW_RELEASE}.json").write_text(json.dumps(_new_release_artifact()))
    db_path = tmp_path / "scorecard.db"

    summary = ingest(db_path, raw_dir=raw_dir)
    assert summary["releases"] == 1
    assert summary["results"] > 0

    conn = sqlite3.connect(db_path)
    # Every result for this release is stamped with the artifact's pin.
    engines = {
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT engine_version FROM pe_results WHERE run_id LIKE ?",
            (f"{RUN_PREFIX}%",),
        )
    }
    assert engines == {"1.799.9"}
    # OBBBA rows default to the current producer's scoring mode. Their
    # construction is reform_delta:<measure>:<mode>:cy2026_for_fy<fy>; other
    # reform_delta rows (state bills, repeals) carry no mode segment.
    modes = {
        r[0].split(":")[2]
        for r in conn.execute(
            "SELECT pe_construction FROM pe_results"
            " WHERE pe_construction LIKE '%cy2026_for_fy%'"
        )
    }
    assert modes == {"jcx_stacked"}
    conn.close()


def test_new_release_without_engine_block_fails_loudly(tmp_path):
    # No pin anywhere -> a clear SystemExit, not a KeyError or a silent
    # mis-stamp.
    artifact = _new_release_artifact()
    del artifact["engine"]
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / f"{NEW_RELEASE}.json").write_text(json.dumps(artifact))
    with pytest.raises(SystemExit, match="no engine pin"):
        ingest(tmp_path / "scorecard.db", raw_dir=raw_dir)


def test_new_release_without_scoring_mode_fails_loudly(tmp_path):
    # A release the OBBBA_SCORING_MODE table doesn't name, with OBBBA rows but
    # no explicit mode, must fail loudly rather than default (re-gate blocker
    # 5) — a silent wrong mode reads as release-over-release drift.
    artifact = _new_release_artifact()
    del artifact["obbba_scoring_mode"]
    assert any(r["category"] == "OBBBA" for r in artifact["reforms"])
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / f"{NEW_RELEASE}.json").write_text(json.dumps(artifact))
    with pytest.raises(SystemExit, match="OBBBA scoring mode"):
        ingest(tmp_path / "scorecard.db", raw_dir=raw_dir)


# --------------------------------------------------------------------------- #
# Non-RV table invariant (re-gate blocker 6)
# --------------------------------------------------------------------------- #
def _fresh_db(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / f"{NEW_RELEASE}.json").write_text(json.dumps(_new_release_artifact()))
    db_path = tmp_path / "scorecard.db"
    ingest(db_path, raw_dir=raw_dir)
    return db_path, raw_dir


def test_non_rv_fingerprint_ignores_rv_but_catches_others(tmp_path):
    db_path, _ = _fresh_db(tmp_path)
    conn = sqlite3.connect(db_path)
    base = _non_rv_fingerprint(conn)
    # Mutating the RV lane must NOT move the fingerprint (it's the ingest's
    # own row).
    conn.execute(
        "UPDATE lanes SET detail = 'touched' WHERE lane = 'populace-reform-validation'"
    )
    conn.commit()
    assert _non_rv_fingerprint(conn) == base
    # Inserting an unrelated (harvest-style) lane MUST move it.
    conn.execute(
        "INSERT INTO lanes (lane, stage, detail, updated_at)"
        " VALUES ('harvest-x', 'ingested', 'seed', '2026-01-01')"
    )
    conn.commit()
    assert _non_rv_fingerprint(conn) != base
    conn.close()


def test_reingest_preserves_non_rv_rows(tmp_path):
    # A row this ingest must never touch (a foreign lane) survives a rebuild,
    # and the rebuild completes (the invariant assertion passes).
    db_path, raw_dir = _fresh_db(tmp_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO lanes (lane, stage, detail, updated_at)"
        " VALUES ('harvest-x', 'ingested', 'seed', '2026-01-01')"
    )
    conn.commit()
    conn.close()
    ingest(db_path, raw_dir=raw_dir)  # rebuild
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT stage FROM lanes WHERE lane = 'harvest-x'"
    ).fetchone() == ("ingested",)
    conn.close()


def test_reingest_preserves_non_rv_pe_results_row(tmp_path):
    # A harvest-style pe_results row (run_id NOT populace-rv-%) must survive the
    # rebuild — pins the delete-scope so broadening the DELETE (or dropping the
    # fingerprint abort) can't silently wipe non-RV results with all else green
    # (re-gate blocker 6 / test-gap note).
    db_path, raw_dir = _fresh_db(tmp_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO pe_results (claim_id, status, engine_version, data_bundle,"
        " pe_construction, run_id, computed_at, annotations)"
        " VALUES ('harvest-claim', 'comparable', '1.0.0', 'harvest-bundle',"
        " 'direct', 'harvest-run-123', '2026-01-01', '{}')"
    )
    conn.commit()
    conn.close()
    ingest(db_path, raw_dir=raw_dir)  # rebuild must not touch the seeded row
    conn = sqlite3.connect(db_path)
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM pe_results WHERE run_id = 'harvest-run-123'"
        ).fetchone()[0]
        == 1
    )
    conn.close()


def test_new_release_without_attestation_fails_loudly(tmp_path):
    # A non-historical release must carry a complete provenance attestation;
    # the ingest CONSUMES it and rejects a missing/unknown one rather than
    # ingesting un-attested provenance (re-gate blocker 6).
    artifact = _new_release_artifact()
    del artifact["_attestation"]
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / f"{NEW_RELEASE}.json").write_text(json.dumps(artifact))
    with pytest.raises(SystemExit, match="attestation"):
        ingest(tmp_path / "scorecard.db", raw_dir=raw_dir)

    # An `unknown`-stamped field is likewise rejected.
    artifact = _new_release_artifact()
    artifact["_attestation"]["producer_commit"] = "unknown"
    (raw_dir / f"{NEW_RELEASE}.json").write_text(json.dumps(artifact))
    with pytest.raises(SystemExit, match="missing/unknown"):
        ingest(tmp_path / "scorecard.db", raw_dir=raw_dir)


# --------------------------------------------------------------------------- #
# backfill.merge revision refusal (re-gate blocker 4) — pure stdlib
# --------------------------------------------------------------------------- #
import backfill  # noqa: E402


def test_refuse_if_mixed_revisions(tmp_path):
    part_dir = tmp_path / "partials"
    part_dir.mkdir()
    (part_dir / "a.json").write_text("{}")  # something to purge

    # Mixed producer revisions -> refuse AND purge the workdir partials.
    with pytest.raises(SystemExit, match="multiple or unstamped"):
        backfill._refuse_if_mixed({"aaa", "bbb"}, {"drv"}, part_dir)
    assert not part_dir.exists()

    # A missing/unknown stamp is refused too (not just a clean 2-way mix).
    assert backfill._revision_dirty({None})
    assert backfill._revision_dirty({"unknown"})
    assert backfill._revision_dirty(set())
    assert backfill._revision_dirty({"a", "b"})
    # A single known revision on both axes is accepted (no raise).
    ok_dir = tmp_path / "ok"
    ok_dir.mkdir()
    backfill._refuse_if_mixed({"aaa"}, {"drv"}, ok_dir)
    assert ok_dir.exists()  # not purged
