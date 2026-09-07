"""Resolve the archived UK campaign staging against the ingested UK claims.

The 2026-08-02 compute campaign staged five UK families before any UK
claims existed in the DB; the archive is frozen under
sources/campaign-20260802/uk (PR #70). Measured against the ingested
vocabulary (PR #48) the archived descriptors under-specify — the
adjudication's finding: two personal-allowance reckoner rows share
identical descriptor conditions, and the descriptor periods key the PE
calendar year, not the claim convention (FY END year). This producer
DERIVES a resolved staging deterministically instead of loosening the
match contract:

    archive row.pe_construction (its " | " prefix, an exact string)
      -> uk_runs/<key>_2026.json pe_construction   (the executed run)
      -> t2_collation.csv hmrc_hint            (HMRC's verbatim change
                                                 label for that run)
      -> exactly ONE ingested claim: source uk_hmrc, metric
         revenue_change, conditions.option == hint, conditions.fy ==
         the archived row's fy                            [fail-loud]
      -> {"claim_id": ...} (ingest_campaign's strict direct form)

Every step is a closed lookup that raises on 0 or 2+ — a drifted
archive, collation, or claim re-ingest fails loudly, never mis-joins.

Family disposition (this module's summary reports it; the per-row
compositions below are pinned in tests so a re-frozen archive cannot
silently outgrow its stated reason):
    hmrc_reckoner_t2   RESOLVED (14 rows) -> uk_resolved/
    free_joins         NOT RESOLVED (16 rows = 7 obr revenue_level +
        7 uk_dwp benefit_cost + 2 metaless exhibits): the OBR rows
        target EFO receipts forecast lines and the uk_dwp rows DWP
        benefit-expenditure forecast lines — NEITHER is staged as
        claims, and pe-uk-data consumes both publication families as
        calibration surfaces, so staging them is relationship-evidence
        work (two source lanes), never a quick join
    obr_measures       NOT RESOLVED (10 rows = 9 obr revenue_change
        fiscal-event costings + 1 metaless exhibit): targets the OBR
        policy-measures costings database (long-tail source, held on
        the DB-storage decision)
    two_child          NOT RESOLVED (4 rows = 2 resolution_foundation
        + 1 ukmod poverty_count_change + 1 metaless exhibit). RF is no
        longer a long-tail source — #86 ingested 58 RF claims — so the
        reason is now precise rather than categorical:
          * the poverty_count_change row's descriptor is under-specified
            against the ingested vocabulary (unit_population "children"
            with no income_concept or poverty_line), the same
            under-specification #48 forced the reckoner rows through the
            derivation below;
          * the reform_fiscal_cost row targets a claim #86 DELIBERATELY
            DROPS — it is an HM Treasury scorecard figure that RF
            re-publishes, so there is no RF claim to attach to and there
            should not be;
          * the ukmod row targets a REFORM claim and the staged UKMOD
            family is baseline validation statistics only.
    uprating_april2026 NOT RESOLVED (4 rows = 3 resolution_foundation
        benefit_uprating_pct + 1 metaless exhibit). Also no longer "RF
        long-tail, held": the claims exist, but the archived descriptors
        speak the HARVEST's proposal vocabulary (metric
        "benefit_uprating_pct", benefit named in verbatim prose such as
        "UC standard allowance, under-25s") while the ingested claims
        speak the DECIDED vocabulary (metric benefit_uprating_rate,
        benefit universal_credit_standard_allowance_under_25). Resolving
        them means deriving the mapping the way the reckoner family is
        derived below — a deliberate act, not a looser match.

The metaless exhibits (5 rows across the families — the free_joins
pair is one construction duplicated) carry exhibit_context but no
exhibit_meta; ingest_campaign would only ever defer them, so they
block with their families rather than shipping as noise.

Usage:
    PYTHONPATH=. python -m scorecard_db.produce_campaign_uk
    PYTHONPATH=. python -m scorecard_db.ingest_campaign \
        data/scorecard.db sources/campaign-20260802/uk_resolved
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import REPO

CAMPAIGN = REPO / "sources" / "campaign-20260802"
ARCHIVE = CAMPAIGN / "uk"
RUNS = CAMPAIGN / "uk_runs"
RESOLVED = CAMPAIGN / "uk_resolved"

# Archived families this producer deliberately does NOT resolve, with
# the reason a future lane must clear first. Every archive family must
# appear either here or in the resolve/copy sets — a new family in the
# archive fails loudly rather than being silently skipped.
BLOCKED = {
    "free_joins": (
        "16 rows = 7 obr revenue_level (EFO receipts forecast lines) + "
        "7 uk_dwp benefit_cost (DWP benefit-expenditure forecast "
        "lines) + 2 metaless exhibits; neither publication family is "
        "staged as claims, and pe-uk-data consumes both as calibration "
        "surfaces — staging needs the relationship evidence read at "
        "the pin (two source lanes)"
    ),
    "obr_measures": (
        "10 rows = 9 obr revenue_change fiscal-event costings + 1 "
        "metaless exhibit; targets the OBR policy-measures costings "
        "database — long-tail source held on the DB-storage decision"
    ),
    # RF is NO LONGER a long-tail held source — #86 ingested 58 RF
    # claims — so these two reasons are precise rather than categorical.
    # This is the value a caller actually sees, so it carries the real
    # reason and not just the module docstring.
    "two_child": (
        "4 rows = 2 resolution_foundation + 1 ukmod "
        "poverty_count_change + 1 metaless exhibit. RF claims now exist "
        "(#86), so: the RF poverty_count_change descriptor is "
        "under-specified against the ingested vocabulary "
        "(unit_population 'children' with no income_concept or "
        "poverty_line); the RF reform_fiscal_cost row targets a claim "
        "#86 deliberately DROPS (an HM Treasury scorecard figure RF "
        "re-publishes), so there is no RF claim to attach to and there "
        "should not be; and the ukmod row targets a REFORM claim while "
        "the staged UKMOD family is baseline statistics only"
    ),
    "uprating_april2026": (
        "4 rows = 3 resolution_foundation benefit_uprating_pct + 1 "
        "metaless exhibit. RF claims now exist (#86), but the archived "
        "descriptors speak the HARVEST's proposal vocabulary (metric "
        "'benefit_uprating_pct', benefit in verbatim prose such as 'UC "
        "standard allowance, under-25s') while the ingested claims "
        "speak the DECIDED vocabulary (metric benefit_uprating_rate, "
        "benefit universal_credit_standard_allowance_under_25). "
        "Resolving them means deriving that mapping the way the "
        "reckoner family is derived, not loosening the match"
    ),
}
RESOLVED_FAMILIES = {"hmrc_reckoner_t2"}


def _runs_by_construction() -> dict[str, str]:
    """pe_construction -> reform_key over the archived executed runs."""
    out: dict[str, str] = {}
    for f in sorted(RUNS.glob("*_2026.json")):
        d = json.loads(f.read_text())
        if isinstance(d, dict) and "pe_construction" in d and "reform_key" in d:
            if d["pe_construction"] in out:
                raise ValueError(
                    f"two runs share a construction: {d['pe_construction']!r}"
                )
            out[d["pe_construction"]] = d["reform_key"]
    if not out:
        raise FileNotFoundError(f"no run files under {RUNS}")
    return out


def _hints_by_key() -> dict[str, str]:
    """reform_key -> HMRC's verbatim change label (t2 collation)."""
    with open(RUNS / "t2_collation.csv") as f:
        rows = list(csv.DictReader(f))
    out = {r["key"]: r["hmrc_hint"] for r in rows}
    if len(out) != len(rows):
        raise ValueError("t2_collation.csv has duplicate keys")
    return out


