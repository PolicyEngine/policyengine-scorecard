#!/usr/bin/env python3
"""Stage the Fraser of Allander Institute and Scottish Fiscal Commission (#230, family uk_fai_sfc).

The family has no rows and lists no primaries (NOTES.md):

- FAI's 28 October reaction ("UK Budget 2026: Rearranging not reimagining")
  refused every fetch with HTTP 403, as does its 29 October post on
  Scotland's funding, found on 4 November through FAI's RSS feed.
- The SFC published nothing in scope on 28 or 29 October.
- The Scottish Government's five rows, first staged here on 29 October,
  moved to uk_devolved_govts on 3 November (thinktanks-b review, finding 7),
  whose stage.py now writes them.

Running this file rewrites an empty manifest.jsonl and an empty,
deterministic claims_staged.jsonl.gz, as the other empty families' stagers
do:

    python harvest-staging/ab2026/lanes/thinktanks-b/uk_fai_sfc/stage.py
"""

import gzip
import hashlib
import io
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Unreached pages: each fetch returned FAI's 103-byte error page, not the
# primary. The error page's sha256 is recorded only as evidence of the
# refusal.
UNREACHED = [
    {"url": "https://fraserofallander.org/uk-budget-reaction/",
     "fetches": [("2026-10-29T15:22:23Z", 403, "f261423d1da97890ff6bfccd31ff4ee0b74f69351cf75095fbe791cb16cbf5bd"),
                 ("2026-11-04", 403, "f261423d1da97890ff6bfccd31ff4ee0b74f69351cf75095fbe791cb16cbf5bd")]},
    {"url": "https://fraserofallander.org/rising-or-falling-why-both-claims-about-scotlands-funding-can-be-true/",
     "fetches": []},  # found via https://fraserofallander.org/feed/ on 4 November; behind the same 403
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
