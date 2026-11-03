#!/usr/bin/env python3
"""Stage Child Poverty Action Group's Autumn Budget 2026 claims (#230, family uk_cpag).

Both assigned pages answered every fetch with a Cloudflare challenge (HTTP
403, "Just a moment..."), and the assignment lists no local copy, so the
family stages no rows and lists no primaries (NOTES.md). Running this file
rewrites an empty manifest.jsonl and an empty, deterministic
claims_staged.jsonl.gz:

    python sources/harvest-uk-ab2026-2026-10-29/uk_cpag/stage.py
"""

import gzip
import hashlib
import io
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Unreached pages: each fetch returned the challenge page, not the primary.
# The challenge pages' sha256 are recorded only as evidence of the refusal.
UNREACHED = [
    {"url": "https://cpag.org.uk/news/cpags-2026-budget-response",
     "fetches": [("2026-10-29T16:17Z", 403, "b493071ca65505dfe519631fdae55a24913eab5057d048ffb1d1db5ff9cb0752"),
                 ("2026-10-29T16:37Z", 403, "131449484af19395eca78b07573834df7e9994d8b24c6642e5990fe9674ea394")]},
    {"url": "https://cpag.org.uk/news/campaigners-call-ps10-child-uk-budget-boost-child-benefit",
     "fetches": [("2026-10-29T16:17Z", 403, "8d238b41566d6f9e663f517a0fab78e4882679c3d88e1341af5d07429d70320f"),
                 ("2026-10-29T16:37Z", 403, "0f9decd1941d6c0c9b068d4f4d9b2a5f73ed19d6fb1c6a6193495f56929cba9e")]},
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
