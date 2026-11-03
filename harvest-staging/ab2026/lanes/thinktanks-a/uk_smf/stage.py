#!/usr/bin/env python3
"""Stage the Social Market Foundation's Autumn Budget 2026 claims (#230, family uk_smf).

The assigned page answered every fetch with a Cloudflare challenge (HTTP
403, "Just a moment..."), and the assignment lists no local copy, so the
family stages no rows and lists no primaries (NOTES.md). Running this file
rewrites an empty manifest.jsonl and an empty, deterministic
claims_staged.jsonl.gz:

    python sources/harvest-uk-ab2026-2026-10-29/uk_smf/stage.py
"""

import gzip
import hashlib
import io
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Unreached pages: each fetch returned the challenge page, not the primary.
# The challenge pages' sha256 are recorded only as evidence of the refusal.
UNREACHED = [
    {"url": "https://www.smf.co.uk/todays-budget-provides-immediate-relief-for-households-but-details-of-changes-on-many-larger-issues-yet-to-come-think-tank-says/",
     "fetches": [("2026-10-29T16:17Z", 403, "70b6e26e33ba117f8ef0e397f9c99919d0c9677972d3b461cb2c8d9d9730deff"),
                 ("2026-10-29T16:37Z", 403, "cb5e681e49f5e4a68fb5ffeb37fed8a6887f89575f3df0934c1b206b532480e1")]},
]
ROWS = []


def claims_bytes():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in ROWS:
            gz.write(r)
    return buf.getvalue()


if __name__ == "__main__":
    (HERE / "manifest.jsonl").write_text("", encoding="utf-8")
    data = claims_bytes()
    (HERE / "claims_staged.jsonl.gz").write_bytes(data)
    print(f"{len(ROWS)} rows, {len(UNREACHED)} unreached pages, sha256 {hashlib.sha256(data).hexdigest()}")
