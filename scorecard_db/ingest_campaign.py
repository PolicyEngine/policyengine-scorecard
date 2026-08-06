"""Attach the compute campaign's day-1 PE results to their harvest claims.

The campaign session (2026-08-02, CAMPAIGN.md driver) computed 120+
comparisons and staged them as per-family JSONL under
``sources/campaign-20260802/`` — each row carries full provenance
(engine_version, the certified data_bundle actually executed, computed_at,
run_id ``campaign-20260802-<family>``) and an ``external_claim_match``
descriptor naming the harvested claim it compares against.

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
external claim, e.g. TPC marginal-band increments) are DEFERRED: they
lack the metric/period/reform identity pe_exhibits requires, so they are
tallied and listed in the summary for the campaign to re-emit with
``exhibit_meta`` — never silently dropped, never guessed.

Idempotent: this module's results are replaced wholesale by run_id prefix
``campaign-``. It creates no claims, so nothing else is touched. All
parsing and matching happens before the single write transaction.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import RESULTS_SQL, ScorecardDB
from .models import ComparisonStatus, PEResult

REPO = Path(__file__).resolve().parent.parent
STAGED_US = REPO / "sources" / "campaign-20260802" / "us"
RUN_PREFIX = "campaign-"

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
    deferred_exhibits: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    families: dict[str, int] = {}
    for path in files:
        family = path.stem.split("_")[0]
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row.get("exhibit"):
                deferred_exhibits.append(
                    f"{path.stem}: {row.get('pe_construction', '')[:60]}"
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
    result_rows = [ScorecardDB.result_row(r) for r in results]
    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE run_id LIKE ?", (f"{RUN_PREFIX}%",)
        )
        db.conn.executemany(RESULTS_SQL, result_rows)
    db.close()
    return {
        "attached": len(result_rows),
        "families": families,
        "exhibits_deferred": deferred_exhibits,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
