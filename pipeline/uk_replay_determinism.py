"""Whether a replayed measure-year artifact reproduces a committed one.

The real replay (`.github/workflows/uk-replay-determinism.yml`) recomputes one
committed artifact on the variant's engine, inside the candidate sandbox, and
this module compares the bytes, outside it, under the runner's own Python. It
imports only the standard library, so that Python needs nothing installed. A
namespace sealed before the processed-value check (#186) holds artifacts
without that check's evidence fields, which the current code writes on every
variant run. The replay is then compared with exactly those fields removed,
and a notice says so; every other byte must still match. An artifact that
carries any evidence field is compared whole.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# The fields a variant artifact gained with the processed-value check.
PROCESSED_EVIDENCE_FIELDS = (
    "processed_parameter_values",
    "parameter_reform_routes",
    "processed_value_notes",
)


def canonical_bytes(value: object) -> bytes:
    """compute_uk_event.canonical_bytes, without importing the engine's
    dependencies (tests/test_uk_replay_determinism.py checks they agree)."""
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def compare(replayed: bytes, committed: bytes) -> tuple[bool, str | None]:
    """(matches, notice). The notice is set when evidence fields were removed."""
    if replayed == committed:
        return True, None
    # The stripped replay holds no evidence field, so it can only equal a
    # committed artifact that holds none either.
    replay = json.loads(replayed)
    if replayed != canonical_bytes(replay):
        return False, None
    removed = [field for field in PROCESSED_EVIDENCE_FIELDS if field in replay]
    if not removed:
        return False, None
    stripped = {k: v for k, v in replay.items() if k not in removed}
    if canonical_bytes(stripped) != committed:
        return False, None
    return True, (
        "The committed artifact predates processed-value evidence (#186); "
        f"compared with {', '.join(removed)} removed from the replay"
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: uk_replay_determinism REPLAYED COMMITTED", file=sys.stderr)
        return 2
    replayed, committed = (Path(a) for a in args)
    # The replay comes back from the sandbox: only a regular file counts, so a
    # link to the committed artifact is not a reproduction of it.
    if replayed.is_symlink() or not replayed.is_file():
        print(f"{replayed} is not a regular file", file=sys.stderr)
        return 1
    matches, notice = compare(replayed.read_bytes(), committed.read_bytes())
    if notice:
        print(f"::notice::{notice}")
    if not matches:
        print(f"{replayed} differs from {committed}", file=sys.stderr)
        return 1
    print(f"{replayed} reproduces {committed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
