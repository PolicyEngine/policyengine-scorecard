"""Reproduce the NIESR AB2026 manifest and empty, deterministic claims file.

The Budget-day primary contains fiscal/market macro commentary, reserved for
the #55 lane, and no household/static estimate. See NOTES.md for the audit.
"""

import gzip
import io
import json
from pathlib import Path


FAMILY_DIR = Path(__file__).resolve().parent
MANIFEST = [
    {
        "url": "https://niesr.ac.uk/blog/breathing-space-not-strategy",
        "title": "Breathing Space, Not a Strategy",
        "date": "2026-10-28",
        "publisher": "NIESR",
        "sha256": "0108b60ad2a85e65a717c03a68060ad9c45fdcbe09cb5a24eca374a618436ccb",
        "bytes": 142303,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": (
            "Fetched fresh with the specified curl browser User-Agent; HTTP 200. "
            "Response Date: 2026-10-29T15:22:11Z; bytes saved as "
            ".ab2026-primaries/uk_niesr/breathing-space-not-strategy.html. "
            "Publication date from article:published_time "
            "(2026-10-28T15:59:11+00:00), matching the visible date. "
            "Macro/fiscal-stance commentary only: no household/static rows. "
            "No assignment local copy was supplied, so no earlier version was compared."
        ),
    }
]

# Rows remain explicit data, including when no eligible estimates were printed.
ROWS = []


def main():
    manifest = "".join(
        json.dumps(document, sort_keys=True, ensure_ascii=False) + "\n"
        for document in MANIFEST
    )
    (FAMILY_DIR / "manifest.jsonl").write_text(manifest, encoding="utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as compressed:
        for row in ROWS:
            compressed.write(
                (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode(
                    "utf-8"
                )
            )
    (FAMILY_DIR / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())
    print(f"{FAMILY_DIR.name}: {len(ROWS)} rows, {len(MANIFEST)} primary")


if __name__ == "__main__":
    main()
