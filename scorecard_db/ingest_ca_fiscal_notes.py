"""Ingest California fiscal notes and their PE counterparts (lane
ca-fiscal-notes, issue #4).

The first dedicated State fiscal-note lane. FTB estimates, restated in the
Assembly Revenue and Taxation Committee analyses, of the General Fund
revenue change from young child tax credit (YCTC) bills, by State fiscal
year. Inputs:

    data/externals/ca-fiscal-notes.json  the adapter's tidy rows (QC'd there)
    sources/ca-fiscal-notes/pe/<bundle>.json  the PE counterparts
        (pipeline/campaign_us/ca_fiscal_notes.py: reform-minus-baseline
        ca_income_tax with the YCTC age limit set year by year)
    sources/ca-fiscal-notes/annotations.json  concept deltas, each with a basis

Claims: 5 revenue changes — AB 397 (FY 2025-26 to 2027-28) and AB 1690
(FY 2027-28 and 2028-29), each for the bill as introduced. The source is
``ca_fiscal_note``, the slug the reform-validation registry's California
claim (AB 2591) already uses; this lane owns only its own rows (source
model ``ftb_revenue_estimate``), never the registry's.

Every claim gets a result: the fiscal year's revenue change against the
tax year whose returns are filed in it (FY 2025-26 <- tax year 2025),
``constructed``. ``program`` is ``ca_yctc``, so App v3 links a YCTC reform
to these claims.

    PYTHONPATH=. python -m scorecard_db.ingest_ca_fiscal_notes data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields
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
SOURCE_DIR = REPO / "sources" / "ca-fiscal-notes"
ADAPTER_SOURCE = "ca-fiscal-notes"
SOURCE = "ca_fiscal_note"
SOURCE_MODEL = "ftb_revenue_estimate"
PROGRAM = "ca_yctc"
PE_BUNDLE = "us-6.2.1"

LANE_ID = "ca-fiscal-notes"
LANE_UPDATED = "2026-10-19"
FEED_UPDATED = "2026-10-19"
LANE_FEED_META = {
    "source": "CA FTB",
    "area": "State fiscal notes (YCTC bills)",
    "mode": 2,
    "country": "US",
}

_KNOWN_FIELDS = frozenset(
    {
        "age_schedule",
        "authors",
        "bill",
        "country",
        "estimator",
        "geography",
        "hearing_date",
        "metric",
        "period",
        "publisher",
        "source",
        "source_column",
        "status",
        "unit_concept",
        "value",
        "version",
        "version_date",
    }
)
_URLS = {
    "AB 397": "https://arev.assembly.ca.gov/media/898",
    "AB 1690": "https://arev.assembly.ca.gov/media/969",
}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run uv run --with pypdf python "
            "sources/ca-fiscal-notes/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
    return rows


def bill_slug(bill: str) -> str:
    """'AB 397' -> 'ab397' (the registry's state.ca.<bill> form)."""
    return bill.replace(" ", "").lower()


def _fiscal_year(period: str) -> tuple[str, int]:
    """'FY 2025-26' -> ('2025-26', 2026): the period is the end year."""
    fy = period.removeprefix("FY ")
    return fy, int(fy[:4]) + 1


def _claim(row: dict) -> ExternalScore:
    if row["metric"] != "revenue_change" or row["geography"] != "CA":
        raise ValueError(f"{SOURCE}: unexpected row {row}")
    fy, period = _fiscal_year(row["period"])
    relationship, _ = us_source_relationship(SOURCE, PROGRAM, Metric.REVENUE_CHANGE)
    return ExternalScore(
        source=SOURCE,
        source_model=SOURCE_MODEL,
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.USD,
        period=period,
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions={
            "geography": "CA",
            "program": PROGRAM,
            "fy": fy,
            "period_basis": "state_fiscal_year",
            "measure": f"{row['bill']} (as introduced {row['version_date']})",
        },
        reform=policy_ref(
            f"state.ca.{bill_slug(row['bill'])}",
            version=f"{row['version']}_{row['version_date']}",
        ),
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication={
            "title": (
                f"Assembly Committee on Revenue and Taxation analysis of "
                f"{row['bill']} ({row['authors']}), as introduced "
                f"{row['version_date']}; hearing {row['hearing_date']}"
            ),
            "url": _URLS[row["bill"]],
            "date": row["hearing_date"],
            "name": f"CA {row['bill']} — young child tax credit age limit",
            "window": f"FY {fy}",
            "estimator": row["estimator"],
        },
        value_kind="usd",
        status=row["status"],
    )


def stage() -> list[ExternalScore]:
    return finish([_claim(row) for row in _load()], SOURCE)


def _annotations() -> list[str]:
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
        raise ValueError(f"staged PE file is {prov['bundle_id']}, want {PE_BUNDLE}")
    out = []
    for s in scores:
        bill = s.reform.reform["policy"].removeprefix("state.ca.")
        tax_year = str(s.period - 1)
        cell = staged["bills"][bill][tax_year]
        base = staged["baseline"][tax_year]
        notes = _annotations() + [
            f"Measured: PolicyEngine tax year {tax_year} with the age limit at "
            f"{cell['ineligible_age']:.0f}: {cell['yctc_units_change'] / 1e3:,.0f} "
            f"thousand more tax units with a YCTC and "
            f"${cell['yctc_change'] / 1e6:,.0f} million more credit, on a "
            f"baseline YCTC of ${base['ca_yctc'] / 1e6:,.0f} million."
        ]
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=float(cell["revenue_change"]),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=prov["engine_version"],
                data_bundle=prov["data_bundle"],
                pe_construction=(
                    f"{staged['pe_construction']} Fiscal year "
                    f"{s.conditions['fy']} <- tax year {tax_year}."
                ),
                run_id=staged["run_id"],
                computed_at=staged["computed_at"],
                annotations=notes,
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=[PROGRAM],
            )
        )
    return out


_EXPECTED = {"claims": 5, "results": 5}


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
        # this lane's rows only: the registry's ca_fiscal_note claim stays
        db.conn.execute(
            "DELETE FROM pe_results WHERE claim_id IN (SELECT claim_id FROM "
            "external_scores WHERE source = ? AND source_model = ?)",
            (SOURCE, SOURCE_MODEL),
        )
        db.conn.execute(
            "DELETE FROM external_scores WHERE source = ? AND source_model = ?",
            (SOURCE, SOURCE_MODEL),
        )
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        register_baselines_txn(db)
        detail = (
            f"{len(pe)} of {len(scores)} claims computed — FTB revenue "
            "estimates for the young child tax credit bills AB 397 and AB 1690 "
            "(as introduced; via Assembly Revenue and Taxation analyses), "
            "against PE's reform-minus-baseline ca_income_tax for the tax "
            "year filed in each fiscal year, on us-6.2.1; LAO CalWORKs costs "
            "and LAO ranges are later tranches"
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
