"""Ingest every pre-publish comparables record (docs/COMPARABLES.md).

Each ``sources/analysis-<country>-<slug>/`` directory records the external
estimates found for one PolicyEngine analysis and the analysis's own
published estimates. This ingest puts them on the scorecard:

- every staged claim the database can hold becomes a claim, held out
  (another producer's estimate of the analysis's world is a comparator,
  never a calibration target: Max, 2026-08-02), with
  ``conditions.analysis`` naming the analysis so its claims are retrievable
  together and never collide with a producer-level source staging the same
  publication;
- every compared claim gets one PolicyEngine result: the analysis's own
  published figure, read from the results file analysis.json pins, with the
  comparison status its annotation gives (``comparable`` when none does);
- a claim with no PolicyEngine counterpart is published without a result,
  and ``conditions.pe_missing`` says why.

Rows the database cannot hold are tallied, not dropped silently: a claim
with a proposed metric or unit (harvest rule 2) waits for its vocabulary
decision, and a restated government figure is dropped under the #86 rule
(the producer did not compute it). Both stay in the directory and in the
published index.

Same contract as every ingest here: the directory is validated first
(scorecard_db/comparables.py), the replacement is one transaction keyed on
``publication.registry``, and an invalid directory fails the build.

    PYTHONPATH=. python -m scorecard_db.ingest_analysis_comparables data/scorecard.db
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from . import comparables as cmp
from .baselines import BASELINES
from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, with_baseline_condition
from .models import (
    CURRENT_LAW_DESCRIPTOR,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
    baseline_key,
)

REGISTRY = "analysis_comparables"
# One mission-control lane per country: the app files a lane under one country.
LANES = {
    "UK": "analysis-comparables-uk",
    "US": "analysis-comparables-us",
}
LANE_FEED_META = {
    lane: {
        "source": "Pre-publish comparables",
        "area": "every external estimate of each PolicyEngine analysis, found before it is published",
        "mode": 2,
        "country": country,
    }
    for country, lane in LANES.items()
}
FIRST_SEARCH_DATE = "2026-10-21"


def _baseline_descriptor(label: str | None) -> dict | None:
    if label is None:
        return None
    for descriptor, registered, *_ in BASELINES:
        if registered == label:
            return None if descriptor == CURRENT_LAW_DESCRIPTOR else descriptor
    raise ValueError(f"baseline {label!r} is not registered")


def _reform(
    record: cmp.AnalysisRecord, world: str, baseline_label: str | None
) -> ReformRef:
    if world == cmp.BASELINE_WORLD:
        return ReformRef()
    policy = record.analysis["worlds"][world]["policy"]
    return policy_ref(policy, baseline=_baseline_descriptor(baseline_label))


def _engine_version(estimate: dict) -> str:
    engine = estimate["provenance"]["engine"]
    return " ".join(f"{name}=={version}" for name, version in sorted(engine.items()))


def stage(root: Path = cmp.SOURCES) -> tuple[list[ExternalScore], list[PEResult], dict]:
    producers, policy = cmp.load_producers(), cmp.load_policy()
    scores: list[ExternalScore] = []
    results: list[PEResult] = []
    tally = {
        country: {
            "analyses": 0,
            "claims": 0,
            "results": 0,
            "not_compared": 0,
            "skipped": {},
        }
        for country in LANES
    }
    for directory in cmp.analysis_dirs(root):
        record = cmp.load_analysis(directory)
        errors = cmp.validate(record, producers, policy)
        if errors:
            raise ValueError(
                f"{directory.name} is not a complete record:\n  " + "\n  ".join(errors)
            )
        a = record.analysis
        if a["country"] not in LANES:
            raise ValueError(
                f"{directory.name}: no mission-control lane for {a['country']}"
            )
        t = tally[a["country"]]
        t["analyses"] += 1
        estimates = {e["key"]: e for e in a["pe_estimates"]}
        evaluation = {row["key"]: row for row in cmp.evaluate(record, policy)}
        notes = {}
        for note in record.annotations:
            for key in note["claims"]:
                notes[key] = note
        for c in record.claims:
            if c["attribution"] == "restated":
                t["skipped"]["restated"] = t["skipped"].get("restated", 0) + 1
                continue
            if c.get("metric") is None or c.get("unit_concept") is None:
                t["skipped"]["proposed_vocabulary"] = (
                    t["skipped"].get("proposed_vocabulary", 0) + 1
                )
                continue
            reform = _reform(record, c["world"], c.get("baseline_policy"))
            conditions = {
                **c["conditions"],
                "analysis": a["id"],
                "analysis_claim": c["key"],
                "benchmark_class": c["benchmark_class"],
                "value_verbatim": c["value_raw"],
            }
            if c["value_kind"] != "point":
                conditions["estimate_kind"] = c["value_kind"]
            with_baseline_condition(conditions, reform)
            if not c.get("compare_to"):
                conditions["pe_missing"] = c["pe_missing"]
            publication = {
                **{
                    k: c["publication"][k]
                    for k in ("title", "url", "date", "publisher", "locator")
                },
                "primary_sha256": c["publication"]["primary_sha256"],
                "table": c["source_table"],
                "quote": c["quote"],
                "registry": REGISTRY,
                "country": a["country"],
                "analysis_url": a["url"],
            }
            if not c.get("compare_to"):
                publication["publish_without_result"] = True
            score = ExternalScore(
                source=c["source"],
                metric=Metric(c["metric"]),
                unit_concept=UnitConcept(c["unit_concept"]),
                period=c["period"],
                time_basis=TimeBasis(c["time_basis"]),
                value=float(c["value"]),
                conditions=conditions,
                reform=reform,
                calibration_relationship="held_out",
                source_model=c.get("source_model"),
                source_column=c["source_column"],
                publication=publication,
                value_kind=c["unit_concept"],
                status="ok",
            )
            scores.append(score)
            t["claims"] += 1
            row = evaluation[c["key"]]
            if not row["estimate"]:
                t["not_compared"] += 1
                continue
            est = estimates[row["estimate"]]
            note = notes.get(c["key"])
            status = row["status"]
            annotations = []
            if note:
                annotations.append(f"{note['id']}: {note['cause']}")
                if status == "pending":
                    # the comparison is like for like; its gap is open on the owner's issue
                    status = ComparisonStatus.COMPARABLE.value
                    annotations.append(
                        f"gap unexplained, tracked at {note['tracking_issue']}"
                    )
            world_baseline = a["worlds"].get(est["world"], {}).get("baseline")
            executed = _baseline_descriptor(world_baseline) or CURRENT_LAW_DESCRIPTOR
            prov = est["provenance"]
            results.append(
                PEResult(
                    claim_id=score.claim_id(),
                    computed_value=float(est["value"]),
                    status=ComparisonStatus(status),
                    engine_version=_engine_version(est),
                    data_bundle=prov["dataset"],
                    pe_construction=json.dumps(
                        {
                            "analysis": a["id"],
                            "estimate": est["key"],
                            "repo": prov["repo"],
                            "commit": prov["commit"],
                            "path": prov["path"],
                            "sha256": prov["sha256"],
                            "field": prov["field"],
                            "relation": row["relation"],
                        },
                        sort_keys=True,
                    ),
                    run_id=f"analysis:{a['id']}@{prov['commit'][:7]}",
                    computed_at=prov["computed_at"],
                    annotations=annotations,
                    baseline_key=baseline_key(executed),
                )
            )
            t["results"] += 1
    return finish(scores, REGISTRY), results, tally


def ingest(db_path: Path) -> dict:
    scores, results, tally = stage()
    db = ScorecardDB(db_path)
    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        existing = [
            r[0]
            for r in db.conn.execute(
                "SELECT claim_id FROM external_scores"
                " WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY,),
            )
        ]
        db.conn.executemany(
            "DELETE FROM pe_results WHERE claim_id = ?", [(c,) for c in existing]
        )
        db.conn.executemany(
            "DELETE FROM external_scores WHERE claim_id = ?", [(c,) for c in existing]
        )
        collisions = [
            s.claim_id()
            for s in scores
            if db.conn.execute(
                "SELECT 1 FROM external_scores WHERE claim_id = ?", (s.claim_id(),)
            ).fetchone()
        ]
        if collisions:
            raise ValueError(
                f"analysis claims collide with existing claims: {collisions[:3]}"
            )
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in results])
        register_baselines_txn(db)
        updated = max(
            (
                s["date"]
                for d in cmp.analysis_dirs()
                for s in cmp.load_analysis(d).search_log.get("searches", [])
            ),
            default=FIRST_SEARCH_DATE,
        )
        for country, lane in LANES.items():
            t = tally[country]
            stage_name = (
                "computed"
                if t["results"]
                else ("ingested" if t["claims"] else "registered")
            )
            detail = (
                f"{t['analyses']} analyses searched, {t['claims']} claims, "
                f"{t['results']} compared with the analysis's own estimate"
            )
            db.conn.execute(LANE_SQL, (lane, stage_name, detail, updated))
    sync_lane_feed(db, REPO / "data" / "lanes.json", updated, lanes=LANE_FEED_META)
    db.close()
    return tally


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
