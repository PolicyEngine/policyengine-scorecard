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
