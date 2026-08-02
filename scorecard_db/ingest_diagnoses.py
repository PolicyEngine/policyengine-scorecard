"""Write the adjudicated diagnosis batch into the diagnoses table.

Each queue item anchors to a primary claim (the national/state row it is
about); the full memo lives at diagnosis/DIAGNOSES.md and the
machine-readable batch at diagnosis/diagnoses.json. Also emits
data/diagnoses_rows.json for the app (row-key -> diagnosis chip).
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .ingest_platform import _probe

REPO = Path(__file__).resolve().parent.parent

# queue_id -> the platform row the diagnosis anchors to
PRIMARY_ROW = {
    1: ("snap", "participation_rate", "US", "total"),
    2: ("tanf", "participation_rate", "US", "total"),
    3: ("eitc", "eligible_count", "US", "total"),
    4: ("ctc_refund", "eligible_count", "US", "total"),
    5: ("ssi", "eligible_count", "US", "total"),
    6: ("housing", "participation_rate", "US", "total"),
    7: ("spm_poverty", "poverty_rate_fullpart", "US", "total"),
    8: ("spm_poverty", "poverty_rate", "US", "child"),
    9: ("snap", "participation_rate", "AK", "total"),
    10: ("wic", "eligible_count", "US", "age_0"),
}

# diagnoses.json classes -> DB enum (external_model_issue -> external_issue)
CLASS_MAP = {
    "pe_gap": "pe_gap",
    "external_model_issue": "external_issue",
    "concept_mismatch": "concept_mismatch",
    "data_vintage": "vintage",
    "vintage": "vintage",
}

UNIT_FOR = {
    ("snap", "participation_rate"): "persons",
    ("tanf", "participation_rate"): "persons",
    ("eitc", "eligible_count"): "tax_units",
    ("ctc_refund", "eligible_count"): "tax_units",
    ("ssi", "eligible_count"): "adults_18plus",
    ("housing", "participation_rate"): "households",
    ("spm_poverty", "poverty_rate_fullpart"): "share",
    ("spm_poverty", "poverty_rate"): "share",
    ("wic", "eligible_count"): "children_0thr4",
}


def ingest(db_path: Path) -> dict:
    batch = json.loads((REPO / "diagnosis" / "diagnoses.json").read_text())
    db = ScorecardDB(db_path)
    app_rows = []
    for item in batch:
        qid = item["queue_id"]
        program, metric, geo, sub = PRIMARY_ROW[qid]
        probe = _probe(
            {
                "program": program,
                "metric": metric,
                "geography": geo,
                "subgroup": sub,
                "variant": None,
                "unit_concept": UNIT_FOR[(program, metric)],
            }
        )
        rationale = (
            f"[batch1 #{qid}, confidence {item['confidence']}] "
            f"{item['title']}"
        )
        db.diagnose(
            probe.claim_id(),
            CLASS_MAP[item["classification"]],
            rationale,
            "diagnosis/DIAGNOSES.md",
        )
        app_rows.append(
            {
                "program": program,
                "metric": metric,
                "geography": geo,
                "subgroup": sub,
                "queue_id": qid,
                "classification": item["classification"],
                "confidence": item["confidence"],
                "title": item["title"],
                "fix_type": (item.get("fix_draft") or {}).get("type"),
            }
        )
    db.set_lane(
        "diagnosis-batch-1", "computed",
        "10/10 adjudicated: 6 pe_gap, 3 concept_mismatch, 1 external issue; "
        "fix drafts in diagnosis/DIAGNOSES.md",
        "2026-08-01T23:59:00",
    )
    db.close()
    out = REPO / "data" / "diagnoses_rows.json"
    out.write_text(json.dumps(app_rows))
    return {"diagnosed": len(app_rows)}


if __name__ == "__main__":
    import sys

    print(json.dumps(ingest(
        Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    )))
