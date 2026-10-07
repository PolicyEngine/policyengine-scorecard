"""Ingest the IRS/Census EITC participation rates and their PE counterparts (#2).

The second US mode-1 source after Urban (lane nta-eitc). Inputs:

    data/externals/irs-eitc-participation.json  the adapter's tidy rows
        (QC'd there: edition match, footnote, CES Tables 1-3 recompute)
    sources/irs-eitc-participation/pe/<bundle>.json  the PE counterparts
        (pipeline/campaign_us/irs_eitc_participation.py: CY2024 tax units,
        forced take-up and filing for eligibility, toggle-verified)
    sources/irs-eitc-participation/annotations.json  notes, each with a basis

Claims (502, every tidy row): the ACS-based State table — participation
rates for 50 States, DC and the nation, tax years 2014-2022 — and the
CPS-based national series: the TY2022 headline (IRS page footnote 2) and
CES-WP-24-75 Tables 1-3 for TY2019-2021 (eligible tax units, taxpayer and
dollar participation rates, eligible dollars at full take-up, non-claimants
and unclaimed dollars by filing route). ``survey_basis`` (acs | cps) keeps
the two national TY2022 figures apart: they differ by method.

PE results attach to the TY2022 taxpayer participation rates (52 ACS rows
and the CPS headline). The CPS TY2019-2021 claims stay registered without a
counterpart: TY2021 is the ARPA year, and TY2019-2020 are three or more
years from the certified data year.

calibration_relationship comes from relationships.us_source_relationship
(the rate and its derived gaps are consumed_as_target — SOI State EITC
claims by children are targets in us-6.2.1; eligibility is held_out).

    PYTHONPATH=. python -m scorecard_db.ingest_irs_eitc_participation data/scorecard.db
"""

from __future__ import annotations

import json
import re
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
from .relationships import us_source_relationship

EXTERNALS = REPO / "data" / "externals"
SOURCE_DIR = REPO / "sources" / "irs-eitc-participation"
ADAPTER_SOURCE = "irs-eitc-participation"
SOURCE = "irs_eitc_participation"
SOURCE_MODEL = "irs_census_exact_match"
PE_BUNDLE = "us-6.2.1"
COMPUTED_PERIOD = 2022

LANE_ID = "nta-eitc"
LANE_UPDATED = "2026-10-06"
FEED_UPDATED = "2026-10-06"
LANE_FEED_META = {
    "source": "IRS/Census",
    "area": "EITC participation",
    "mode": 1,
    "country": "US",
}

STATE_PAGE = {
    "title": "EITC participation rates by state",
    "url": "https://www.irs.gov/tax-professionals/eitc-central/eitc-participation-rate-by-state",
    "date": "2026-10-06 (fetched; TY2022 edition)",
}
CES_PAPER = {
    "title": (
        "EITC Participation Results and IRS-Census Match Methodology, Tax Year 2021"
    ),
    "url": "https://www2.census.gov/library/working-papers/2024/adrm/ces/CES-WP-24-75.pdf",
    "date": "2024-12",
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

# adapter metric -> (Metric, UnitConcept, value_kind, extra conditions, name)
_METRICS = {
    "participation_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        {"rate_unit": "tax_units"},
        "EITC participation rate",
    ),
    "dollar_participation_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        {"rate_unit": "usd"},
        "EITC dollar participation rate",
    ),
    "eligible_count": (
        Metric.ELIGIBLE_COUNT,
        UnitConcept.TAX_UNITS,
        "count",
        {},
        "Tax units eligible for the EITC",
    ),
    "eligible_amount": (
        Metric.BENEFIT_COST,
        UnitConcept.USD,
        "usd",
        {"take_up": "full"},
        "EITC dollars, all eligible units",
    ),
    "participation_gap_count": (
        Metric.PARTICIPATION_GAP_COUNT,
        UnitConcept.TAX_UNITS,
        "count",
        {},
        "Eligible EITC non-claimants",
    ),
    "unclaimed_benefit_amount": (
        Metric.UNCLAIMED_BENEFIT_AMOUNT,
        UnitConcept.USD,
        "usd",
        {},
        "Unclaimed EITC dollars",
    ),
}
_SUBGROUP_NAMES = {
    "non_filers": "non-filers",
    "filers": "filers",
    "filers_claimed_no_eitc": "filers who claimed none",
    "under_claimants": "under-claimants",
}
_BASIS = {None: "acs", "cps": "cps"}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run sources/irs-eitc-participation/adapter.py first"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
        if row["source"] != ADAPTER_SOURCE or row["country"] != "US":
            raise ValueError(f"{SOURCE}: foreign row {row['source_column']!r}")
        if row["program"] != "eitc" or row["variant"] not in _BASIS:
            raise ValueError(f"{SOURCE}: unexpected row {row['source_column']!r}")
    return rows


