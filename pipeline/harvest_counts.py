"""Write or check a harvest's COUNTS.json from its family directories.

COUNTS.json pins, per family, the row count the ingest's exact accounting
reads as `read`, the primary count, the family's producer slugs and the
sha256 of its claims_staged.jsonl.gz, plus `_totals`. The AB2025 file was
written by hand; this computes the same shape so a new family cannot be
added without its pin moving in the same commit.

    python pipeline/harvest_counts.py sources/harvest-uk-ab2026-2026-10-29 --pinned-on 2026-10-29
    python pipeline/harvest_counts.py sources/harvest-uk-ab2026-2026-10-29 --check
"""

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path


def counts(harvest, pinned_on):
    out, rows_total, restated = {}, 0, 0
    families = sorted(
        p for p in Path(harvest).iterdir() if (p / "claims_staged.jsonl.gz").exists()
    )
    for fam in families:
        gz = fam / "claims_staged.jsonl.gz"
        with gzip.open(gz, "rt") as fh:
            rows = [json.loads(line) for line in fh if line.strip()]
        primaries = [
            line
            for line in (fam / "manifest.jsonl").read_text().splitlines()
            if line.strip()
        ]
        out[fam.name] = {
            "rows": len(rows),
            "primaries": len(primaries),
            "claims_sha256": hashlib.sha256(gz.read_bytes()).hexdigest(),
            "sources": sorted({r["source"] for r in rows}),
        }
        rows_total += len(rows)
        restated += sum(1 for r in rows if r["attribution"] == "restated")
    out["_totals"] = {
        "rows": rows_total,
        "restated": restated,
        "families": len(families),
        "pinned_on": pinned_on,
    }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("harvest")
    ap.add_argument("--pinned-on")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    path = Path(args.harvest) / "COUNTS.json"
    if args.check:
        pinned = json.loads(path.read_text())
        fresh = counts(args.harvest, pinned["_totals"]["pinned_on"])
        if fresh != pinned:
            print("COUNTS.json is stale")
            return 1
        print("COUNTS.json matches the families")
        return 0
    if not args.pinned_on:
        ap.error("--pinned-on is required when writing")
    path.write_text(json.dumps(counts(args.harvest, args.pinned_on), indent=1) + "\n")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
