"""Ingest the Census STC individual income tax collections and their PE
counterparts (lane census-stc, issue #176).

The Census Annual Survey of State Government Tax Collections publishes each
State's tax collections in its fiscal year; item T40 is individual income
taxes. Inputs:

    data/externals/census-stc.json  the adapter's tidy rows (QC'd there)
    sources/census-stc/pe/<bundle>.json  the PE counterparts
        (pipeline/campaign_us/census_stc.py: weighted CY2024 total of each
        State's own income tax variable, checked equal to
        state_income_tax over the State's tax units)
    sources/census-stc/annotations.json  concept deltas, each with a basis

Claims: tax_collections for the 44 jurisdictions with an income tax in the
engine (41 States, DC, New Hampshire and Washington), fiscal years 2023-2025
(132). ``program`` is the State's own engine variable (``vt_income_tax``):
App v3 matches a reform's reached variables against ``program`` and
``policyengine_variables``, and ``state_income_tax`` is reached by every
State's reform, so only the per-State name keeps a Vermont reform on
Vermont's claims.

PE results attach to FY2025, the latest year, and to FY2023, the year
us-6.2.1 calibrates to (its in-sample fit) — 88. FY2024 stays registered
without a counterpart.

Boundary note: STC collections are administrative outturns, which the
2026-08-02 boundary ruling (issue #6) routes to Chronicle rather than to
claims. They are claims here by decision on #176 (2026-10-15), so that
App v3 can show a baseline check for every State income tax reform; the
populace registry's ``<st>_admin`` and ``irs_soi`` rows are the precedent.

Deliberate drops, tallied (all still in data/externals):
    - the national total (the issue asks for one claim per State; a
      national claim would match every State's reform in App v3)
    - Tennessee: residual Hall-tax collections, no engine variable

calibration_relationship comes from relationships.us_source_relationship:
FY2023 is consumed_as_target, FY2024 and FY2025 are held_out.

    PYTHONPATH=. python -m scorecard_db.ingest_census_stc data/scorecard.db
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, require_fields, state_name
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
SOURCE_DIR = REPO / "sources" / "census-stc"
ADAPTER_SOURCE = "census-stc"
SOURCE = "census_stc"
SOURCE_MODEL = "census_stc_survey"
PE_BUNDLE = "us-6.2.1"
COMPUTED_PERIODS = (2023, 2025)  # the fiscal years PE results attach to

LANE_ID = "census-stc"
LANE_UPDATED = "2026-10-15"
FEED_UPDATED = "2026-10-15"
LANE_FEED_META = {
    "source": "Census STC",
    "area": "State individual income tax collections",
    "mode": 1,
    "country": "US",
}

PUBLICATION = {
    "title": "Annual Survey of State Government Tax Collections",
    "url": "https://www.census.gov/programs-surveys/stc.html",
    "date": "2026-04",
    "vintage": "FY2023-FY2025 as released April 2026 (fetched 2026-10-15)",
}

_KNOWN_FIELDS = frozenset(
    {
        "country",
        "geography",
        "item",
        "metric",
        "period",
        "source",
        "source_column",
        "status",
        "unit_concept",
        "value",
    }
)
# Fiscal years end on June 30 except in these States (technical
# documentation, "Fiscal Years").
_FY_END = {
    "NY": "March 31",
    "TX": "August 31",
    "AL": "September 30",
    "MI": "September 30",
}
_DROPPED = {"US": "national_total", "TN": "no_engine_variable:TN"}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run python sources/census-stc/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
    return rows


def _claim(row: dict) -> ExternalScore:
    if row["item"] != "T40" or row["metric"] != "tax_collections":
        raise ValueError(f"{SOURCE}: unexpected item/metric {row}")
    code = row["geography"]
    year = int(row["period"].removeprefix("FY "))
    program = f"{code.lower()}_income_tax"
    relationship, _ = us_source_relationship(
        SOURCE, program, Metric.TAX_COLLECTIONS, year
    )
    return ExternalScore(
        source=SOURCE,
        source_model=SOURCE_MODEL,
        metric=Metric.TAX_COLLECTIONS,
        unit_concept=UnitConcept.USD,
        period=year,
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions={
            "geography": code,
            "program": program,
            "line_item": "T40",
            "period_basis": "state_fiscal_year",
        },
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication={
            **PUBLICATION,
            "name": f"Individual income tax collections, {state_name(code)}",
            "window": (
                f"FY {year} (12 months ending {_FY_END.get(code, 'June 30')}, {year})"
            ),
        },
        value_kind="usd",
        status=row["status"],
    )


def stage() -> tuple[list[ExternalScore], dict]:
    """(claims, drop tally)."""
    scores: list[ExternalScore] = []
    drops: Counter = Counter()
    for row in _load():
        if row["geography"] in _DROPPED:
            drops[_DROPPED[row["geography"]]] += 1
            continue
        scores.append(_claim(row))
    return finish(scores, SOURCE), dict(sorted(drops.items()))


def _annotations(period: int, geography: str) -> list[str]:
    spec = json.loads((SOURCE_DIR / "annotations.json").read_text())
    out = []
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        match = a["applies_to"]
        if set(match) - {"periods", "geographies"}:
            raise ValueError(f"annotation {a['id']}: unknown matcher {match}")
        periods, geographies = match.get("periods"), match.get("geographies")
        if periods is not None and period not in periods:
            continue
        if geographies is not None and geography not in geographies:
            continue
        out.append(a["text"])
    return out


def results(scores: list[ExternalScore]) -> list[PEResult]:
    staged = json.loads((SOURCE_DIR / "pe" / f"{PE_BUNDLE}.json").read_text())
    prov = staged["provenance"]
    if prov["bundle_id"] != PE_BUNDLE:
        raise ValueError(f"staged PE file is {prov['bundle_id']}, want {PE_BUNDLE}")
    geos = staged["geographies"]
    out = []
    for s in scores:
        if s.period not in COMPUTED_PERIODS:
            continue
        code = s.conditions["geography"]
        notes = _annotations(s.period, code)
        calibration = geos[code].get("calibration")
        if s.period == 2023:
            if calibration is None or calibration["target"] != s.value:
                raise ValueError(f"{SOURCE}: {code} FY2023 is not the target value")
            notes.append(
                f"Measured: the us-6.2.1 calibration's estimate for this "
                f"target is ${calibration['final_estimate'] / 1e6:,.0f} million "
                f"against ${calibration['target'] / 1e6:,.0f} million."
            )
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=float(geos[code]["state_income_tax"]),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=prov["engine_version"],
                data_bundle=prov["data_bundle"],
                pe_construction=staged["pe_construction"],
                run_id=staged["run_id"],
                computed_at=staged["computed_at"],
                annotations=notes,
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=[s.conditions["program"]],
            )
        )
    return out


_EXPECTED = {"claims": 132, "results": 88}


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
            f"{len(pe)} of {len(scores)} claims computed — State individual "
            "income tax collections (T40) for 41 States, DC, NH and WA, FY2023-"
            "FY2025; FY2023 (a us-6.2.1 calibration target) and FY2025 "
            "compared with PE's CY2024 State income tax on us-6.2.1; adapter QC "
            "checks the US column against the 50 States on all 25 items; "
            "admin outturns staged as claims by decision on #176"
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
