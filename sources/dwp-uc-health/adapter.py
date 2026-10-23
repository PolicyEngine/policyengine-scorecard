"""Adapter: DWP Universal Credit Health statistics -> tidy rows (lane
dwp-uc-health, issue #87).

Input (raw/):
    uc_health_tables_2026-09-15.ods
        DWP, Universal Credit Health statistics, Great Britain: April 2019
        to June 2026, data tables (published 15 September 2026), from
        assets.publishing.service.gov.uk.
Output: data/externals/dwp-uc-health.json

Table 2 splits the limited capability for work and work-related activity
(LCWRA) caseload by the entitlement rate the Universal Credit Act 2025
created from April 2026: the protected higher rate (pre-April 2026
claims), the severe conditions and terminally ill higher rates, and the
lower rate that new claimants get. One row per month (April to June 2026)
and rate, plus the total. A rate DWP shows as "[low]" is a suppressed row.
One derived row: the lower rate's share of the June 2026 total, the
quantity PolicyEngine-UK's new-claimant share parameter sets.

QC (any failure raises):
  1. Table 2's header names the five columns, and each month row occurs
     exactly once
  2. each month's rates add to its total within 10 people (DWP's
     published counts differ by a few people, from disclosure control)
  3. Table 2's total and severe conditions count equal Table 1's LCWRA
     column and its "of which, Severe Conditions" for the same month

Run (needs pandas and odfpy; imported lazily so the helpers stay
importable without them):
    uv run --with pandas --with odfpy python sources/dwp-uc-health/adapter.py
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "dwp-uc-health.json"

TABLES = "uc_health_tables_2026-09-15.ods"
MONTHS = {"April 2026": "2026-04", "May 2026": "2026-05", "June 2026": "2026-06"}
# Table 2's column headers (stripped) -> the subgroup slug.
RATES = {
    "Total LCWRA": "total",
    "Higher rate - Severe condition criteria": "higher_severe_conditions",
    "Higher rate - Special Rule End of Life (Terminally ill)": "higher_terminally_ill",
    "Higher Rate - pre-April 2026 (protected)": "higher_protected",
    "Lower rate": "lower_new_claimant",
}
ADD_UP_TOLERANCE = 10
SHARE_MONTH = "June 2026"
EXPECTED_ROWS = 16


def _cell(value) -> str:
    return "" if value is None or str(value) == "nan" else str(value).strip()


def _row(table: list[list], label: str) -> list:
    hits = [r for r in table if _cell(r[0]) == label]
    if len(hits) != 1:
        raise ValueError(f"row {label!r} occurs {len(hits)} times")
    return hits[0]


def count(value) -> int | None:
    """A published count, or None where DWP shows '[low]'."""
    text = _cell(value)
    if text == "[low]":
        return None
    return int(float(text))


def lcwra_rows(table2: list[list]) -> list[dict]:
    header = [_cell(c) for c in table2[5]]
    columns = {RATES[h]: i for i, h in enumerate(header) if h in RATES}
    if set(columns) != set(RATES.values()):
        raise ValueError(f"Table 2 header changed: {header}")
    rows = []
    for label, month in MONTHS.items():
        cells = _row(table2, label)
        values = {slug: count(cells[i]) for slug, i in columns.items()}
        parts = [v for k, v in values.items() if k != "total" and v is not None]
        if abs(sum(parts) - values["total"]) > ADD_UP_TOLERANCE:
            raise ValueError(f"{label}: rates {sum(parts)} vs total {values['total']}")
        for slug, value in values.items():
            header_name = next(h for h, s in RATES.items() if s == slug)
            rows.append(
                {
                    "source": "dwp_uc_health",
                    "program": "universal_credit",
                    "metric": "caseload",
                    "subgroup": slug,
                    "geography": "GB",
                    "unit_concept": "persons",
                    "period": month,
                    "value": value,
                    "status": "ok" if value is not None else "suppressed",
                    "source_column": f"{TABLES} 2_LCWRA_Caseload row {label!r} "
                    f"column {header_name!r}",
                }
            )
    return rows


def share_row(rows: list[dict]) -> dict:
    month = MONTHS[SHARE_MONTH]
    at = {r["subgroup"]: r["value"] for r in rows if r["period"] == month}
    return {
        "source": "dwp_uc_health",
        "program": "universal_credit",
        "metric": "affected_share",
        "subgroup": "lower_new_claimant",
        "geography": "GB",
        "unit_concept": "share",
        "period": month,
        "value": at["lower_new_claimant"] / at["total"],
        "status": "ok",
        "source_column": f"{TABLES} 2_LCWRA_Caseload row {SHARE_MONTH!r}: "
        "'Lower rate' / 'Total LCWRA' (derived)",
    }


def check_against_table1(table1: list[list], rows: list[dict]) -> None:
    header = [_cell(c) for c in table1[6]]
    lcwra = next(
        i
        for i, h in enumerate(header)
        if h.startswith("limited capability for work and")
    )
    severe = header.index("of which, Severe Conditions")
    for label, month in MONTHS.items():
        cells = _row(table1, label)
        at = {r["subgroup"]: r["value"] for r in rows if r["period"] == month}
        if count(cells[lcwra]) != at["total"]:
            raise ValueError(f"{label}: Table 1 LCWRA {cells[lcwra]} != Table 2 total")
        if count(cells[severe]) != at["higher_severe_conditions"]:
            raise ValueError(f"{label}: Table 1 severe {cells[severe]} != Table 2")


def extract() -> list[dict]:
    import pandas as pd

    sheets = pd.read_excel(RAW / TABLES, sheet_name=None, header=None, engine="odf")
    table1 = sheets["1_Caseload_by_stage"].values.tolist()
    table2 = sheets["2_LCWRA_Caseload"].values.tolist()
    rows = lcwra_rows(table2)
    check_against_table1(table1, rows)
    rows.append(share_row(rows))
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"expected {EXPECTED_ROWS} rows, got {len(rows)}")
    return rows


def main() -> None:
    rows = extract()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
