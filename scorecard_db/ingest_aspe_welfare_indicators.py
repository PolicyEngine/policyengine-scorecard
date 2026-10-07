"""Ingest ASPE Welfare Indicators (Indicator 4) and their PE counterparts (#2).

Lane aspe-welfare-indicators. Inputs:

    data/externals/aspe-welfare-indicators.json  the adapter's tidy rows
        (QC'd there: every rate recomputes from its counts; the 24th and
        25th editions agree cell for cell)
    sources/aspe-welfare-indicators/pe/<bundle>.json  the PE counterparts
        (pipeline/campaign_us/aspe_welfare_indicators.py)
    sources/aspe-welfare-indicators/annotations.json  notes with a basis

Claims: Tables 10-12 — TANF families (TRIM3), SNAP households (FNS series),
SSI adult units by category (TRIM3): eligible counts, participation rates,
and the TRIM3 participant counts. SNAP participating households are FNS
program-operations counts — an administrative outturn — and are dropped
with a tally (the 2026-08-02 boundary rule). Suppressed cells ("no data",
"n.a.") stay as suppressed claims.

PE results attach to the latest period of each series (TANF 2023, SNAP
FY 2022, SSI 2023). The TANF counts are concept_mismatch — PE's are
any-time-in-year SPM units, ASPE's average-month TRIM3 units — and only the
TANF rate is constructed. calibration_relationship comes from
relationships.effective_relationship: TANF rate and participants seed_source
(the take-up flag is seeded from this table), SNAP and SSI rates and SSI
participants consumed_as_target, every eligible count held_out.

    PYTHONPATH=. python -m scorecard_db.ingest_aspe_welfare_indicators data/scorecard.db
"""

from __future__ import annotations

import json
from collections import Counter
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
from .relationships import effective_relationship

EXTERNALS = REPO / "data" / "externals"
SOURCE_DIR = REPO / "sources" / "aspe-welfare-indicators"
ADAPTER_SOURCE = "aspe-welfare-indicators"
SOURCE = "aspe_welfare_indicators"
PE_BUNDLE = "us-6.2.1"

LANE_ID = "aspe-welfare-indicators"
LANE_UPDATED = "2026-10-07"
FEED_UPDATED = "2026-10-07"
LANE_FEED_META = {
    "source": "ASPE",
    "area": "TANF/SSI/SNAP participation among the eligible",
    "mode": 1,
    "country": "US",
}

PUBLICATION = {
    "title": "Welfare Indicators and Risk Factors: 25th Report to Congress",
    "url": "https://aspe.hhs.gov/reports/welfare-indicators-risk-factors-twenty-fifth-report-congress",
    "date": "2026-04",
}

_KNOWN_FIELDS = frozenset(
    {
        "country",
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
        "variant",
    }
)
_UNITS = {
    "families": UnitConcept.FAMILIES,
    "households": UnitConcept.HOUSEHOLDS,
    "benefit_units": UnitConcept.BENEFIT_UNITS,
}
_METRICS = {
    "eligible_count": Metric.ELIGIBLE_COUNT,
    "participant_count": Metric.PARTICIPANT_COUNT,
    "participation_rate": Metric.PARTICIPATION_RATE,
}
_PROGRAM_NAMES = {"tanf": "TANF", "snap": "SNAP", "ssi": "SSI"}
_UNIT_NAMES = {
    "families": "families",
    "households": "households",
    "benefit_units": "units",
}
_SSI_NAMES = {
    "aged_65plus_individuals": "aged 65+ individuals",
    "disabled_individuals": "disabled individuals",
    "couples": "married couples",
}
# the latest period of each series, where PE results attach
_COMPUTED = {"tanf": "2023", "snap": "FY 2022", "ssi": "2023"}
_MONTHS = ("September", "August", "February")


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — run the adapter first")
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
        if row["source"] != ADAPTER_SOURCE or row["variant"] is not None:
            raise ValueError(f"{SOURCE}: unexpected row {row['source_column']!r}")
    return rows


def _period(label: str) -> tuple[int, TimeBasis, dict]:
    if label.startswith("FY "):
        return (
            int(label[3:]),
            TimeBasis.AVERAGE_MONTH,
            {"year_basis": "federal_fiscal_year"},
        )
    month, _, year = label.partition(" ")
    if month in _MONTHS:
        return int(year), TimeBasis.POINT_IN_TIME, {"reference_month": month}
    return int(label), TimeBasis.AVERAGE_MONTH, {}


def _name(row: dict) -> str:
    prog, unit = _PROGRAM_NAMES[row["program"]], _UNIT_NAMES[row["unit_concept"]]
    metric = row["metric"]
    if metric == "participation_rate":
        name = f"{prog} participation rate ({unit})"
    elif metric == "eligible_count":
        name = f"{prog} {unit} eligible"
    else:
        name = f"{prog} {unit} participating"
    if row["program"] == "ssi":
        name += f", {_SSI_NAMES[row['subgroup']]}"
    return name


