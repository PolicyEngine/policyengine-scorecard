"""Export DB-backed populations for the app -> data/populations.json.

The Urban SotSN population reaches the app through the file-based
pipeline/build_comparison.py export (data/comparison.json). Everything
else — today, exactly the reform-validation registry (issue #20): its 205
minted claims plus the 36 harvested JCX-35-25 provision claims its OBBBA
results attach to — lives only in scorecard.db. This module exports every
non-Urban claim that has at least one pe_result, carrying the dimension
the Urban export doesn't have: the full per-release result history
(one row per certified release, engine pins and OBBBA scoring mode in the
construction), so cross-release drift is visible.

Doctrine (issues #1/#9): descriptive only. Statuses and calibration
relationships are exported verbatim; ratios are raw pe/external with no
pass/fail anywhere. concept_mismatch results carry their construction so
the app can label, never grade.

Also refreshes data/lanes.json via ingest_harvest.sync_lane_feed so the
populace-reform-validation lane appears in mission control.

Usage:
    PYTHONPATH=. python -m scorecard_db.export_populations data/scorecard.db
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .db import ScorecardDB
from .ingest_harvest import sync_lane_feed

REPO = Path(__file__).resolve().parent.parent
URBAN_SOURCE = "urban_sotsn"

_RELEASE_TOKEN = (
    "l0-refit",
    "buildi",
    "buildj",
    "buildo",
    "buildp",
    "f0af251",
)


def release_label(bundle: str) -> str:
    """Short human label for a data-bundle id ("buildo", "l0-refit")."""
    for token in _RELEASE_TOKEN:
        if token in bundle:
            return token
    return bundle.rsplit("-", 1)[0][-12:]


def _ratio(pe: float | None, external: float | None) -> float | None:
    if pe is None or external is None or external == 0:
        return None
    return pe / external


def export(
    db_path: Path,
    out_path: Path | None = None,
    lanes_path: Path | None = None,
    built: str | None = None,
) -> dict:
    out_path = out_path or REPO / "data" / "populations.json"
    db = ScorecardDB(db_path)
    claims = db.conn.execute(
        """SELECT s.*, d.diagnosis_class, d.rationale, d.action_link
           FROM external_scores s
           LEFT JOIN diagnoses d USING (claim_id)
           WHERE s.source != ?
             AND EXISTS (SELECT 1 FROM pe_results r
                         WHERE r.claim_id = s.claim_id)
           ORDER BY s.source, s.metric, s.period, s.source_column,
                    s.claim_id""",
        (URBAN_SOURCE,),
    ).fetchall()

    rows = []
    by_source: dict[str, int] = {}
    by_status: dict[str, int] = {}
    multi_release = 0
    for c in claims:
        results = [
            {
                "value": r["computed_value"],
                "status": r["status"],
                "engine_version": r["engine_version"],
                "data_bundle": r["data_bundle"],
                "release": release_label(r["data_bundle"]),
                "construction": r["pe_construction"],
                "computed_at": r["computed_at"],
                "annotations": json.loads(r["annotations"]),
            }
            for r in db.conn.execute(
                """SELECT computed_value, status, engine_version,
                          data_bundle, pe_construction, computed_at,
                          annotations
                   FROM pe_results WHERE claim_id = ?
                   ORDER BY computed_at, id""",
                (c["claim_id"],),
            )
        ]
        latest = results[-1]
        publication = json.loads(c["publication"])
        reform = json.loads(c["reform_json"])
        conditions = json.loads(c["conditions"])
        # Harvest OBBBA claims carry no per-claim name — the provision
        # label in conditions is their identity; the publication title is
        # the whole JCX document.
        name = (
            publication.get("name")
            or conditions.get("provision")
            or publication.get("title")
            or ""
        )
        if len({r["data_bundle"] for r in results}) > 1:
            multi_release += 1
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1
        by_status[latest["status"]] = by_status.get(latest["status"], 0) + 1
        rows.append(
            {
                "claim_id": c["claim_id"],
                "source": c["source"],
                "source_column": c["source_column"],
                "name": name,
                "window": publication.get("window") or "",
                "publication_title": publication.get("title") or "",
                "url": publication.get("url") or "",
                "metric": c["metric"],
                "unit_concept": c["unit_concept"],
                "value_kind": c["value_kind"],
                "period": c["period"],
                "time_basis": c["time_basis"],
                "period_start": c["period_start"],
                "period_end": c["period_end"],
                "geography": c["geography"],
                "program": c["program"],
                "conditions": conditions,
                "reform_framework": reform.get("framework"),
                "reform_key": c["reform_key"],
                "external_value": c["value"],
                "calibration_relationship": c["calibration_relationship"],
                "latest": {
                    **latest,
                    "ratio": _ratio(latest["value"], c["value"]),
                    "delta": (
                        latest["value"] - c["value"]
                        if latest["value"] is not None and c["value"] is not None
                        else None
                    ),
                },
                "results": results,
                "diagnosis": (
                    {
                        "class": c["diagnosis_class"],
                        "rationale": c["rationale"],
                        "action_link": c["action_link"],
                    }
                    if c["diagnosis_class"]
                    else None
                ),
            }
        )

    payload = {
        "built": built or date.today().isoformat(),
        "note": (
            "Non-Urban populations exported from scorecard.db: the populace"
            " reform-validation registry (issue #20) plus the compute"
            " campaign's attached comparisons (TPC/CPSP/PWBM/CBO/JCT)."
            " Statuses and calibration relationships are verbatim; nothing"
            " here is a pass/fail grade."
        ),
        "summary": {
            "claims": len(rows),
            "multi_release_claims": multi_release,
            "by_source": dict(sorted(by_source.items())),
            "by_latest_status": dict(sorted(by_status.items())),
        },
        "rows": rows,
    }
    out_path.write_text(json.dumps(payload, indent=1) + "\n")

    n_lanes = 0
    if lanes_path is not None:
        n_lanes = sync_lane_feed(
            db,
            lanes_path,
            payload["built"],
            lanes={
                "populace-reform-validation": {
                    "source": "Populace releases",
                    "area": "reform-validation registry (per-release)",
                    "mode": 2,
                },
            },
        )
    db.close()
    return {
        "rows": len(rows),
        "multi_release_claims": multi_release,
        "lanes_synced": n_lanes,
        "out": str(out_path),
    }


if __name__ == "__main__":
    import sys

    db = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(export(db, lanes_path=REPO / "data" / "lanes.json"), indent=1))
