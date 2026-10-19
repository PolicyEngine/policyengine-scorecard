"""The replay-engine matrix: every certified variant in the variant index.

CI's ``replay-engine`` job runs once for each id this prints: the certified
variants of ``data/uk/replay_variants.json``, in index order, as a JSON list
on one line. A results pull request adds a variant to the index alone, and
CI replays it from there, so nothing has to edit a workflow file.

Standard library only, run with the runner's own Python (``python3 -I``) in
a job that installs nothing. CI puts each id in a job name, an environment
variable, shell commands and paths, so every id in the index must be plain:
letters, digits, ``.``, ``_`` and ``-``, starting with a letter or digit,
with no ``..`` (the rule the results pull request applies to a new variant).
Anything the matrix cannot be built from fails the job rather than replay
fewer variants: a record that is not an object, an unknown status, a repeated
id, no certified variant, or more than GitHub's 256 jobs per matrix.

    python3 -I .github/scripts/uk_replay_engine_matrix.py data/uk/replay_variants.json
"""

from __future__ import annotations

import json
import re
import sys

# uk_replay_variants.STATUSES (a test checks).
STATUSES = ("certified", "candidate", "retired")
PLAIN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
# "A job matrix can generate a maximum of 256 jobs per workflow run."
# https://docs.github.com/en/actions/reference/limits
MAX_JOBS = 256


class MatrixError(Exception):
    """The index gives no matrix: the job fails rather than replay less."""


def plain(variant_id: object) -> bool:
    return (
        isinstance(variant_id, str)
        and PLAIN_ID.fullmatch(variant_id) is not None
        and ".." not in variant_id
    )


def certified_ids(document: object) -> list[str]:
    """Every certified variant's id, in index order."""
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise MatrixError("the variant index is not a schema_version 1 document")
    variants = document.get("variants")
    if not isinstance(variants, list) or not variants:
        raise MatrixError("the variant index lists no variants")
    seen: set[str] = set()
    certified = []
    for record in variants:
        if not isinstance(record, dict):
            raise MatrixError("a variant record is not an object")
        variant_id = record.get("variant_id")
        if not plain(variant_id):
            raise MatrixError(f"variant_id {variant_id!r} is not a plain id")
        if variant_id in seen:
            raise MatrixError(f"the variant index repeats {variant_id}")
        seen.add(variant_id)
        if record.get("status") not in STATUSES:
            raise MatrixError(
                f"{variant_id} has status {record.get('status')!r}, not one of "
                f"{', '.join(STATUSES)}"
            )
        if record["status"] == "certified":
            certified.append(variant_id)
    if not certified:
        raise MatrixError("the variant index has no certified variant")
    if len(certified) > MAX_JOBS:
        raise MatrixError(
            f"{len(certified)} certified variants exceed GitHub's {MAX_JOBS} jobs "
            "per matrix"
        )
    return certified


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: uk_replay_engine_matrix.py INDEX", file=sys.stderr)
        return 2
    try:
        with open(arguments[0], "rb") as handle:
            ids = certified_ids(json.load(handle))
    except (OSError, ValueError, MatrixError) as problem:
        print(f"::error::{problem}", file=sys.stderr)
        return 1
    print(json.dumps(ids, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
