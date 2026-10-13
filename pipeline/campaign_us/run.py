"""Reconstruct and run the US compute-campaign families.

The original campaign code (2026-08-02, CAMPAIGN.md driver) is not
available; each family module re-implements its rows from the recipe text
the original staged rows carry (``pe_construction`` + annotations) and
states that construction in its docstring.

Usage (one family per invocation; at most one simulation runs at a time,
each in its own child process):

    <env python> pipeline/campaign_us/run.py <family> --out <dir>

    <family>  cbo_free_joins | cpsp_ctc_2024 | jct_obbba_provision4 |
              pwbm_ss_elimination | tpc_t25_0209_t26_0029 |
              urban_subgroup_counts | all

The engine/data bundle is whatever ``policyengine`` the interpreter has:
``.venv-pe501`` (policyengine 5.0.1 = us-5.0.1, the August 2026 bundle) for
the reproduction check, ``.venv-pe`` (policyengine 6.2.1) for the new
certified bundle. Rows are written in the original JSONL schema to
``<dir>/<family>.jsonl``; per-run metadata (every job's raw values, the
reform dicts actually applied, timings) goes to
``pipeline/campaign_us/runs/<family>__<bundle_id>.json``.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from common import log, write_family

FAMILIES = [
    "cbo_free_joins",
    "pwbm_ss_elimination",
    "jct_obbba_provision4",
    "cpsp_ctc_2024",
    "urban_subgroup_counts",
    "tpc_t25_0209_t26_0029",
]


def reproduced_mask(fam: str, old_dir: Path) -> list[bool]:
    """Per original row: did the old-bundle reproduction match?"""
    import json

    from common import load_original
    from validate import compare

    path = old_dir / f"{fam}.jsonl"
    if not path.exists():
        raise SystemExit(f"{fam}: no old-bundle reproduction at {path}")
    old = [json.loads(x) for x in path.read_text().splitlines() if x]
    orig = load_original(fam)
    if len(old) != len(orig):
        raise SystemExit(
            f"{fam}: old-bundle run has {len(old)} rows, original {len(orig)}"
        )
    return [compare(o["pe_value"], r["pe_value"])[1] for o, r in zip(orig, old)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("family", choices=FAMILIES + ["all"])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "--require-reproduced",
        type=Path,
        metavar="OLD_DIR",
        help="drop every row whose old-bundle reproduction in OLD_DIR did not"
        " match the original (validate.py tolerance); refuse a family with no"
        " old-bundle run",
    )
    args = ap.parse_args()
    fams = FAMILIES if args.family == "all" else [args.family]
    for fam in fams:
        t0 = time.time()
        log(f"=== family {fam} ===")
        mod = importlib.import_module(fam)
        if args.require_reproduced:
            keep = reproduced_mask(fam, args.require_reproduced)
            if not any(keep):
                log(f"=== {fam}: no row reproduced on the old bundle; skipped ===")
                continue
        rows, meta = mod.run()
        if args.require_reproduced:
            dropped = [i for i, k in enumerate(keep) if not k]
            meta["dropped_not_reproduced"] = dropped
            if dropped:
                log(f"dropping rows not reproduced on the old bundle: {dropped}")
            rows = [r for r, k in zip(rows, keep) if k]
        meta["family"] = fam
        meta["rows"] = [
            {
                "pe_value": r["pe_value"],
                "match": r.get("external_claim_match") or r.get("exhibit_meta"),
            }
            for r in rows
        ]
        meta["wall_seconds"] = round(time.time() - t0, 1)
        write_family(args.out, fam, rows, meta)
        log(
            f"=== {fam}: {len(rows)} rows -> {args.out / (fam + '.jsonl')}"
            f" ({meta['wall_seconds']}s) ==="
        )


if __name__ == "__main__":
    main()
