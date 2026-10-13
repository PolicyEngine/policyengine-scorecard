"""Land a harvested reform_validation.json into the Scorecard's source tree.

The Modal backfill (modal_backfill_app.py) produces one release's
reform_validation.json; this drops it under
``sources/populace-reform-validation/raw/<release_id>.json`` and adds the
release to that source's ``source.json`` ``releases`` list (deduped, ordered
oldest-first by the release timestamp — the same order the ingest globs in).
It does NOT run the ingest; the workflow does that next so the rebuilt DB is
part of the same commit.

Usage:
    python tools/reform_validation/register_release.py <release_id> <artifact_path>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = REPO / "sources" / "populace-reform-validation"
RAW_DIR = SOURCE_DIR / "raw"
SOURCE_JSON = SOURCE_DIR / "source.json"


def _timestamp_key(release_id: str) -> str:
    # Reuse the ingest's parser so raw/ ordering and the releases list agree.
    from scorecard_db.ingest_reform_validation import _release_timestamp

    return _release_timestamp(release_id)


def register(
    release_id: str,
    artifact_path: Path,
    *,
    raw_dir: Path = RAW_DIR,
    source_json: Path = SOURCE_JSON,
) -> dict:
    """Copy the artifact into raw/ and register the release in source.json.

    Returns a summary dict. Idempotent: re-registering an existing release
    overwrites its raw file and leaves the releases list unchanged.
    """
    artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    if artifact.get("release_id") != release_id:
        raise SystemExit(
            f"artifact release_id {artifact.get('release_id')!r} != {release_id!r}"
        )
    _timestamp_key(release_id)  # fail fast if the id has no parseable timestamp

    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / f"{release_id}.json"
    dest.write_text(json.dumps(artifact, indent=1), encoding="utf-8")

    doc = json.loads(source_json.read_text(encoding="utf-8"))
    releases = doc.get("releases", [])
    added = release_id not in releases
    if added:
        releases.append(release_id)
    doc["releases"] = sorted(set(releases), key=_timestamp_key)
    source_json.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        raw_file = str(dest.relative_to(REPO))
    except ValueError:  # a caller (tests) may write outside the repo tree
        raw_file = str(dest)
    return {
        "release_id": release_id,
        "raw_file": raw_file,
        "added_to_source": added,
        "releases": doc["releases"],
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: register_release.py <release_id> <artifact_path>")
    summary = register(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
