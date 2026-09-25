"""Ingest New Zealand official Budget reform-score candidates.

The first tranche contains two separable Vote Revenue (IRD–Crown) operating
costings: Budget 2026's temporary in-work tax credit increase and Budget 2025's
Working for Families abatement changes. Source NZD millions are normalized to
raw NZD. Every claim is held out and intentionally has no model result yet.

Usage:
    PYTHONPATH=. python -m nz.ingest_official_budget_scores data/scorecard.db
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from scorecard_db.baselines import register_baselines_txn
from scorecard_db.db import LANE_SQL, SCORES_SQL, ScorecardDB
from scorecard_db.harvest import REPO, finish
from scorecard_db.ingest_harvest import sync_lane_feed
from scorecard_db.models import (
    BenchmarkClass,
    CalibrationRelationship,
    ExternalScore,
    Metric,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

SOURCE_DIR = REPO / "sources" / "nz-official-budget-scores"
CLAIMS_PATH = SOURCE_DIR / "claims.json"
MANIFEST_PATH = SOURCE_DIR / "manifest.jsonl"
NOTES_PATH = SOURCE_DIR / "NOTES.md"
SOURCE_PAGES_PATH = SOURCE_DIR / "source-pages.txt"

CLAIMS_SHA256 = "14f534b15e3ecd52b418118c3349b79d71132a2b9ce780d9f9cc1e84e0f44e6c"
MANIFEST_SHA256 = "1618333cc05a224532b71efda3fa45e394065ab55c6421a90c45aa3a1eb0108c"
NOTES_SHA256 = "284cdc91834070b7fd63191f29596c26823f8f079dac13faafd0bdca68047788"
SOURCE_PAGES_SHA256 = "2dcc238c4797c8f1990f5dafea06d645834e8a88a41bd79e050d5eeaae49f4a6"

REGISTRY_MARK = "nz_official_budget_scores"
LANE_ID = "nz-official-budget-scores"
UPDATED = "2026-08-29"
RULESPEC_NZ_COMMIT = "a17f1adc84b3fb23210d91e408e72ae6c37af6a3"
RULESPEC_MODULE = "nz/statutes/income_tax/family_scheme/tax_credits.yaml"

_TOP_LEVEL_FIELDS = {"schema_version", "registry", "claims"}
_ANNUAL_FIELDS = {
    "id",
    "reform_policy",
    "fiscal_event",
    "measure",
    "fy",
    "period",
    "value_nzd_millions",
    "source_display",
    "source_pin",
}
_TOTAL_FIELDS = (_ANNUAL_FIELDS - {"fy"}) | {
    "period_start",
    "period_end",
    "window",
}
_MANIFEST_FIELDS = {
    "id",
    "document",
    "publisher",
    "date",
    "url",
    "sha256",
    "artifact",
    "stored_in_repo",
    "role",
    "printed_page",
    "pdf_page",
    "derived_from",
}
_MANIFEST_REQUIRED = {
    "id",
    "document",
    "publisher",
    "date",
    "sha256",
    "artifact",
    "stored_in_repo",
    "role",
}

_MEASURES = {
    "nz_budget_2026_temporary_iwtc_increase": {
        "event": "budget_2026",
        "measure": (
            "Increase to the In-Work Tax Credit in Response to the Conflict "
            "in the Middle East"
        ),
        "pin": "budget_2026_summary_pdf",
        "id_prefix": "budget_2026_iwtc",
        "years": (
            ("2025-26", 2026, 79.0, "79.000"),
            ("2026-27", 2027, 264.0, "264.000"),
            ("2027-28", 2028, 30.0, "30.000"),
            ("2028-29", 2029, 0.0, "-"),
            ("2029-30", 2030, 0.0, "-"),
        ),
        "total": (2026, 2030, 373.0, "373.000"),
        "window": "FY2025-26 to FY2029-30 operating total",
        "change": "iwtc_base_annual_amount_5070_to_7670_for_2026_27_tax_year",
        "effective_from": "2026-04-01",
        "maximum_effective_to": "2027-03-31",
        "termination_condition": (
            "91_petrol_below_nzd_3_per_litre_for_four_consecutive_weeks"
        ),
        "rules": ("in_work_tax_credit_base_annual_amount",),
        "supporting_pins": (),
    },
    "nz_budget_2025_wff_abatement_changes": {
        "event": "budget_2025",
        "measure": "Working for Families – Abatement Changes",
        "pin": "budget_2025_summary_pdf",
        "id_prefix": "budget_2025_wff_abatement",
        "years": (
            ("2024-25", 2025, 0.0, "-"),
            ("2025-26", 2026, 15.0, "15.000"),
            ("2026-27", 2027, 63.0, "63.000"),
            ("2027-28", 2028, 64.0, "64.000"),
            ("2028-29", 2029, 63.0, "63.000"),
        ),
        "total": (2025, 2029, 205.0, "205.000"),
        "window": "FY2024-25 to FY2028-29 operating total",
        "change": "wff_abatement_threshold_42700_to_44900_and_rate_0.27_to_0.275",
        # The pinned Vote Revenue passage says only "from April 2026".
        # Preserve that source precision instead of inferring a day.
        "effective_month": "2026-04",
        "rules": (
            "wff_family_credit_abatement_threshold",
            "wff_family_credit_abatement_rate",
        ),
        "supporting_pins": (
            "budget_2025_fiscal_recommendation_pdf",
            "budget_2025_vote_revenue_estimates_pdf",
        ),
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_hash(path: Path, expected: str, label: str) -> None:
    actual = _sha256(path)
    if actual != expected:
        raise ValueError(f"{label} SHA-256 drifted: {actual} != {expected}")


def _fy_end(label: str) -> int:
    match = re.fullmatch(r"(\d{4})-(\d{2})", label)
    if not match:
        raise ValueError(f"NZ Budget score: malformed fiscal year {label!r}")
    start = int(match.group(1))
    if (start + 1) % 100 != int(match.group(2)):
        raise ValueError(f"NZ Budget score: fiscal year suffix drifted: {label!r}")
    return start + 1


def load_manifest(
    path: Path = MANIFEST_PATH, *, verify_sha: bool = True
) -> dict[str, dict]:
    if verify_sha:
        _require_hash(path, MANIFEST_SHA256, "manifest")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    manifest: dict[str, dict] = {}
    for row in rows:
        unknown = set(row) - _MANIFEST_FIELDS
        missing = _MANIFEST_REQUIRED - set(row)
        if unknown or missing:
            raise ValueError(
                f"NZ Budget manifest schema drift: unknown={sorted(unknown)}, "
                f"missing={sorted(missing)}"
            )
        if type(row["stored_in_repo"]) is not bool:
            raise ValueError("stored_in_repo must be true or false")
        if row["id"] in manifest:
            raise ValueError(f"duplicate manifest id: {row['id']}")
        if row["stored_in_repo"]:
            artifact = SOURCE_DIR / row["artifact"]
            if not artifact.exists() or _sha256(artifact) != row["sha256"]:
                raise ValueError(f"vendored artifact missing or drifted: {artifact}")
        manifest[row["id"]] = row
    expected = {
        "budget_2026_summary_pdf",
        "budget_2025_summary_pdf",
        "budget_2025_fiscal_recommendation_pdf",
        "budget_2025_vote_revenue_estimates_pdf",
        "source_page_excerpt",
    }
    if set(manifest) != expected:
        raise ValueError(
            f"NZ Budget manifest census drifted: {sorted(manifest)} != "
            f"{sorted(expected)}"
        )
    return manifest


def _source_table_values() -> tuple[tuple[float, ...], tuple[float, ...]]:
    lines = [
        line
        for line in SOURCE_PAGES_PATH.read_text().splitlines()
        if line.startswith("Revenue (IRD–Crown)")
    ]
    if len(lines) != 2:
        raise ValueError(f"expected two source score-table rows, found {len(lines)}")

    def values(line: str) -> tuple[float, ...]:
        tokens = line.split(")", 1)[1].split()
        if len(tokens) != 7:
            raise ValueError(f"source score-table row has {len(tokens)} cells: {line}")
        if tokens[-1] != "-":
            raise ValueError(
                "NZ Budget source table has a nonzero Capital Total; "
                "the operating-score adapter must not discard it"
            )
        return tuple(0.0 if token == "-" else float(token) for token in tokens[:6])

    return values(lines[0]), values(lines[1])


def _validate_payload(payload: dict, manifest: dict[str, dict]) -> None:
    if set(payload) != _TOP_LEVEL_FIELDS:
        raise ValueError(f"NZ Budget top-level schema drifted: {sorted(payload)}")
    if payload["schema_version"] != 1 or payload["registry"] != REGISTRY_MARK:
        raise ValueError("NZ Budget schema version or registry marker drifted")
    rows = payload["claims"]
    if not isinstance(rows, list) or len(rows) != 12:
        raise ValueError("NZ Budget claim census must contain exactly 12 claims")

    by_policy: dict[str, list[dict]] = {}
    seen: set[str] = set()
    for row in rows:
        fields = _TOTAL_FIELDS if "period_start" in row else _ANNUAL_FIELDS
        if set(row) != fields:
            raise ValueError(
                f"NZ Budget claim schema drift for {row.get('id')}: "
                f"{sorted(set(row) ^ fields)}"
            )
        if row["id"] in seen:
            raise ValueError(f"duplicate NZ Budget claim id: {row['id']}")
        seen.add(row["id"])
        if row["reform_policy"] not in _MEASURES:
            raise ValueError(f"unknown NZ Budget reform: {row['reform_policy']}")
        if row["source_pin"] not in manifest:
            raise ValueError(f"unknown source pin: {row['source_pin']}")
        value = row["value_nzd_millions"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"non-numeric NZ Budget score: {value!r}")
        if not math.isfinite(value):
            raise ValueError(f"non-finite NZ Budget score: {value!r}")
        if row["source_display"] == "-" and value != 0:
            raise ValueError("a source dash may only normalize to zero")
        if row["source_display"] != "-" and row["source_display"] != f"{value:.3f}":
            raise ValueError("source display and normalized value disagree")
        by_policy.setdefault(row["reform_policy"], []).append(row)

    expected_ids: set[str] = set()
    for policy, spec in _MEASURES.items():
        group = by_policy.get(policy, [])
        annual = {row.get("fy"): row for row in group if "fy" in row}
        for fy, period, value, display in spec["years"]:
            suffix = fy.replace("-", "_")
            expected_id = f"{spec['id_prefix']}_fy{suffix}"
            expected_ids.add(expected_id)
            row = annual.get(fy)
            expected = (
                expected_id,
                spec["event"],
                spec["measure"],
                period,
                value,
                display,
                spec["pin"],
            )
            actual = (
                row and row["id"],
                row and row["fiscal_event"],
                row and row["measure"],
                row and row["period"],
                row and row["value_nzd_millions"],
                row and row["source_display"],
                row and row["source_pin"],
            )
            if actual != expected or _fy_end(fy) != period:
                raise ValueError(f"NZ Budget annual row drifted: {policy} {fy}")

        totals = [row for row in group if "period_start" in row]
        total_id = f"{spec['id_prefix']}_operating_total"
        expected_ids.add(total_id)
        if len(totals) != 1:
            raise ValueError(f"NZ Budget total census drifted for {policy}")
        total = totals[0]
        start, end, value, display = spec["total"]
        expected_total = (
            total_id,
            spec["event"],
            spec["measure"],
            end,
            start,
            end,
            spec["window"],
            value,
            display,
            spec["pin"],
        )
        actual_total = (
            total["id"],
            total["fiscal_event"],
            total["measure"],
            total["period"],
            total["period_start"],
            total["period_end"],
            total["window"],
            total["value_nzd_millions"],
            total["source_display"],
            total["source_pin"],
        )
        if actual_total != expected_total:
            raise ValueError(f"NZ Budget total row drifted: {policy}")
        if sum(v for _, _, v, _ in spec["years"]) != value:
            raise ValueError(f"NZ Budget annual values do not sum to total: {policy}")

    if seen != expected_ids:
        raise ValueError("NZ Budget claim ids or exact census drifted")

    source_iwtc, source_wff = _source_table_values()
    expected_tables = tuple(
        tuple(v for _, _, v, _ in _MEASURES[policy]["years"])
        + (_MEASURES[policy]["total"][2],)
        for policy in _MEASURES
    )
    if (source_iwtc, source_wff) != expected_tables:
        raise ValueError("claims do not match the pinned source-page score tables")


def load_claims(
    path: Path = CLAIMS_PATH,
    *,
    manifest_path: Path = MANIFEST_PATH,
    verify_sha: bool = True,
) -> dict:
    if verify_sha:
        _require_hash(path, CLAIMS_SHA256, "claims")
        _require_hash(NOTES_PATH, NOTES_SHA256, "notes")
        _require_hash(SOURCE_PAGES_PATH, SOURCE_PAGES_SHA256, "source pages")
    manifest = load_manifest(manifest_path, verify_sha=verify_sha)
    payload = json.loads(path.read_text())
    _validate_payload(payload, manifest)
    return payload


def _reform(policy: str) -> ReformRef:
    spec = _MEASURES[policy]
    descriptor = {
        "policy": policy,
        "change": spec["change"],
    }
    if "effective_from" in spec:
        descriptor["effective_from"] = spec["effective_from"]
    if "effective_month" in spec:
        descriptor["effective_month"] = spec["effective_month"]
    if "maximum_effective_to" in spec:
        descriptor["maximum_effective_to"] = spec["maximum_effective_to"]
        descriptor["termination_condition"] = spec["termination_condition"]
    return ReformRef(
        framework="policy_ref",
        reform=descriptor,
    )


def _publication(row: dict, manifest: dict[str, dict]) -> dict:
    primary = manifest[row["source_pin"]]
    excerpt = manifest["source_page_excerpt"]
    supporting = [
        {
            "id": pin,
            "title": manifest[pin]["document"],
            "url": manifest[pin]["url"],
            "sha256": manifest[pin]["sha256"],
            "page": (
                f"{manifest[pin]['printed_page']} (PDF p. {manifest[pin]['pdf_page']})"
            ),
        }
        for pin in _MEASURES[row["reform_policy"]]["supporting_pins"]
    ]
    return {
        "registry": REGISTRY_MARK,
        "publish_without_result": True,
        "publisher": primary["publisher"],
        "title": primary["document"],
        "name": row["measure"],
        "date": primary["date"],
        "url": primary["url"],
        "page": f"{primary['printed_page']} (PDF p. {primary['pdf_page']})",
        "window": row.get("window") or f"FY{row['fy']}",
        "vote": "Revenue (IRD–Crown)",
        "source_pin": row["source_pin"],
        "source_sha256": primary["sha256"],
        "source_excerpt_sha256": excerpt["sha256"],
        "supporting_sources": supporting,
        "replication_status": (
            "rule_mechanics_present; official_to_model_fiscal_timing_bridge "
            "pending; IWTC petrol_termination_scenario pending where applicable"
        ),
        "axiom_rulespec": (
            f"rulespec-nz@{RULESPEC_NZ_COMMIT}#{RULESPEC_MODULE}::"
            + ",".join(_MEASURES[row["reform_policy"]]["rules"])
        ),
    }


def stage_scores(payload: dict | None = None) -> list[ExternalScore]:
    manifest = load_manifest()
    if payload is None:
        payload = load_claims()
    else:
        _validate_payload(payload, manifest)
    scores = []
    for row in payload["claims"]:
        conditions = {
            "country": "NZ",
            "geography": "NZ",
            "program": "working_for_families",
            "subgroup": "total",
            "basis": "forecast",
            "period_basis": "new_zealand_fiscal_year_ending_30_june",
            "benchmark_class": BenchmarkClass.DIFFERENT_MODEL.value,
            "behavioral_response": "official_costing_not_stated",
            "fiscal_event": row["fiscal_event"],
            "measure": row["measure"],
            "fiscal_measure": "vote_revenue_ird_crown_operating_impact",
            "source_scale": "nzd_millions",
            "accounting_scope": "official_vote_operating_impact",
            "source_notation": "nzd_millions_increase_dash_normalized_zero",
        }
        if "fy" in row:
            conditions["fy"] = row["fy"]
        else:
            conditions["window_kind"] = "total"
        scores.append(
            ExternalScore(
                source="nz_treasury",
                source_model=(
                    "Official Budget costing; methodology not stated in the "
                    "Summary of Initiatives"
                ),
                source_column=(
                    f"Revenue (IRD–Crown) — "
                    f"{row.get('fy', 'Operating Total')}: "
                    f"{row['source_display']} ($m)"
                ),
                publication=_publication(row, manifest),
                metric=Metric.OPERATING_COST_CHANGE,
                unit_concept=UnitConcept.NZD,
                period=row["period"],
                time_basis=TimeBasis.FISCAL_YEAR,
                value=float(row["value_nzd_millions"]) * 1_000_000,
                value_kind="nzd",
                conditions=conditions,
                reform=_reform(row["reform_policy"]),
                calibration_relationship=CalibrationRelationship.HELD_OUT,
                period_start=row.get("period_start"),
                period_end=row.get("period_end"),
            )
        )
    return finish(scores, REGISTRY_MARK)


def ingest(db_path: Path) -> dict:
    """Validate, atomically replace this registry, then mirror lane state.

    Result/diagnosis rows survive when their claim id remains in the exact
    source census; unchanged parents are updated in place and attachments are
    pruned only for claims that disappeared. Existing diagnosing/published/
    regressed lane states are never rolled back by a source refresh, while an
    early-stage lane advances to computed when surviving results exist.
    The committed JSON lane mirror is deliberately post-transaction, matching
    the repository-wide convention. A mirror failure is recoverable by safely
    rerunning this idempotent ingest.
    """
    scores = stage_scores()
    score_rows = [ScorecardDB.score_row(score) for score in scores]
    new_claim_ids = {score.claim_id() for score in scores}
    db = ScorecardDB(db_path)
    try:
        with db.conn:
            old_claim_ids = {
                row[0]
                for row in db.conn.execute(
                    "SELECT claim_id FROM external_scores "
                    "WHERE json_extract(publication, '$.registry') = ?",
                    (REGISTRY_MARK,),
                ).fetchall()
            }
            stale_claim_ids = sorted(old_claim_ids - new_claim_ids)
            if stale_claim_ids:
                placeholders = ",".join("?" for _ in stale_claim_ids)
                db.conn.execute(
                    f"DELETE FROM diagnoses WHERE claim_id IN ({placeholders})",
                    stale_claim_ids,
                )
                db.conn.execute(
                    f"DELETE FROM pe_results WHERE claim_id IN ({placeholders})",
                    stale_claim_ids,
                )
                db.conn.execute(
                    f"DELETE FROM external_scores WHERE claim_id IN ({placeholders})",
                    stale_claim_ids,
                )
            db.conn.executemany(SCORES_SQL, score_rows)
            register_baselines_txn(db)

            result_state = db.conn.execute(
                "SELECT COUNT(r.id) AS latest_results, "
                "COALESCE(SUM(CASE WHEN r.status != 'not_computed' "
                "THEN 1 ELSE 0 END), 0) AS computed_claims, "
                "MAX(CASE WHEN r.status != 'not_computed' "
                "THEN substr(r.computed_at, 1, 10) END) AS latest_result "
                "FROM external_scores s "
                "LEFT JOIN pe_results r ON r.id = ("
                "SELECT id FROM pe_results WHERE claim_id = s.claim_id "
                "ORDER BY computed_at DESC, id DESC LIMIT 1) "
                "WHERE json_extract(s.publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            ).fetchone()
            result_count = result_state["latest_results"]
            computed_claims = result_state["computed_claims"]
            latest_result = result_state["latest_result"] or UPDATED
            base_detail = (
                "12 official claims across 2 rule-encoded replication "
                "candidates; fiscal timing and IWTC termination bridge pending"
            )
            current_lane = db.conn.execute(
                "SELECT stage, detail, updated_at FROM lanes WHERE lane = ?",
                (LANE_ID,),
            ).fetchone()
            protected_stages = {"diagnosing", "published", "regressed"}
            if current_lane is not None and current_lane["stage"] in protected_stages:
                lane_stage = current_lane["stage"]
            elif computed_claims:
                lane_stage = "computed"
                detail = f"{computed_claims} of {len(scores)} claims computed — {base_detail}"
                db.conn.execute(
                    LANE_SQL,
                    (LANE_ID, lane_stage, detail, latest_result),
                )
            elif current_lane is not None and current_lane["stage"] == "computed":
                lane_stage = "regressed"
                detail = f"0 of {len(scores)} claims retain results — {base_detail}"
                db.conn.execute(
                    LANE_SQL,
                    (LANE_ID, lane_stage, detail, UPDATED),
                )
            else:
                lane_stage = "ingested"
                db.conn.execute(
                    LANE_SQL,
                    (LANE_ID, lane_stage, base_detail, UPDATED),
                )
        lanes_synced = sync_lane_feed(
            db,
            REPO / "data" / "lanes.json",
            UPDATED,
            lanes={
                LANE_ID: {
                    "source": "New Zealand Treasury",
                    "area": "official Budget reform scores",
                    "mode": 2,
                    "country": "NZ",
                }
            },
        )
        coverage = db.coverage()
    finally:
        db.close()
    return {
        "claims": len(scores),
        "results": result_count,
        "computed_claims": computed_claims,
        "lane": LANE_ID,
        "lane_stage": lane_stage,
        "lanes_synced": lanes_synced,
        "coverage": coverage,
    }


if __name__ == "__main__":
    import sys

    output = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(output), indent=1))