def _resolve_reckoner(db: ScorecardDB, rows: list[dict]) -> list[dict]:
    constructions = _runs_by_construction()
    hints = _hints_by_key()
    resolved = []
    for row in rows:
        prefix = row["pe_construction"].split(" | ")[0]
        if prefix not in constructions:
            raise ValueError(
                f"hmrc_reckoner_t2: construction {prefix!r} matches no archived run"
            )
        key = constructions[prefix]
        if key not in hints:
            raise ValueError(f"hmrc_reckoner_t2: run {key!r} not in t2 collation")
        option = hints[key]
        fy = row["external_claim_match"]["conditions"]["fy"]
        hits = [
            r[0]
            for r in db.conn.execute(
                "SELECT claim_id FROM external_scores"
                " WHERE source='uk_hmrc' AND metric='revenue_change'"
                " AND json_extract(conditions, '$.option') = ?"
                " AND json_extract(conditions, '$.fy') = ?",
                (option, fy),
            )
        ]
        if len(hits) != 1:
            raise ValueError(
                f"hmrc_reckoner_t2: {len(hits)} claims for option "
                f"{option!r} fy {fy!r} — need exactly one"
            )
        out = dict(row)
        out["external_claim_match"] = {"claim_id": hits[0]}
        resolved.append(out)
    if len({r["external_claim_match"]["claim_id"] for r in resolved}) != len(resolved):
        raise ValueError("hmrc_reckoner_t2: two rows resolved to one claim")
    return resolved


def produce(db_path: Path, out_dir: Path | None = None) -> dict:
    """Write the resolved staging; returns the disposition summary."""
    out_dir = out_dir or RESOLVED
    db = ScorecardDB(db_path)
    families = {p.stem: p for p in sorted(ARCHIVE.glob("*.jsonl"))}
    unaccounted = (set(families) - set(BLOCKED) - RESOLVED_FAMILIES) | (
        RESOLVED_FAMILIES - set(families)
    )
    if unaccounted:
        raise ValueError(
            f"archive families without a disposition: {sorted(unaccounted)}"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: dict = {"resolved": {}, "blocked": BLOCKED}
    for name, path in families.items():
        rows = [
            json.loads(line) for line in path.read_text().splitlines() if line.strip()
        ]
        if name in BLOCKED:
            continue
        resolved = _resolve_reckoner(db, rows)
        (out_dir / path.name).write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in resolved) + "\n"
        )
        summary["resolved"][name] = len(resolved)
    db.close()
    return summary


if __name__ == "__main__":
    import sys

    db = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(produce(db), indent=1))
