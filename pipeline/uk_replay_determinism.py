"""Whether a replayed measure-year artifact reproduces a committed one.

CI's real-replay step (`.github/workflows/ci.yml`, "One real measure-year
replays byte for byte") recomputes one committed artifact with the current
code and compares the bytes. A namespace sealed before the processed-value
check (#186) holds artifacts without that check's evidence fields, which the
current code writes on every variant run. The replay is then compared with
exactly those fields removed, and a notice says so; every other byte must
still match. An artifact that carries any evidence field is compared whole.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pipeline.compute_uk_event import canonical_bytes

# The fields a variant artifact gained with the processed-value check.
PROCESSED_EVIDENCE_FIELDS = (
    "processed_parameter_values",
    "parameter_reform_routes",
    "processed_value_notes",
)


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
