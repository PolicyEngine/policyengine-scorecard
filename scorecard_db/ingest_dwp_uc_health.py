"""Ingest DWP's UC health element caseload and PolicyEngine-UK's new-claimant
share (lane dwp-uc-health, issue #87).

Inputs:

    data/externals/dwp-uc-health.json  the adapter's tidy rows (QC'd there)
    sources/dwp-uc-health/pe/<bundle>.json  the parameter-tree read-back
        (pipeline/compute_uk_uc_health_readback.py)
    sources/dwp-uc-health/annotations.json  notes, each with a basis

Claims (16, held out; see source.json for the calibration evidence):
    15 LCWRA caseloads, April to June 2026, by entitlement rate and in
       total (April's lower rate is "[low]", a suppressed claim). They have
       no counterpart until a run on the certified bundle, so they publish
       without a result.
    1  the lower (new-claimant) rate's share of the June 2026 total.
The share's counterpart is PolicyEngine-UK's new_claimant_share for
2026-27, ``constructed``: a whole-year assumption against one month.

    PYTHONPATH=. python -m scorecard_db.ingest_dwp_uc_health data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, require_fields
from .models import (
    BASELINE,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
)
from .relationships import uk_relationship

EXTERNALS = REPO / "data" / "externals"
SOURCE_DIR = REPO / "sources" / "dwp-uc-health"
ADAPTER_SOURCE = "dwp-uc-health"
SOURCE = "dwp_uc_health"
SOURCE_MODEL = "dwp_administrative_data"
PE_BUNDLE = "uk-2.147.2"

LANE_ID = "dwp-uc-health"
LANE_UPDATED = "2026-10-23"
FEED_UPDATED = "2026-10-23"
LANE_FEED_META = {
    "source": "DWP",
    "area": "UC health element caseload by rate",
    "mode": 1,
    "country": "UK",
}

_KNOWN_FIELDS = frozenset(
    {
        "geography",
        "metric",
        "period",
        "program",
        "source",
        "source_column",
        "status",
        "subgroup",
        "unit_concept",
        "value",
    }
)
_METRICS = {
    "caseload": (Metric.CASELOAD, UnitConcept.PERSONS, "count"),
    "affected_share": (Metric.AFFECTED_SHARE, UnitConcept.SHARE, "share"),
}
_RATE_LABELS = {
    "total": "all LCWRA claimants",
    "higher_severe_conditions": "higher rate, severe conditions criteria",
    "higher_terminally_ill": "higher rate, terminally ill",
    "higher_protected": "higher rate, pre-April 2026 claims (protected)",
    "lower_new_claimant": "lower rate (new claimants from April 2026)",
}
_URL = (
    "https://www.gov.uk/government/statistics/"
    "universal-credit-health-statistics-april-2019-to-june-2026"
)


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run uv run --with pandas --with odfpy python "
            "sources/dwp-uc-health/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
    return rows


def _claim(row: dict) -> ExternalScore:
    if row["geography"] != "GB" or row["program"] != "universal_credit":
        raise ValueError(f"{SOURCE}: unexpected row {row}")
    metric, unit, value_kind = _METRICS[row["metric"]]
    relationship, _ = uk_relationship(SOURCE, metric, row["program"])
    month = row["period"]
    rate = _RATE_LABELS[row["subgroup"]]
    publication = {
        "title": (
            "Universal Credit Health statistics, Great Britain: April 2019 to "
            "June 2026, Table 2 (LCWRA caseload by entitlement rate)"
        ),
        "publisher": "Department for Work and Pensions",
        "url": _URL,
        "date": "2026-09-15",
        "name": f"UC health element (LCWRA) caseload, {rate}, {month}",
        "boundary": (
            "an administrative outturn staged as a claim by decision "
            "(sources/dwp-uc-health/source.json boundary_note)"
        ),
    }
    if metric == Metric.CASELOAD and row["status"] == "ok":
        # no counterpart until a run on the certified bundle (#87)
        publication["publish_without_result"] = True
    return ExternalScore(
        source=SOURCE,
        source_model=SOURCE_MODEL,
        metric=metric,
        unit_concept=unit,
        period=int(month[:4]),
        time_basis=TimeBasis.POINT_IN_TIME,
        value=row["value"],
        conditions={
            "geography": "GB",
            "country": "UK",
            "program": row["program"],
            "element": "lcwra",
            "lcwra_rate": row["subgroup"],
            "month": month,
            "benchmark_class": "administrative_fact",
        },
        reform=BASELINE,
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication=publication,
        value_kind=value_kind,
        status=row["status"],
    )


def stage() -> list[ExternalScore]:
    return finish([_claim(row) for row in _load()], SOURCE)


def _notes() -> list[str]:
    spec = json.loads((SOURCE_DIR / "annotations.json").read_text())
    out = []
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        out.append(a["text"])
    return out


def results(scores: list[ExternalScore]) -> list[PEResult]:
    staged = json.loads((SOURCE_DIR / "pe" / f"{PE_BUNDLE}.json").read_text())
    prov = staged["provenance"]
    if prov["bundle_id"] != PE_BUNDLE:
        raise ValueError(f"staged read-back is {prov['bundle_id']}, want {PE_BUNDLE}")
    share = staged["new_claimant_share"]
    lower = {
        s.conditions["month"]: s.value
        for s in scores
        if s.metric == Metric.CASELOAD
        and s.conditions["lcwra_rate"] == "lower_new_claimant"
    }
    measured = ", ".join(
        f"{m} {'[low]' if v is None else f'{v:,.0f}'}" for m, v in sorted(lower.items())
    )
    out = []
    for s in scores:
        if s.metric != Metric.AFFECTED_SHARE:
            continue
        year = s.conditions["month"][:4]
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=share["values"][year],
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=prov["engine_version"],
                data_bundle=prov["data_bundle"],
                pe_construction=(
                    f"{staged['pe_construction']} Tax year {year}-"
                    f"{int(year[2:]) + 1} against DWP's {s.conditions['month']}."
                ),
                run_id=staged["run_id"],
                computed_at=staged["computed_at"],
                annotations=_notes()
                + [f"Measured: DWP lower-rate claimants {measured}."],
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=["uc_LCWRA_element"],
            )
        )
    return out


_EXPECTED = {"claims": 16, "suppressed": 1, "results": 1}


def ingest(db_path: Path) -> dict:
    scores = stage()
    pe = results(scores)
    counts = {
        "claims": len(scores),
        "suppressed": sum(s.status == "suppressed" for s in scores),
        "results": len(pe),
    }
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    db = ScorecardDB(db_path)

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE claim_id IN (SELECT claim_id FROM "
            "external_scores WHERE source = ?)",
            (SOURCE,),
        )
        db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        register_baselines_txn(db)
        detail = (
            f"{len(pe)} of {len(scores)} claims computed — DWP's UC health "
            "element (LCWRA) caseload by entitlement rate, April to June 2026 "
            "(Table 2), and the new-claimant rate's June share against PE-UK's "
            f"new_claimant_share ({PE_BUNDLE}); caseload counterparts wait for "
            "a run on the certified bundle; Stat-Xplore element counts open (#87)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return counts


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
