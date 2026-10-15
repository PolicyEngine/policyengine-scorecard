"""Refuse a replay output directory unless every file is an expected aggregate.

Scorecard is public, so the run job's upload, and the record job's commit to
the public replay-state branch, may hold only the receipt, status and the
sealed aggregate results. This is an allowlist: every entry must be a regular
file (no symlink, device or other special file) with an allowed extension,
whose bytes parse as that format, under a per-file and a total size cap. The
committed sealed namespace has 30 MB over 316 files, the largest 3.3 MB.

It stops accidental publication (an honest run that writes a dataset,
household-level table or binary). Content that parses can still carry
anything a deliberately malicious candidate encodes in it; RELEASE_REPLAY.md
states that limit.

Standard library only: it runs with the runner's system Python, before and
independently of anything the candidate installed.

    python3 -I .github/scripts/uk_replay_output_guard.py output
"""

from __future__ import annotations

import json
import stat
import sys
from pathlib import Path

ALLOWED_SUFFIXES = (".json", ".jsonl", ".csv", ".md", ".txt")
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024


def _parses(path: Path, data: bytes) -> str | None:
    """None when the bytes are what the extension says; else the reason."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "not UTF-8 text"
    if "\x00" in text:
        return "contains a NUL byte"
    try:
        if path.suffix == ".json":
            json.loads(text)
        elif path.suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    json.loads(line)
    except ValueError as error:
        return f"does not parse as {path.suffix[1:]} ({error})"
    return None


def problems(root: Path) -> list[str]:
    """Every reason to refuse ``root``; empty when it may leave the runner."""
    if not root.exists() and not root.is_symlink():
        return []
    found, total = [], 0
    entries = [root, *sorted(root.rglob("*"))] if root.is_dir() else [root]
    for path in entries:
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            found.append(f"{path}: not a regular file (symlink or special file)")
            continue
        if path.suffix not in ALLOWED_SUFFIXES:
            found.append(f"{path}: extension not allowed ({path.suffix or 'none'})")
            continue
        size = path.stat().st_size
        total += size
        if size > MAX_FILE_BYTES:
            found.append(f"{path}: {size} bytes, over {MAX_FILE_BYTES}")
            continue
        reason = _parses(path, path.read_bytes())
        if reason:
            found.append(f"{path}: {reason}")
    if total > MAX_TOTAL_BYTES:
        found.append(f"{root}: {total} bytes in all, over {MAX_TOTAL_BYTES}")
    return found


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: uk_replay_output_guard.py <directory>", file=sys.stderr)
        return 2
    refused = problems(Path(argv[0]))
    for reason in refused:
        print(f"::error::refusing to publish {reason}")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
