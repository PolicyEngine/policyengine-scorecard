"""Export DB-backed populations for the app -> data/populations.json.

The Urban SotSN population reaches the app through the file-based
pipeline/build_comparison.py export (data/comparison.json). Everything
else lives only in scorecard.db: the reform-validation registry (issue
#20, its 205 minted claims plus the 36 harvested JCX-35-25 provision
claims its OBBBA results attach to), the US campaign attaches, and —
since the campaign-UK producer — the 14 uk_hmrc reckoner claims with
campaign results; and Belgium's honest concept-mismatch Axiom attachments
to JRC EUROMOD-BE claims. This module exports every non-Urban claim that has at
least one pe_result, carrying the dimension the Urban export doesn't
have: the full per-release result history (one row per certified
release, engine pins and OBBBA scoring mode in the construction), plus the
Belgian PIT-reform scorekeeper rows, so
cross-release drift is visible.

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

from .db import CURRENT_LAW_KEY, ScorecardDB, require_complete_provenance
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
    "microcosm_be_v02",
    "microcosm_be_v05h",
)


def release_label(bundle: str) -> str:
    """Short human label for a data-bundle id ("buildo", "l0-refit")."""
    for token in _RELEASE_TOKEN:
        if token in bundle:
            return token
    return bundle.rsplit("-", 1)[0][-12:]


def _effective_status(status: str, result_bk: str | None, claim_bk: str | None) -> str:
    """Mirror of the comparisons-view #13 guard, applied per result so
    the exported feed can never publish plain agreement across baseline
    worlds (or over unverifiable legacy provenance)."""
    if status != "comparable" or claim_bk is None:
        return status
    if result_bk is not None and result_bk != claim_bk:
        return "constructed"
    if result_bk is None and claim_bk != CURRENT_LAW_KEY:
        return "baseline_unvalidated"
    return status


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
    try:
        require_complete_provenance(db.conn, context="export_populations")
    except BaseException:
        db.close()
        raise
    claims = db.conn.execute(
        """SELECT s.*, p.publication AS publication,
                  rf.reform_json AS reform_json,
                  d.diagnosis_class, d.rationale, d.action_link
           FROM external_scores s
           JOIN publications p USING (publication_id)
           JOIN reforms rf USING (reform_key)
           LEFT JOIN diagnoses d USING (claim_id)
           WHERE s.source != ?
             AND EXISTS (SELECT 1 FROM pe_results r
                         WHERE r.claim_id = s.claim_id)
           ORDER BY s.source, s.metric, s.period, s.source_column,
                    s.claim_id""",
        (URBAN_SOURCE,),
    ).fetchall()

    labels = {
        r["baseline_key"]: r["label"]
        for r in db.conn.execute("SELECT baseline_key, label FROM baselines")
    }
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
                "baseline": labels.get(r["baseline_key"]),
                "status_effective": _effective_status(
                    r["status"], r["baseline_key"], c["baseline_key"]
                ),
            }
            for r in db.conn.execute(
                """SELECT computed_value, status, engine_version,
                          data_bundle, pe_construction, computed_at,
                          annotations, baseline_key
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
        eff = latest["status_effective"]
        by_status[eff] = by_status.get(eff, 0) + 1
        rows.append(
            {
                "claim_id": c["claim_id"],
                "source": c["source"],
                # the model instance the claim belongs to (issue #42): UK
                # claims carry conditions["country"]; its absence IS the
                # US claim-side convention, mirrored by the app's
                # countryOf() default — emit it explicitly so the feed
                # never relies on the default for non-US rows
                "country": conditions.get("country", "US"),
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
                "claim_baseline": labels.get(c["baseline_key"]),
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
            " campaign's attached comparisons (US: TPC/CPSP/PWBM/CBO/JCT;"
            " UK: the HMRC ready-reckoner family; BE: JRC EUROMOD-BE claims"
            " with demo-grade Axiom concept-mismatch attachments and the"
            " 2026 PIT-reform scorekeeper claims)."
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
                    "country": "US",
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
