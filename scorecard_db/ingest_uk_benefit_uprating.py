"""Ingest the September 2026 CPI claims and PolicyEngine-UK's benefit-rate
read-backs (lane uk-benefit-uprating).

Most working-age benefits rise each April by the September CPI rate. This
lane stages that rate and checks the rates PolicyEngine-UK holds against the
upratings already published. Inputs:

    data/externals/uk-benefit-uprating.json  the adapter's tidy rows
    sources/uk-benefit-uprating/pe/<bundle>.json  the parameter-tree read-back
        (pipeline/compute_uk_uprating_readback.py)
    sources/uk-benefit-uprating/annotations.json  notes, each with a basis

Claims (2, this lane's own): the ONS CPI rate for September 2026 (an
outturn staged as a claim by decision; see source.json) and OBR's March
2026 forecast for 2026 Q3. Their counterpart is the rise PolicyEngine-UK
applies to CPI-linked working-age rates in April 2027, ``constructed``.

Results attached to other lanes' claims, never editing them:
    hm_treasury            4  Budget 2025 April 2026 upratings
    resolution_foundation 11  April 2025 to April 2029 upratings
Each is the year-on-year rise of the matching rate, ``comparable``.

    PYTHONPATH=. python -m scorecard_db.ingest_uk_benefit_uprating data/scorecard.db
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
SOURCE_DIR = REPO / "sources" / "uk-benefit-uprating"
ADAPTER_SOURCE = "uk-benefit-uprating"
PE_BUNDLE = "uk-2.147.2"
RUN_PREFIX = "uk-uprating-readback-"

LANE_ID = "uk-benefit-uprating"
LANE_UPDATED = "2026-10-22"
FEED_UPDATED = "2026-10-22"
LANE_FEED_META = {
    "source": "ONS + OBR + HMT + RF",
    "area": "benefit uprating and September CPI",
    "mode": 1,
    "country": "UK",
}

_KNOWN_FIELDS = frozenset(
    {
        "calendar_year_value",
        "geography",
        "metric",
        "period",
        "publisher",
        "release_date",
        "series",
        "source",
        "source_column",
        "status",
        "unit_concept",
        "value",
    }
)
_SOURCE_MODEL = {"ons_cpi": "ons_d7g7", "obr_efo_economy": "obr_efo_forecast"}
_ONS_URL = (
    "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7g7/mm23"
)
_OBR_URL = (
    "https://obr.uk/download/"
    "march-2026-economic-and-fiscal-outlook-detailed-forecast-tables-economy/"
)
_OBR_WAYBACK = (
    "https://web.archive.org/web/20260423152500id_/https://obr.uk/docs/"
    "d055fbf02d5b3g6jq8l2/efo-march-2026-detailed-forecast-tables-economy.xlsx"
)

# The variables each read rate feeds, so App v3 links a reform to the claim.
CPI_BASKET_VARIABLES = [
    "uc_child_element",
    "uc_carer_element",
    "child_benefit",
    "carers_allowance",
    "pip_dl",
]
SA_VARIABLES = ["uc_standard_allowance"]

# Existing claims -> the read-back that answers them. HM Treasury claims are
# keyed by their reform policy and stated in percent; Resolution Foundation
# claims by (benefit, fy) and stated as shares.
HMT_MAP = {
    "hm_treasury:Working-age benefits uprated by September 2025 CPI": (
        "uc_child_element",
        "2026",
    ),
    "hm_treasury:UC Standard Allowance uprating in line with the UC Act 2025": (
        "uc_sa_single_25plus",
        "2026",
    ),
    "hm_treasury:State Pension uprating April 2026 under the Triple Lock": (
        "new_state_pension",
        "2026",
    ),
    "hm_treasury:Pension Credit Standard Minimum Guarantee uprating April 2026": (
        "pension_credit_mg_single",
        "2026",
    ),
}
RF_MAP = {
    ("universal_credit_standard_allowance", "2025-26"): ("uc_sa_single_25plus", "2025"),
    ("universal_credit_standard_allowance", "2026-27"): ("uc_sa_single_25plus", "2026"),
    ("universal_credit_standard_allowance", "2027-28"): ("uc_sa_single_25plus", "2027"),
    ("universal_credit_standard_allowance", "2028-29"): ("uc_sa_single_25plus", "2028"),
    ("universal_credit_standard_allowance", "2029-30"): ("uc_sa_single_25plus", "2029"),
    ("universal_credit_standard_allowance_under_25", "2026-27"): (
        "uc_sa_single_u25",
        "2026",
    ),
    ("inflation_linked_benefits", "2026-27"): ("uc_child_element", "2026"),
    ("state_pension", "2026-27"): ("new_state_pension", "2026"),
    ("universal_credit_health_element", "2026-27"): (
        "protected_health_element",
        "2026",
    ),
    ("local_housing_allowance", "2026-27"): ("lha", "2026"),
}
_VARIABLES = {
    "uc_sa_single_25plus": SA_VARIABLES,
    "uc_sa_single_u25": SA_VARIABLES,
    "uc_child_element": CPI_BASKET_VARIABLES,
    "new_state_pension": ["state_pension"],
    "pension_credit_mg_single": ["pension_credit"],
    "protected_health_element": ["uc_LCWRA_element"],
    "lha": ["LHA_cap"],
}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run uv run --with openpyxl python "
            "sources/uk-benefit-uprating/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, ADAPTER_SOURCE)
    return rows


def _claim(row: dict) -> ExternalScore:
    source = row["source"]
    if row["metric"] != "cpi_inflation_rate" or row["geography"] != "UK":
        raise ValueError(f"{ADAPTER_SOURCE}: unexpected row {row}")
    relationship, _ = uk_relationship(source, Metric.CPI_INFLATION_RATE)
    conditions = {
        "geography": "UK",
        "country": "UK",
        "uprating_event": "April 2027",
    }
    if source == "ons_cpi":
        conditions |= {
            "month": "2026-09",
            "index": "CPI all items, 12-month rate (ONS D7G7)",
            "benchmark_class": "administrative_fact",
        }
        publication = {
            "title": "Consumer price inflation, UK: September 2026 (series D7G7)",
            "publisher": row["publisher"],
            "url": _ONS_URL,
            "date": row["release_date"],
            "name": "September 2026 CPI, the April 2027 uprating rate",
            "boundary": (
                "an official outturn staged as a claim by decision "
                "(sources/uk-benefit-uprating/source.json boundary_note)"
            ),
        }
    elif source == "obr_efo_economy":
        conditions |= {
            "quarter": "2026Q3",
            "index": "CPI all items, year-on-year growth (OBR Table 1.7)",
            "basis": "forecast",
            "fiscal_event": "efo_march_2026",
        }
        publication = {
            "title": (
                "Economic and fiscal outlook March 2026, detailed forecast "
                "tables: economy, Table 1.7"
            ),
            "publisher": row["publisher"],
            "url": _OBR_URL,
            "wayback": _OBR_WAYBACK,
            "date": "2026-03-03",
            "name": "OBR March 2026 forecast of CPI inflation, 2026 Q3",
            "calendar_year_2026": f"{row['calendar_year_value']:.3f}",
        }
    else:
        raise ValueError(f"{ADAPTER_SOURCE}: unknown source {source!r}")
    return ExternalScore(
        source=source,
        source_model=_SOURCE_MODEL[source],
        metric=Metric.CPI_INFLATION_RATE,
        unit_concept=UnitConcept.PERCENT,
        period=2026,
        time_basis=TimeBasis.POINT_IN_TIME,
        value=float(row["value"]),
        conditions=conditions,
        reform=BASELINE,
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication=publication,
        value_kind="percent",
        status=row["status"],
    )


def stage() -> list[ExternalScore]:
    return finish([_claim(row) for row in _load()], ADAPTER_SOURCE)


def _readback() -> dict:
    staged = json.loads((SOURCE_DIR / "pe" / f"{PE_BUNDLE}.json").read_text())
    if staged["provenance"]["bundle_id"] != PE_BUNDLE:
        raise ValueError(
            f"staged read-back is {staged['provenance']['bundle_id']}, want {PE_BUNDLE}"
        )
    return staged


def _notes(*ids: str) -> list[str]:
    spec = json.loads((SOURCE_DIR / "annotations.json").read_text())
    by_id = {}
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        by_id[a["id"]] = a["text"]
    return [by_id[i] for i in ids]


def rise(staged: dict, key: str, year: str) -> float:
    """The April rise (a fraction) that answers a claim."""
    if key == "protected_health_element":
        if year != "2026":
            raise ValueError("the protected amount's base is 2025-26's LCWRA")
        base = staged["rates"]["uc_lcwra_element"]["values"]["2025"]
        return staged["protected_health_element_monthly"]["2026"] / base - 1
    if key == "lha":
        if not staged["lha_freeze"][year]:
            raise ValueError(f"LHA not frozen in {year}: rates are rent-derived")
        return 0.0
    return staged["rates"][key]["rises"][year]


def basket_rise(staged: dict, year: str) -> tuple[float, float, float]:
    """(UC child element rise, basket min, basket max) for one April."""
    rises = [staged["rates"][k]["rises"][year] for k in staged["cpi_basket"]]
    return staged["rates"]["uc_child_element"]["rises"][year], min(rises), max(rises)


def _result(staged: dict, claim_id: str, value: float, status, notes, variables):
    prov = staged["provenance"]
    return PEResult(
        claim_id=claim_id,
        computed_value=value,
        status=status,
        engine_version=prov["engine_version"],
        data_bundle=prov["data_bundle"],
        pe_construction=staged["pe_construction"],
        run_id=staged["run_id"],
        computed_at=staged["computed_at"],
        annotations=notes,
        baseline_key=BASELINE.baseline_key(),
        policyengine_variables=variables,
    )


def _measured(staged: dict, key: str, year: str) -> str:
    if key == "uc_child_element":
        child, lo, hi = basket_rise(staged, year)
        return (
            f"Measured: the UC child element rises {child:.2%} in April {year}; "
            f"the CPI-linked working-age basket ({', '.join(staged['cpi_basket'])}) "
            f"rises {lo:.2%} to {hi:.2%} (rates rounded to the penny)."
        )
    if key == "protected_health_element":
        amount = staged["protected_health_element_monthly"][year]
        return f"Measured: the protected health element is £{amount:.2f} a month in {year}-{int(year[2:]) + 1}."
    if key == "lha":
        return f"Measured: gov.dwp.LHA.freeze is true for {year}-{int(year[2:]) + 1}."
    return f"Measured: {staged['rates'][key]['path']} rises {rise(staged, key, year):.2%} in April {year}."


def own_results(scores: list[ExternalScore], staged: dict) -> list[PEResult]:
    child, lo, hi = basket_rise(staged, "2027")
    if hi - lo > 1e-9:
        raise ValueError(f"April 2027 basket rises differ: {lo} to {hi}")
    sa = staged["rates"]["uc_sa_single_25plus"]["rises"]["2027"]
    protected = staged["protected_health_element_monthly"]
    september = staged["september_cpi"]["2026"]
    entered = staged["september_2026_entered"]
    detail = [
        (
            f"Measured: CPI-linked working-age rates rise {child:.2%} in "
            f"April 2027 on {PE_BUNDLE}. The UC standard allowance rises "
            f"{sa:.2%} (CPI plus the Act's uplift); the protected health "
            f"element rises {protected['2027'] / protected['2026'] - 1:.2%} to "
            f"£{protected['2027']:.2f} a month; the new-claimant health element "
            "is frozen."
        ),
        (
            f"The model's own September 2026 CPI is {september:.2%} "
            + (
                "(an entered outturn)."
                if entered
                else "(a forecast; no outturn entered)."
            )
        ),
    ]
    out = []
    for s in scores:
        notes = (
            _notes(
                "uk-uprating-tree-only",
                "uk-uprating-benefit-index",
                "uk-uprating-september-forecast",
            )
            + detail
        )
        if s.source == "ons_cpi":
            notes.append(
                f"With the ONS rate, CPI-linked working-age rates would rise "
                f"{s.value:.1f}% in April 2027, {s.value - 100 * child:.1f} "
                "points above PolicyEngine-UK's baseline."
            )
        out.append(
            _result(
                staged,
                s.claim_id(),
                100 * child,
                ComparisonStatus.CONSTRUCTED,
                notes,
                CPI_BASKET_VARIABLES + SA_VARIABLES,
            )
        )
    return out


def attached_results(db: ScorecardDB, staged: dict) -> tuple[list[PEResult], dict]:
    """Results for the HM Treasury and Resolution Foundation uprating claims."""
    rows = db.conn.execute(
        "SELECT claim_id, source, reform_json, conditions FROM external_scores "
        "WHERE metric = ? AND source IN ('hm_treasury', 'resolution_foundation')",
        (Metric.BENEFIT_UPRATING_RATE.value,),
    ).fetchall()
    out, counts = [], {"hm_treasury": 0, "resolution_foundation": 0}
    for claim_id, source, reform_json, conditions in rows:
        cond = json.loads(conditions)
        if source == "hm_treasury":
            policy = json.loads(reform_json)["reform"]["policy"]
            key, year = HMT_MAP[policy]
            scale = 100.0
        else:
            key, year = RF_MAP[(cond["benefit"], cond["fy"])]
            scale = 1.0
        notes = _notes("uk-uprating-tree-only")
        if key.startswith("uc_sa_"):
            notes += _notes("uk-uprating-uc-act")
        if cond.get("estimate_kind") == "range_low":
            notes.append(
                f"The claim is a lower bound ({cond.get('value_verbatim', 'over')})."
            )
        notes.append(_measured(staged, key, year))
        out.append(
            _result(
                staged,
                claim_id,
                scale * rise(staged, key, year),
                ComparisonStatus.COMPARABLE,
                notes,
                _VARIABLES[key],
            )
        )
        counts[source] += 1
    return out, counts


_EXPECTED = {
    "claims": 2,
    "results": 17,
    "hm_treasury": 4,
    "resolution_foundation": 11,
}


def ingest(db_path: Path) -> dict:
    scores = stage()
    staged = _readback()
    db = ScorecardDB(db_path)
    attached, by_source = attached_results(db, staged)
    pe = own_results(scores, staged) + attached
    counts = {"claims": len(scores), "results": len(pe), **by_source}
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE run_id LIKE ?", (RUN_PREFIX + "%",)
        )
        db.conn.execute(
            "DELETE FROM external_scores WHERE source IN (?, ?)",
            tuple(_SOURCE_MODEL),
        )
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        register_baselines_txn(db)
        detail = (
            f"{len(scores)} claims (ONS September 2026 CPI, OBR's March 2026 "
            f"forecast of it) and {len(pe)} PE results, {len(attached)} of them "
            "on the HM Treasury and Resolution Foundation uprating claims; "
            f"parameter-tree read-back on policyengine-uk {PE_BUNDLE[3:]}"
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
