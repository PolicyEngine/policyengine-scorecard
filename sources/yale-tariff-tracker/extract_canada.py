"""Authenticate Yale's published country panel and vendor its Canada rows.

Usage (from the scorecard repository):
    git -C <tracker-checkout> show <publication-commit>:<country-file> |
      uv run python sources/yale-tariff-tracker/extract_canada.py

The output preserves the publication's header and selected row bytes exactly.
"""

import csv
import hashlib
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "raw" / "daily_by_country_canada_2026-06-09.csv"

PUBLICATION_SHA256 = "15704e514ffe57fde8eaec79c44d0b48232f24ef36c00c1a6d3d8354bcbf0603"
PUBLICATION_ROWS = 175_200
CANADA_KEY = ("1220", "Canada", "canada")
CANADA_ROWS = 730
CANADA_EXTRACT_SHA256 = (
    "e7718b626bba1648fa3e86f0330facdbcf8f60a05a516fbba790948b4453ac55"
)


def extract_canada(payload: bytes) -> bytes:
    """Return byte-preserving Canada rows from the authenticated publication."""
    digest = hashlib.sha256(payload).hexdigest()
    if digest != PUBLICATION_SHA256:
        raise ValueError(f"publication SHA-256 mismatch: {digest}")

    lines = payload.splitlines(keepends=True)
    if len(lines) - 1 != PUBLICATION_ROWS:
        raise ValueError(f"expected {PUBLICATION_ROWS} publication rows")

    header = next(csv.reader(io.StringIO(lines[0].decode())))
    country = header.index("country")
    country_name = header.index("country_name")
    country_abbr = header.index("country_abbr")
    selected = []
    for line in lines[1:]:
        row = next(csv.reader(io.StringIO(line.decode())))
        if (row[country], row[country_name], row[country_abbr]) == CANADA_KEY:
            selected.append(line)

    if len(selected) != CANADA_ROWS:
        raise ValueError(f"expected {CANADA_ROWS} Canada rows")
    output = lines[0] + b"".join(selected)
    output_digest = hashlib.sha256(output).hexdigest()
    if output_digest != CANADA_EXTRACT_SHA256:
        raise ValueError(f"Canada extract SHA-256 mismatch: {output_digest}")
    return output


def main() -> None:
    """Read authenticated publication bytes on stdin and write the raw extract."""
    output = extract_canada(sys.stdin.buffer.read())
    OUT.write_bytes(output)
    print(f"{OUT}: {CANADA_ROWS} rows, sha256={CANADA_EXTRACT_SHA256}")


if __name__ == "__main__":
    main()