def _claim(row: dict) -> ExternalScore:
    metric = _METRICS[row["metric"]]
    period, basis, extra = _period(row["period"])
    conditions = {"geography": "US", "program": row["program"], **extra}
    if row["subgroup"] != "total":
        conditions["subgroup"] = row["subgroup"]
    if metric == Metric.PARTICIPATION_RATE:
        conditions["rate_unit"] = row["unit_concept"]
        unit, kind = UnitConcept.SHARE, "share"
    else:
        unit, kind = _UNITS[row["unit_concept"]], "count"
    return ExternalScore(
        source=SOURCE,
        source_model="trim3" if row["program"] in ("tanf", "ssi") else "fns_snap_rates",
        metric=metric,
        unit_concept=unit,
        period=period,
        time_basis=basis,
        value=row["value"],
        conditions=conditions,
        calibration_relationship=effective_relationship(row["program"], metric)[0],
        source_column=row["source_column"],
        publication={**PUBLICATION, "name": _name(row), "window": row["period"]},
        value_kind=kind,
        status=row["status"],
    )


def stage() -> tuple[list[ExternalScore], dict]:
    scores, drops = [], Counter()
    for row in _load():
        if row["program"] == "snap" and row["metric"] == "participant_count":
            drops["admin:snap_participating_households"] += 1
            continue
        scores.append(_claim(row))
    return finish(scores, SOURCE), dict(drops)


def _annotations(program: str, metric: str, notes: dict) -> list[str]:
    spec = json.loads((SOURCE_DIR / "annotations.json").read_text())
    out = []
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        match = a["applies_to"]
        if match.get("program") not in (None, program):
            continue
        if match.get("metrics") is not None and metric not in match["metrics"]:
            continue
        extra = notes.get(a["id"])
        out.append(f"{a['text']} {extra}" if extra else a["text"])
    return out


def results(scores: list[ExternalScore]) -> list[PEResult]:
    staged = json.loads((SOURCE_DIR / "pe" / f"{PE_BUNDLE}.json").read_text())
    prov = staged["provenance"]
    if prov["bundle_id"] != PE_BUNDLE:
        raise ValueError(f"staged PE file is {prov['bundle_id']}, want {PE_BUNDLE}")
    series = staged["series"]
    flag = series["tanf"]["takeup_flag_mean_among_eligible"]
    notes = {
        "aspe-tanf-seed": (
            f"Measured: the flag is on for {flag:.1%} of PolicyEngine's eligible "
            f"units (unweighted); the weighted rate is "
            f"{series['tanf']['participation_rate']:.1%}."
        )
    }
    out = []
    for s in scores:
        program = s.conditions["program"]
        if s.status != "ok" or s.publication["window"] != _COMPUTED[program]:
            continue
        key = (
            program
            if program != "ssi"
            else {
                "aged_65plus_individuals": "ssi_aged",
                "disabled_individuals": "ssi_disabled",
                "couples": "ssi_couples",
            }[s.conditions["subgroup"]]
        )
        status = ComparisonStatus.CONSTRUCTED
        if program == "tanf" and s.metric != Metric.PARTICIPATION_RATE:
            status = ComparisonStatus.CONCEPT_MISMATCH
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=float(series[key][s.metric.value]),
                status=status,
                engine_version=prov["engine_version"],
                data_bundle=prov["data_bundle"],
                pe_construction=staged["pe_construction"][
                    "ssi" if program == "ssi" else program
                ],
                run_id=staged["run_id"],
                computed_at=staged["computed_at"],
                annotations=_annotations(program, s.metric.value, notes),
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=staged["policyengine_variables"],
            )
        )
    return out


_EXPECTED = {"claims": 476, "results": 14}


def ingest(db_path: Path) -> dict:
    scores, drops = stage()
    pe = results(scores)
    counts = {"claims": len(scores), "results": len(pe)}
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    db = ScorecardDB(db_path)

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE claim_id IN "
            "(SELECT claim_id FROM external_scores WHERE source = ?)",
            (SOURCE,),
        )
        db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        register_baselines_txn(db)
        detail = (
            f"{len(pe)} of {len(scores)} claims computed — ASPE Indicator 4: "
            "TANF families 1981-2023 and SSI adult units 1993-2023 (TRIM3), "
            "SNAP households 1976-FY2022 (FNS series); latest periods compared "
            "with PE CY2024 on us-6.2.1; rates recomputed from counts and the "
            "24th/25th editions agree"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {**counts, "drops": drops}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
