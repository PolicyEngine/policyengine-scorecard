"""Attach the compute campaign's day-1 PE results to their harvest claims.

The campaign session (2026-08-02, CAMPAIGN.md driver) computed 120+
comparisons and staged them as per-family JSONL under
``sources/campaign-20260802/`` — each row carries full provenance
(engine_version, the certified data_bundle actually executed, computed_at,
run_id ``campaign-20260802-<family>``) and an ``external_claim_match``
descriptor naming the harvested claim it compares against — either a
family-vocabulary descriptor (translated below) or, for claims already in
the DB (the Urban subgroup joins), the claim_id directly.

US families attach here. The UK families (free_joins, hmrc_reckoner_t2,
obr_measures, uprating_april2026, two_child) are vendored alongside but
NOT ingested: their claims live in the UK harvest, which has no DB ingest
yet — they attach when it lands, and this module fails loudly if pointed
at them early.

Match contract: descriptors were verified by the campaign against the
harvest STAGING files; the DB's per-source adapters normalized vocabulary
on ingest, so each family gets a small translator here mapping the
descriptor onto the DB's ingested shape — conditions must match EXACTLY
(canonical JSON equality, not subset: CBO's SSI rows differ only by the
presence of a ``component`` key) and, where the scenario rides on the
reform (CPSP's CTC worlds), a reform predicate joins the match. Exactly
one claim must match; 0 or >1 aborts the run with nothing written.

Exhibit rows (``exhibit: true`` — derived pair-differences with no single
external claim, e.g. TPC marginal-band increments) route to pe_exhibits
when they carry ``exhibit_meta`` (the metric/period/reform identity the
table requires; the campaign emits it via stage_emit.py). The four TPC
increments are the top-tail/cap-binding localization evidence: band
increments at 0.93-0.99 parity while levels diverge. A row WITHOUT
exhibit_meta is deferred — tallied and listed in the summary for the
campaign to re-emit, never silently dropped, never guessed.

Input-override exhibit rows use the strict alternate ``reform_ref`` route
instead of ``external_claim_match``. The descriptor must be a
``policyengine_us_inputs`` ReformRef; its canonical key/JSON are stored on
the exhibit, while ``exhibit_context`` supplies conditions and the indexed
geography/program fields. This keeps take-up-flag counterfactuals executable
and distinct from the legacy ``policy_ref`` exhibit descriptors above.

Idempotent: this module replaces exactly the run_ids present in the
staged files it is ingesting — never a prefix sweep, so re-running the US
directory can't erase results another campaign directory (UK) ingested
under its own run_ids. It creates no claims, so nothing else is touched.
All parsing and matching happens before the single write transaction.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import EXHIBITS_SQL, RESULTS_SQL, ScorecardDB
from .models import ComparisonStatus, PEResult, ReformRef

REPO = Path(__file__).resolve().parent.parent
STAGED_US = REPO / "sources" / "campaign-20260802" / "us"

# CPSP's CTC-brief scenario worlds live on the claim's policy_ref reform
# (ingest_cpsp), not in conditions — descriptor policy_scenario -> policy.
_CPSP_WORLDS = {
    "TCJA CTC": "tcja_ctc",
    "No CTC": "no_ctc",
    "OBBBA CTC": "obbba_ctc",
    "AFA CTC": "afa_ctc",
}

# TPC T25-0209 option legs carry the score's stated baseline on the claim.
_TPC_T25_BASELINE = "current_law_plus_senate_obbba_title_vii"

# CBO's refundable-credit outlay rows carry an ingest-side variant key the
# campaign's descriptor (built from the staging file) predates.
_CBO_OUTLAY_VARIANT = "outlay_portion_of_refundable_credits"


def _normalize(family: str, match: dict) -> tuple[dict, str | None]:
    """(exact DB conditions, reform-policy predicate or None) for a
    campaign descriptor. Every translation here mirrors a documented
    choice in the per-source harvest adapter."""
    cond = dict(match.get("conditions", {}))
    geo = cond.get("geography")
    if geo:
        cond["geography"] = geo.upper()
    else:
        cond["geography"] = "US"
    reform_policy = None
    if family == "cpsp":
        scenario = cond.pop("policy_scenario")
        reform_policy = _CPSP_WORLDS[scenario]
    elif family == "tpc":
        cond["provision"] = cond.pop("provision_row")
        if "option" in cond:
            cond["baseline_policy"] = _TPC_T25_BASELINE
    elif family == "jct":
        cond.pop("baseline", None)
        cond["row_kind"] = "provision"
    elif family == "cbo":
        # The staging file's free-text "note" became the ingest's "variant"
        # key on outlay rows.
        if "note" in cond:
            cond["variant"] = cond.pop("note")
        elif cond.get("component") == "outlays":
            cond["variant"] = _CBO_OUTLAY_VARIANT
    elif family == "pwbm":
        pass
    else:
        raise ValueError(f"no normalizer for family {family!r}")
    return cond, reform_policy


def _find_claim(db: ScorecardDB, family: str, match: dict) -> str:
    # Direct key: rows against claims already in the DB (the Urban
    # subgroup joins) name the claim_id itself — no descriptor
    # resolution, just a fail-loud existence check. The form is strict:
    # a match carrying claim_id AND descriptor fields would let the two
    # contradict silently, so it is rejected.
    if "claim_id" in match:
        if set(match) != {"claim_id"}:
            raise ValueError(
                f"{family}: claim_id-direct match must be exactly"
                f" {{'claim_id'}}, got {sorted(match)}"
            )
        cid = match["claim_id"]
        row = db.conn.execute(
            "SELECT 1 FROM external_scores WHERE claim_id = ?", (cid,)
        ).fetchone()
        if row is None:
            raise ValueError(f"{family}: claim_id {cid!r} not in the DB")
        return cid
    cond, reform_policy = _normalize(family, match)
    q = (
        "SELECT claim_id FROM external_scores"
        " WHERE source = ? AND metric = ? AND period = ? AND conditions = ?"
    )
    args: list = [
        match["source"],
        match["metric"],
        match["period"],
        json.dumps(cond, sort_keys=True),
    ]
    if reform_policy is not None:
        q += " AND json_extract(reform_json, '$.reform.policy') = ?"
        args.append(reform_policy)
    hits = [r[0] for r in db.conn.execute(q, args)]
    if len(hits) != 1:
        raise ValueError(
            f"{family}: {len(hits)} claims match {json.dumps(cond)}"
            f" (reform={reform_policy}) — need exactly one"
        )
    return hits[0]


def ingest(db_path: Path, staged_dir: Path | None = None) -> dict:
    staged_dir = staged_dir or STAGED_US
    db = ScorecardDB(db_path)
    files = sorted(staged_dir.glob("*.jsonl"))
    if not files:
        raise SystemExit(f"no staged families in {staged_dir}")

    results: list[PEResult] = []
    exhibits: list[dict] = []
    deferred_exhibits: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    families: dict[str, int] = {}
    staged_run_ids: set[str] = set()
    for path in files:
        family = path.stem.split("_")[0]
        for line in path.read_text().splitlines():
            row = json.loads(line)
            # Every staged row's run_id is a deletion key — including
            # deferred exhibits, so a row that LOSES its exhibit_meta
            # between runs can't leave its stale pe_exhibits row behind.
            staged_run_ids.add(row["run_id"])
            if "reform_ref" in row:
                if "external_claim_match" in row:
                    raise ValueError(
                        f"{path.stem}: reform_ref and external_claim_match "
                        "are mutually exclusive"
                    )
                meta = row.get("exhibit_meta")
                if not isinstance(meta, dict):
                    raise ValueError(
                        f"{path.stem}: reform_ref route requires exhibit_meta"
                    )
                raw_reform = row["reform_ref"]
                if not isinstance(raw_reform, dict):
                    raise ValueError(f"{path.stem}: reform_ref must be an object")
                reform = ReformRef(**raw_reform)
                if reform.framework != "policyengine_us_inputs":
                    raise ValueError(
                        f"{path.stem}: reform_ref route requires "
                        "framework='policyengine_us_inputs'"
                    )
                if "reform_key" in meta and meta["reform_key"] != reform.key():
                    raise ValueError(
                        f"{path.stem}: exhibit_meta reform_key does not match "
                        "reform_ref"
                    )
                conditions = row.get("exhibit_context", {})
                if not isinstance(conditions, dict):
                    raise ValueError(f"{path.stem}: exhibit_context must be an object")
                note = " | ".join(
                    [meta["note"], row["pe_construction"]] + row.get("annotations", [])
                )
                exhibits.append(
                    {
                        "exhibit": f"campaign:{path.stem}",
                        "reform_key": reform.key(),
                        "reform_json": reform.to_json(),
                        "metric": meta["metric"],
                        "unit_concept": meta["unit_concept"],
                        "period": meta["period"],
                        "time_basis": meta["time_basis"],
                        "conditions": conditions,
                        "geography": conditions.get("geography"),
                        "program": conditions.get("program"),
                        "value": row["pe_value"],
                        "baseline_value": row.get("baseline_value"),
                        "delta": row.get("delta"),
                        "engine_version": row["engine_version"],
                        "data_bundle": row["data_bundle"],
                        "run_id": row["run_id"],
                        "computed_at": row["computed_at"],
                        "note": note,
                    }
                )
                continue
            if row.get("exhibit"):
                meta = row.get("exhibit_meta")
                if meta is None:
                    deferred_exhibits.append(
                        f"{path.stem}: {row.get('pe_construction', '')[:60]}"
                    )
                    continue
                # PE-only content (a derived pair-difference has no single
                # external claim); the external twin stays in the note.
                note = " | ".join(
                    [meta["note"], row["pe_construction"]] + row.get("annotations", [])
                )
                exhibits.append(
                    {
                        "exhibit": f"campaign:{path.stem}",
                        "reform_key": meta["reform_key"],
                        "reform_json": json.dumps(
                            {
                                "framework": "policy_ref",
                                "reform": {"policy": meta["reform_key"]},
                            },
                            sort_keys=True,
                        ),
                        "metric": meta["metric"],
                        "unit_concept": meta["unit_concept"],
                        "period": meta["period"],
                        "time_basis": meta["time_basis"],
                        "conditions": row.get("exhibit_context", {}),
                        "geography": "US",
                        "value": row["pe_value"],
                        "engine_version": row["engine_version"],
                        "data_bundle": row["data_bundle"],
                        "run_id": row["run_id"],
                        "computed_at": row["computed_at"],
                        "note": note,
                    }
                )
                continue
            cid = _find_claim(db, family, row["external_claim_match"])
            key = (cid, row["data_bundle"], row["run_id"])
            if key in seen:
                raise ValueError(f"duplicate campaign result: {key}")
            seen.add(key)
            families[path.stem] = families.get(path.stem, 0) + 1
            results.append(
                PEResult(
                    claim_id=cid,
                    computed_value=row["pe_value"],
                    status=ComparisonStatus(row["status"]),
                    engine_version=row["engine_version"],
                    data_bundle=row["data_bundle"],
                    pe_construction=row["pe_construction"],
                    run_id=row["run_id"],
                    computed_at=row["computed_at"],
                    annotations=row.get("annotations", []),
                )
            )

    # All parsing and matching done — one transaction, commit or nothing.
    # Deletion is scoped to the exact run_ids being re-ingested, never the
    # campaign- prefix: other staged directories' results must survive.
    result_rows = [ScorecardDB.result_row(r) for r in results]
    exhibit_rows = [ScorecardDB.exhibit_row(e) for e in exhibits]
    run_ids = sorted(staged_run_ids)
    placeholders = ",".join("?" * len(run_ids))
    with db.conn:
        db.conn.execute(
            f"DELETE FROM pe_results WHERE run_id IN ({placeholders})",
            run_ids,
        )
        db.conn.execute(
            f"DELETE FROM pe_exhibits WHERE run_id IN ({placeholders})",
            run_ids,
        )
        db.conn.executemany(RESULTS_SQL, result_rows)
        db.conn.executemany(EXHIBITS_SQL, exhibit_rows)
    db.close()
    return {
        "attached": len(result_rows),
        "exhibits": len(exhibit_rows),
        "families": families,
        "exhibits_deferred": deferred_exhibits,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    staged = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    print(json.dumps(ingest(out, staged_dir=staged), indent=1))
