"""Resolve the OBR costings compute staging to claim ids and executed worlds.

`results/uk/staged/obr_costings.jsonl` is what `pipeline/compute_uk_obr_costings.py`
stages: one row per computed head, with an `external_claim_match`
descriptor in the harvest's own vocabulary (source, metric, period,
source_table, reform_hint, the exact harvested conditions). The campaign
ingest attaches results by claim_id or by a per-family translator, and
has no translator for OBR rows — so this step, the UK pattern
produce_campaign_uk set, resolves every descriptor against the slice the
DB ingest keys (ingest_obr_costings.claim_ids) and writes the derived
staging in ingest_campaign's strict claim_id-direct form under
`results/uk/staged_resolved/`.

It also stamps `baseline_key`: the world PE EXECUTED for the row
(ingest_obr_costings.executed_world_key), the result-side half of gate
round 1's finding 1. A reversal on the certified world executed the
registered pre-measure world; the comparisons view's #13 guard then
compares that with the world the OBR scored the claim against, and a
row that differs can never render as plain agreement.

Every lookup is closed: a descriptor that matches no slice row, or a
measure without a registered executed world, raises with nothing written.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import ingest_obr_costings as ingest_mod
from .harvest import REPO

STAGED = REPO / "results" / "uk" / "staged" / "obr_costings.jsonl"
RESOLVED = REPO / "results" / "uk" / "staged_resolved"


def resolve(rows: list[dict]) -> list[dict]:
    by_desc = ingest_mod.claim_ids()
    index = ingest_mod.measures()
    out: list[dict] = []
    for row in rows:
        desc = json.dumps(row["external_claim_match"], sort_keys=True)
        cid = by_desc.get(desc)
        if cid is None:
            raise ValueError(
                f"obr_costings: staged descriptor matches no slice row: {desc[:200]}"
            )
        resolved = {k: v for k, v in row.items() if k != "external_claim_match"}
        resolved["external_claim_match"] = {"claim_id": cid}
        resolved["baseline_key"] = ingest_mod.executed_world_key(
            row["measure_key"], index
        )
        out.append(resolved)
    return out


def produce(db_path: Path | None = None, out_dir: Path | None = None) -> dict:
    """Write the resolved staging; the DB is not read (claim ids are the
    ingest's own function of the slice), the argument keeps the build
    chain's step shape."""
    out_dir = out_dir or RESOLVED
    rows = [json.loads(l) for l in STAGED.read_text().splitlines() if l.strip()]
    resolved = resolve(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / STAGED.name).write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in resolved) + "\n"
    )
    worlds = sorted({r["baseline_key"] for r in resolved})
    return {"resolved": len(resolved), "executed_worlds": len(worlds)}


if __name__ == "__main__":
    print(json.dumps(produce(), indent=1))
