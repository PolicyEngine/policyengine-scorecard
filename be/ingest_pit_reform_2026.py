"""Ingest descriptive claims for Belgium's 15 July 2026 PIT reform.

The vendored package contains seven claims: one SPF Finances horizon-2030
statement, one Cour des comptes horizon-2030 evaluation quoted secondarily in
the Chamber committee report, and five PolicyEngine/Axiom results keyed to
income years 2026-2030 (assessment years 2027-2031). The official citations do
not identify whether their 2030 horizon is an income year, assessment year, or
another annual basis. This adapter records that ambiguity and never resolves
it by reference to the PolicyEngine series.

Every claim is held out. Five ``PEResult`` rows project the same pinned draft
PolicyEngine computations onto the five PolicyEngine claims; they preserve
result provenance for the result-backed app export and are not independent
validation. The income-year-2030 computation also attaches to both official
claims as ``constructed``. Those annotations state the unknown period
relationship, the distinct baseline provenance, and—in the Cour des comptes
case—the secondary citation. No row claims an outturn, behavioural response,
shared official period basis, or published official methodology that the
pinned sources do not provide.

Usage:
    PYTHONPATH=. python -m be.ingest_pit_reform_2026 data/scorecard.db
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from scorecard_db.baselines import register_baselines_txn
from scorecard_db.db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from scorecard_db.harvest import REPO, finish
from scorecard_db.ingest_harvest import sync_lane_feed
from scorecard_db.models import (
    BenchmarkClass,
    CalibrationRelationship,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
    baseline_key,
)

from .worlds import (
    AXIOM_BE_PIT_REFORM_2026_BASELINE,
    COUR_DES_COMPTES_PIT_REFORM_2026_BASELINE,
    SPF_FINANCES_PIT_REFORM_2026_BASELINE,
)

SOURCE_DIR = REPO / "sources" / "be-pit-reform-2026"
CLAIMS_PATH = SOURCE_DIR / "claims.json"
MANIFEST_PATH = SOURCE_DIR / "manifest.jsonl"
NOTES_PATH = SOURCE_DIR / "NOTES.md"

CLAIMS_SHA256 = "0406e6edaaf2ea99c3eeeaf7712267841aeffc0865f5c9e43b3174db9d8cf935"
MANIFEST_SHA256 = "b1717480bcd720df9c3e492a4d7aaaef157403421b1e12c8eb7e59173c724572"
NOTES_SHA256 = "281d8c81e8b786af24518ed829e9b85ac76c7a86e5d86e2629e0a3cf2aa64890"

REGISTRY_MARK = "be_pit_reform_2026"
LANE_ID = "be-pit-reform-2026"
UPDATED = "2026-08-29"
RUN_ID = "be-pit-reform-2026@3d9f690"
COMPUTED_AT = "2026-08-28"

REPORT_SHA256 = "53c65d610f2d2624040528287a47b1810ef7096f42fa1ea7a00ef1ef016c29db"
AGED_RESULTS_SHA256 = "f138697423c77c77af10467dccf253faf10bc9869a0f9844379d31ab5ab88d50"
AXIOM_COMMIT = "c6cc389a8f5e7238019e4fa06849325fad9acd46"
RULESPEC_BE_COMMIT = "ddc28fe7fba3509019a2b80ada5fb6f3ee922839"
# First-class reform-implementation provenance (the report's own pins): the
# beReform overlay commit that implements the loi du 15 juillet 2026 and the
# digest of the enacted-law source bytes it encodes. Without these the exact
# implementation is recoverable only transitively through the report.
BEREFORM_COMMIT = "cf05994bc815d70014eff64261d296c200402384"
REFORM_LAW_SHA256 = "c95eda87835a874fc49cc84f2d65b834c2f372b150e6b65a1732a1b2f485f9d1"
ENGINE_VERSION = f"axiom@{AXIOM_COMMIT}; rulespec-be@{RULESPEC_BE_COMMIT}"
DATA_BUNDLE = f"microcosm_be_v05h_corrected@{AGED_RESULTS_SHA256}"

REFORM = {
    "policy": "be_pit_reform_2026_07_15",
    "law": "loi_du_15_juillet_2026",
    "moniteur_belge": "2026-07-29_p40196",
}

AXIOM_BASELINE = AXIOM_BE_PIT_REFORM_2026_BASELINE

_BASELINE_BY_SOURCE = {
    "spf_finances": SPF_FINANCES_PIT_REFORM_2026_BASELINE,
    "cour_des_comptes": COUR_DES_COMPTES_PIT_REFORM_2026_BASELINE,
    "policyengine": AXIOM_BASELINE,
}

_SOURCE_META = {
    "spf_finances": {
        "publisher": "SPF Finances",
        "title": "DOC 56 1243/004 — Rapport de la première lecture",
        "date": "2026-06-16",
        "name": "SPF Finances PIT-reform revenue change",
    },
    "cour_des_comptes": {
        "publisher": "Cour des comptes",
        "title": "DOC 56 1243/004 — Rapport de la première lecture",
        "date": "2026-06-16",
        "name": "Cour des comptes PIT-reform revenue change",
    },
    "policyengine": {
        "publisher": "PolicyEngine",
        "title": "Belgian PIT reform corrected v05h aged run",
        "date": "2026-08-28",
        "name": "PolicyEngine PIT-reform revenue change",
    },
}

_EXPECTED_PINS = {
    "doc56_1243_001_pdf": (
        "0e216fcd40c6cb4fa2b1feaabbdc16bc9c6a8c20583e3d5cc1a5637c043d0e70"
    ),
    "doc56_1243_004_pdf": (
        "532cb5f831d84dc52641134802f428bf0171ce72a643ab14558c6b5736324a83"
    ),
    "doc56_1243_004_text": (
        "bc65616d3969c94dd6745d4a168c4395d89f6a77e112479b0d0d29fc757b568d"
    ),
    "lane_aged3_report": REPORT_SHA256,
    "v05h_aged_results": AGED_RESULTS_SHA256,
}

_EXPECTED_ROWS = {
    "spf_finances_horizon_2030": (
        "spf_finances",
        2030,
        None,
        -4_000_000_000,
        "forecast",
        "horizon_2030_income_vs_assessment_year_unspecified",
        "different_model",
        ("doc56_1243_004_pdf", "doc56_1243_001_pdf"),
    ),
    "cour_des_comptes_horizon_2030": (
        "cour_des_comptes",
        2030,
        None,
        -5_000_000_000,
        "forecast",
        "horizon_2030_income_vs_assessment_year_unspecified",
        "different_model",
        ("doc56_1243_004_pdf",),
    ),
    "policyengine_income_2026_ay2027": (
        "policyengine",
        2026,
        2027,
        -513_450_000,
        "projection_conditioned_mechanics",
        "income_year",
        "same_assumptions",
        ("lane_aged3_report", "v05h_aged_results"),
    ),
    "policyengine_income_2027_ay2028": (
        "policyengine",
        2027,
        2028,
        -456_510_000,
        "projection_conditioned_mechanics",
        "income_year",
        "same_assumptions",
        ("lane_aged3_report", "v05h_aged_results"),
    ),
    "policyengine_income_2028_ay2029": (
        "policyengine",
        2028,
        2029,
        -779_680_000,
        "projection_conditioned_mechanics",
        "income_year",
        "same_assumptions",
        ("lane_aged3_report", "v05h_aged_results"),
    ),
    "policyengine_income_2029_ay2030": (
        "policyengine",
        2029,
        2030,
        -2_457_460_000,
        "projection_conditioned_mechanics",
        "income_year",
        "same_assumptions",
        ("lane_aged3_report", "v05h_aged_results"),
    ),
    "policyengine_income_2030_ay2031": (
        "policyengine",
        2030,
        2031,
        -4_155_520_000,
        "projection_conditioned_mechanics",
        "income_year",
        "same_assumptions",
        ("lane_aged3_report", "v05h_aged_results"),
    ),
}

_SOURCE_MODELS = {
    "spf_finances": "SPF Finances internal model",
    "cour_des_comptes": "Cour des comptes evaluation",
    "policyengine": "Axiom engine over Microcosm-BE v05h corrected aged run",
}

_OFFICIAL_QUOTES = {
    "spf_finances_horizon_2030": (
        "diminution des recettes fiscales de 4 milliards d’euros à l’horizon 2030"
    ),
    "cour_des_comptes_horizon_2030": (
        "la Cour des comptes évalue celle-ci à près de 5 milliards "
        "d’euros à l’horizon 2030"
    ),
}

_COMMON_ROW_FIELDS = {
    "id",
    "source",
    "source_model",
    "period",
    "value",
    "basis",
    "period_basis",
    "benchmark_class",
    "source_pins",
}
_OFFICIAL_ROW_FIELDS = _COMMON_ROW_FIELDS | {"quote", "methodology_note"}
_POLICYENGINE_ROW_FIELDS = _COMMON_ROW_FIELDS | {"assessment_year"}

_MANIFEST_FIELDS = {
    "id",
    "document",
    "date",
    "sha256",
    "artifact",
    "stored_in_repo",
    "role",
    "derived_from",
    "source_commit",
}
_MANIFEST_REQUIRED = {
    "id",
    "document",
    "date",
    "sha256",
    "artifact",
    "stored_in_repo",
    "role",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest(
    path: Path | None = None, *, verify_sha: bool = True
) -> dict[str, dict]:
    path = path or MANIFEST_PATH
    if verify_sha and _sha256(path) != MANIFEST_SHA256:
        raise ValueError("Belgian PIT-reform manifest SHA-256 drifted")
    records: dict[str, dict] = {}
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        unknown = set(row) - _MANIFEST_FIELDS
        missing = _MANIFEST_REQUIRED - set(row)
        if unknown or missing:
            raise ValueError(
                "Belgian PIT-reform manifest fields drifted on line "
                f"{line_number}: unknown={sorted(unknown)}, missing={sorted(missing)}"
            )
        pin_id = row["id"]
        if pin_id in records:
            raise ValueError(f"duplicate Belgian PIT-reform pin: {pin_id}")
        if row["stored_in_repo"] is True:
            artifact = SOURCE_DIR / row["artifact"]
            if verify_sha and (
                not artifact.is_file() or _sha256(artifact) != row["sha256"]
            ):
                raise ValueError(
                    f"{pin_id}: vendored artifact missing or SHA-256 drifted"
                )
        elif row["stored_in_repo"] is not False:
            raise ValueError(f"{pin_id}: stored_in_repo must be true or false")
        records[pin_id] = row
    observed = {pin_id: row["sha256"] for pin_id, row in records.items()}
    if observed != _EXPECTED_PINS:
        raise ValueError(
            f"Belgian PIT-reform manifest pin census drifted: observed={observed!r}"
        )
    return records


def _validate_payload(payload: dict, manifest: dict[str, dict]) -> None:
    if set(payload) != {"reform", "claims"}:
        raise ValueError(
            "Belgian PIT-reform top-level fields drifted: "
            f"{sorted(set(payload) ^ {'reform', 'claims'})}"
        )
    if payload["reform"] != REFORM:
        raise ValueError("Belgian PIT-reform policy descriptor drifted")
    if not isinstance(payload["claims"], list):
        raise ValueError("Belgian PIT-reform claims must be a list")

    observed = {}
    for row in payload["claims"]:
        if not isinstance(row, dict):
            raise ValueError("Belgian PIT-reform claim must be an object")
        source = row.get("source")
        expected_fields = (
            _POLICYENGINE_ROW_FIELDS
            if source == "policyengine"
            else _OFFICIAL_ROW_FIELDS
        )
        if set(row) != expected_fields:
            raise ValueError(
                f"{row.get('id', '<unknown>')}: staged fields drifted: "
                f"unknown={sorted(set(row) - expected_fields)}, "
                f"missing={sorted(expected_fields - set(row))}"
            )
        claim_id = row["id"]
        if claim_id in observed:
            raise ValueError(f"duplicate Belgian PIT-reform claim id: {claim_id}")
        if source not in _SOURCE_META:
            raise ValueError(f"{claim_id}: unknown source {source!r}")
        if row["source_model"] != _SOURCE_MODELS[source]:
            raise ValueError(f"{claim_id}: source model drifted")
        BenchmarkClass(row["benchmark_class"])
        for pin_id in row["source_pins"]:
            if pin_id not in manifest:
                raise ValueError(f"{claim_id}: unknown source pin {pin_id!r}")
        if source != "policyengine" and row["quote"] != _OFFICIAL_QUOTES[claim_id]:
            raise ValueError(f"{claim_id}: source quotation drifted")
        observed[claim_id] = (
            source,
            row["period"],
            row.get("assessment_year"),
            row["value"],
            row["basis"],
            row["period_basis"],
            row["benchmark_class"],
            tuple(row["source_pins"]),
        )

    if observed != _EXPECTED_ROWS:
        missing = sorted(set(_EXPECTED_ROWS) - set(observed))
        extra = sorted(set(observed) - set(_EXPECTED_ROWS))
        changed = sorted(
            claim_id
            for claim_id in set(observed) & set(_EXPECTED_ROWS)
            if observed[claim_id] != _EXPECTED_ROWS[claim_id]
        )
        raise ValueError(
            "Belgian PIT-reform claim census drifted: "
            f"missing={missing}, extra={extra}, changed={changed}"
        )


_REPORT_HEADLINE_ROW = re.compile(
    r"^\| AY(20\d\d) \| (-[\d,]+\.\d\d) \| (-[\d,]+\.\d\d) \| ([\d,]+\.\d\d) \|$"
)


def _report_aged_deltas(report_path: Path) -> dict[int, float]:
    """The vendored report's headline aged deltas, keyed by assessment year.

    The report is the pinned source the PolicyEngine claims transcribe; a
    census that only compares claims against constants written alongside them
    is green by construction, so the applied per-year values are re-read from
    the report itself on every load.
    """
    deltas: dict[int, float] = {}
    for line in report_path.read_text().splitlines():
        match = _REPORT_HEADLINE_ROW.match(line)
        if match:
            # Columns: AY | static delta | aged delta | aged minus static.
            deltas[int(match.group(1))] = float(match.group(3).replace(",", ""))
    return deltas


def _verify_report_faithfulness(payload: dict) -> None:
    report_path = SOURCE_DIR / "LANE_AGED3_REPORT.md"
    deltas = _report_aged_deltas(report_path)
    if sorted(deltas) != [2027, 2028, 2029, 2030, 2031]:
        raise ValueError(
            "Belgian PIT-reform report headline table drifted: "
            f"assessment years {sorted(deltas)}"
        )
    for row in payload["claims"]:
        if row["source"] != "policyengine":
            continue
        # Static-column deltas share the AY row; the aged column is what the
        # claims transcribe, rounded to the nearest EUR 10,000.
        expected = round(deltas[row["assessment_year"]], -4)
        if row["value"] != expected:
            raise ValueError(
                f"{row['id']}: value {row['value']} is not the pinned "
                f"report's aged delta {deltas[row['assessment_year']]} "
                f"rounded to EUR 10,000 ({expected:.0f})"
            )


def load_claims(
    path: Path = CLAIMS_PATH,
    *,
    manifest_path: Path = MANIFEST_PATH,
    verify_sha: bool = True,
) -> dict:
    """Load and validate the complete vendored package before any write."""
    if verify_sha and _sha256(path) != CLAIMS_SHA256:
        raise ValueError("Belgian PIT-reform claims SHA-256 drifted")
    if verify_sha and _sha256(NOTES_PATH) != NOTES_SHA256:
        raise ValueError("Belgian PIT-reform source notes SHA-256 drifted")
    manifest = _load_manifest(manifest_path, verify_sha=verify_sha)
    payload = json.loads(path.read_text())
    _validate_payload(payload, manifest)
    _verify_report_faithfulness(payload)
    return payload


def _publication(row: dict, manifest: dict[str, dict]) -> dict:
    meta = _SOURCE_META[row["source"]]
    source_pins = [
        {
            "id": pin_id,
            "sha256": manifest[pin_id]["sha256"],
            "document": manifest[pin_id]["document"],
        }
        for pin_id in row["source_pins"]
    ]
    if row["source"] == "policyengine":
        return {
            **meta,
            "name": (
                f"{meta['name']}, income {row['period']} "
                f"(assessment year {row['assessment_year']})"
            ),
            "url": "",
            "window": f"Income {row['period']} (AY{row['assessment_year']})",
            "registry": REGISTRY_MARK,
            "source_pins": source_pins,
            "source_commit": "3d9f690",
            "report_sha256": REPORT_SHA256,
            "aged_results_sha256": AGED_RESULTS_SHA256,
            "period_semantics": "income year; assessment year is income year + 1",
            "baseline_note": (
                "Same-year indexed current law (encoded Article 178 chain and "
                "statutory special coefficients); incomes uprated by declared "
                "FPB factors on fixed 2025 weights; Royal-Decree-pending "
                "Article 147 values carried at last enacted levels."
            ),
            "behavioral_response": "none",
            "model_status": "draft_pending_standard_validation",
            "public_release": False,
        }
    publication = {
        **meta,
        "url": "",
        "window": "Horizon 2030 (income/assessment-year basis unspecified)",
        "registry": REGISTRY_MARK,
        "source_pins": source_pins,
        "quote": row["quote"],
        "methodology_note": row["methodology_note"],
        "period_semantics": (
            "official horizon 2030; pinned citation does not identify income "
            "year versus assessment year"
        ),
    }
    if row["source"] == "cour_des_comptes":
        publication["citation_class"] = "secondary"
        publication["unavailable_pin"] = "Cour des comptes advice document"
    return publication


def _score(row: dict, manifest: dict[str, dict]) -> ExternalScore:
    baseline = _BASELINE_BY_SOURCE[row["source"]]
    conditions = {
        "country": "BE",
        "geography": "BE",
        "program": "income_tax",
        "subgroup": "total",
        "basis": row["basis"],
        "period_basis": row["period_basis"],
        "benchmark_class": BenchmarkClass(row["benchmark_class"]).value,
        "baseline_policy": baseline["policy"],
    }
    if row["source"] == "policyengine":
        conditions.update(
            {
                "assessment_year": str(row["assessment_year"]),
                "behavioral_response": "none",
                "data_vintage": "microcosm_be_v05h_corrected",
            }
        )
    return ExternalScore(
        source=row["source"],
        source_model=row["source_model"],
        source_column=row["id"],
        publication=_publication(row, manifest),
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.EUR,
        period=row["period"],
        time_basis=TimeBasis.ANNUAL,
        value=float(row["value"]),
        value_kind="eur",
        conditions=conditions,
        reform=ReformRef(
            framework="policy_ref",
            reform=REFORM,
            baseline=baseline,
        ),
        calibration_relationship=CalibrationRelationship.HELD_OUT,
    )


def _self_result(score: ExternalScore, row: dict) -> PEResult:
    recipe = {
        "kind": "same_computation_projection",
        "income_year": row["period"],
        "assessment_year": row["assessment_year"],
        "baseline": AXIOM_BASELINE["policy"],
        "behavioral_response": "none",
        "population": "microcosm_be_v05_2025",
        "source_commit": "3d9f690",
        "report_sha256": REPORT_SHA256,
        "aged_results_sha256": AGED_RESULTS_SHA256,
        "reform_implementation": f"beReform@{BEREFORM_COMMIT}",
        "reform_law_sha256": REFORM_LAW_SHA256,
    }
    annotation = (
        "This result and the PolicyEngine claim project the same pinned draft "
        "computation; the attachment preserves computation provenance for the "
        "result-backed export and is not independent validation. Period is "
        f"income year {row['period']} (assessment year {row['assessment_year']}); "
        "no behavioural response. Draft pending standard validation procedures."
    )
    return PEResult(
        claim_id=score.claim_id(),
        computed_value=float(row["value"]),
        status=ComparisonStatus.COMPARABLE,
        engine_version=ENGINE_VERSION,
        data_bundle=DATA_BUNDLE,
        pe_construction=json.dumps(recipe, sort_keys=True),
        run_id=RUN_ID,
        computed_at=COMPUTED_AT,
        annotations=[annotation],
        baseline_key=baseline_key(AXIOM_BASELINE),
    )


def _official_result(
    score: ExternalScore, official_row: dict, computed_row: dict
) -> PEResult:
    recipe = {
        "kind": "official_horizon_cross_attachment",
        "attachment_class": ComparisonStatus.CONSTRUCTED.value,
        "claim_period": official_row["period"],
        "claim_period_basis": official_row["period_basis"],
        "computed_income_year": computed_row["period"],
        "computed_assessment_year": computed_row["assessment_year"],
        "period_relationship": "unresolved",
        "claim_baseline": _BASELINE_BY_SOURCE[official_row["source"]]["policy"],
        "computed_baseline": AXIOM_BASELINE["policy"],
        "source_commit": "3d9f690",
        "aged_results_sha256": AGED_RESULTS_SHA256,
        "reform_implementation": f"beReform@{BEREFORM_COMMIT}",
        "reform_law_sha256": REFORM_LAW_SHA256,
    }
    source_name = _SOURCE_META[official_row["source"]]["publisher"]
    extra = (
        " The Cour des comptes figure is a secondary citation; its advice "
        "document is not pinned."
        if official_row["source"] == "cour_des_comptes"
        else " SPF Finances' methodology is unpublished."
    )
    annotation = (
        f"The {source_name} claim states only horizon 2030; the pinned "
        "citation does not identify income year versus assessment year. The "
        "attached PolicyEngine value is keyed to income year 2030 (assessment "
        "year 2031). Their period relationship remains unresolved, and no "
        "baseline equivalence is asserted." + extra
    )
    return PEResult(
        claim_id=score.claim_id(),
        computed_value=float(computed_row["value"]),
        status=ComparisonStatus.CONSTRUCTED,
        engine_version=ENGINE_VERSION,
        data_bundle=DATA_BUNDLE,
        pe_construction=json.dumps(recipe, sort_keys=True),
        run_id=RUN_ID,
        computed_at=COMPUTED_AT,
        annotations=[annotation],
        baseline_key=baseline_key(AXIOM_BASELINE),
    )


def stage_all(
    payload: dict | None = None,
) -> tuple[list[ExternalScore], list[PEResult], dict]:
    """Stage the exact seven-claim/seven-result registry population."""
    manifest = _load_manifest()
    if payload is None:
        payload = load_claims()
    else:
        _validate_payload(payload, manifest)
    rows = payload["claims"]
    scores = finish([_score(row, manifest) for row in rows], REGISTRY_MARK)
    by_column = {score.source_column: score for score in scores}

    policyengine_rows = [row for row in rows if row["source"] == "policyengine"]
    official_rows = [row for row in rows if row["source"] != "policyengine"]
    computed_2030 = next(row for row in policyengine_rows if row["period"] == 2030)
    results = [_self_result(by_column[row["id"]], row) for row in policyengine_rows] + [
        _official_result(by_column[row["id"]], row, computed_2030)
        for row in official_rows
    ]

    result_claims = [result.claim_id for result in results]
    if len(set(result_claims)) != len(results):
        raise ValueError("duplicate Belgian PIT-reform result attachment")
    if set(result_claims) != {score.claim_id() for score in scores}:
        raise ValueError("Belgian PIT-reform claims/results do not form a full export")

    summary = {
        "claims": len(scores),
        "results": len(results),
        "sources": len({score.source for score in scores}),
        "self_attachments": len(policyengine_rows),
        "official_cross_attachments": len(official_rows),
    }
    if summary != {
        "claims": 7,
        "results": 7,
        "sources": 3,
        "self_attachments": 5,
        "official_cross_attachments": 2,
    }:
        raise ValueError(f"Belgian PIT-reform staging accounting drifted: {summary}")
    return scores, results, summary


def ingest(db_path: Path) -> dict:
    """Validate first, then atomically replace this registry and its lane."""
    scores, results, summary = stage_all()
    score_rows = [ScorecardDB.score_row(score) for score in scores]
    result_rows = [ScorecardDB.result_row(result) for result in results]
    db = ScorecardDB(db_path)
    try:
        with db.conn:
            selector = (
                "SELECT claim_id FROM external_scores "
                "WHERE json_extract(publication, '$.registry') = ?"
            )
            db.conn.execute(
                f"DELETE FROM diagnoses WHERE claim_id IN ({selector})",
                (REGISTRY_MARK,),
            )
            db.conn.execute(
                f"DELETE FROM pe_results WHERE claim_id IN ({selector})",
                (REGISTRY_MARK,),
            )
            db.conn.execute(
                "DELETE FROM external_scores "
                "WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            )
            db.conn.executemany(SCORES_SQL, score_rows)
            db.conn.executemany(RESULTS_SQL, result_rows)
            register_baselines_txn(db)
            db.conn.execute(
                LANE_SQL,
                (
                    LANE_ID,
                    "computed",
                    "7 claims from 3 sources; 7 results (5 same-computation "
                    "PolicyEngine self-attachments, 2 constructed official "
                    "cross-attachments with unresolved horizon basis)",
                    UPDATED,
                ),
            )
        lanes_synced = sync_lane_feed(
            db,
            REPO / "data" / "lanes.json",
            UPDATED,
            lanes={
                LANE_ID: {
                    "source": "Belgian PIT reform scorekeepers",
                    "area": "15 July 2026 PIT-reform revenue changes",
                    "mode": 2,
                    "country": "BE",
                }
            },
        )
        coverage = db.coverage()
    finally:
        db.close()
    return summary | {
        "lane": LANE_ID,
        "lanes_synced": lanes_synced,
        "coverage": coverage,
    }


if __name__ == "__main__":
    import sys

    output = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(output), indent=1))