def _place(row: dict) -> str:
    """'...: New York, Tax year 2022' -> 'New York'; national -> 'United
    States'."""
    if row["geography"] == "US":
        return "United States"
    m = re.search(r": (.+), Tax year \d{4}$", row["source_column"])
    if m is None:
        raise ValueError(f"{SOURCE}: no State name in {row['source_column']!r}")
    return m.group(1)


def _claim(row: dict) -> ExternalScore:
    metric, unit, value_kind, extra, label = _METRICS[row["metric"]]
    value = float(row["value"])
    if value_kind == "share" and not 0.0 < value < 1.0:
        raise ValueError(f"{SOURCE}: rate {value} is not a share ({row})")
    basis = _BASIS[row["variant"]]
    conditions = {
        "geography": row["geography"],
        "program": "eitc",
        "survey_basis": basis,
        **extra,
    }
    name = f"{label}, {_place(row)}"
    if row["subgroup"] != "total":
        conditions["subgroup"] = row["subgroup"]
        name += f", {_SUBGROUP_NAMES[row['subgroup']]}"
    if basis == "cps":
        name += " (CPS)"
    page = CES_PAPER if row["source_column"].startswith("CES-WP") else STATE_PAGE
    return ExternalScore(
        source=SOURCE,
        source_model=SOURCE_MODEL,
        metric=metric,
        unit_concept=unit,
        period=int(row["period"].removeprefix("TY ")),
        time_basis=TimeBasis.ANNUAL,
        value=value,
        conditions=conditions,
        calibration_relationship=us_source_relationship(SOURCE, "eitc", metric)[0],
        source_column=row["source_column"],
        publication={**page, "name": name, "window": row["period"]},
        value_kind=value_kind,
        status=row["status"],
    )


def stage() -> list[ExternalScore]:
    rows = _load()
    scores = [_claim(r) for r in rows]
    if len(scores) != len(rows):
        raise ValueError(f"{SOURCE}: {len(rows) - len(scores)} rows left unmapped")
    return finish(scores, SOURCE)


def _annotations(metric: str, seed_note: str) -> list[str]:
    spec = json.loads((SOURCE_DIR / "annotations.json").read_text())
    out = []
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        if set(a["applies_to"]) - {"program", "metrics"}:
            raise ValueError(f"annotation {a['id']}: unknown matcher")
        metrics = a["applies_to"].get("metrics")
        if metrics is not None and metric not in metrics:
            continue
        out.append(
            f"{a['text']} {seed_note}" if a["id"] == "eitc-takeup-seed" else a["text"]
        )
    return out


def _seed_note(staged: dict) -> str:
    """The measured post-calibration rates by qualifying children."""
    by = staged["national_by_children"]
    rates = ", ".join(
        f"{by[b]['participation_rate']:.1%}" for b in ("0", "1", "2", "3+")
    )
    return (
        f"Measured: after calibration, PolicyEngine's {staged['period']} rates "
        f"by number of children are {rates}."
    )


def results(scores: list[ExternalScore]) -> list[PEResult]:
    staged = json.loads((SOURCE_DIR / "pe" / f"{PE_BUNDLE}.json").read_text())
    prov = staged["provenance"]
    if prov["bundle_id"] != PE_BUNDLE:
        raise ValueError(f"staged PE file is {prov['bundle_id']}, want {PE_BUNDLE}")
    geos = staged["geographies"]
    seed = _seed_note(staged)
    out = []
    for s in scores:
        if not (
            s.period == COMPUTED_PERIOD
            and s.metric == Metric.PARTICIPATION_RATE
            and s.conditions["rate_unit"] == "tax_units"
        ):
            continue
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=float(
                    geos[s.conditions["geography"]]["participation_rate"]
                ),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=prov["engine_version"],
                data_bundle=prov["data_bundle"],
                pe_construction=staged["pe_construction"],
                run_id=staged["run_id"],
                computed_at=staged["computed_at"],
                annotations=_annotations(s.metric.value, seed),
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=staged["policyengine_variables"],
            )
        )
    return out


_EXPECTED = {"claims": 502, "results": 53}


def ingest(db_path: Path) -> dict:
    scores = stage()
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
            f"{len(pe)} of {len(scores)} claims computed — IRS/Census EITC "
            "participation: ACS State table TY2014-2022 and the CPS national "
            "series (TY2022 headline; CES-WP-24-75 TY2019-2021 eligibility, "
            "non-claimants, unclaimed dollars); TY2022 rates compared with PE "
            "CY2024 on us-6.2.1; numerator calibrated (SOI State claims by "
            "children), eligibility held out"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    by_metric = Counter(s.metric.value for s in scores)
    return {**counts, "by_metric": dict(sorted(by_metric.items()))}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
