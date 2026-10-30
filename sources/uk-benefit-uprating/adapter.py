"""Adapter: the September 2026 CPI rate that sets the April 2027 benefit
uprating -> tidy rows (lane uk-benefit-uprating).

Most working-age benefits rise each April by the CPI 12-month rate of the
September before. Two figures for September 2026 are staged:

Input (raw/):
    ons_d7g7_cpi_annual_rate.json
        ONS series D7G7 (CPI annual rate, all items), the time-series JSON
        as fetched 2026-10-22, after the 21 October 2026 release.
    obr_efo_march2026_detailed_forecast_tables_economy.xlsx
        OBR, Economic and fiscal outlook March 2026, detailed forecast
        tables: economy (published 2026-03-03). obr.uk refuses scripted
        fetches; this copy is the Wayback capture of 2026-04-23 of the
        file obr.uk/download/march-2026-economic-and-fiscal-outlook-
        detailed-forecast-tables-economy/ redirects to.
Output: data/externals/uk-benefit-uprating.json — two rows:
    the ONS outturn for September 2026, and the OBR March 2026 forecast
    for 2026 Q3 (OBR forecasts quarters; September is the last month of
    Q3). The OBR row also carries the calendar-year 2026 forecast, the
    figure policyengine-uk's benefit uprating index follows.

QC (any failure raises):
  1. the ONS file is series D7G7 and carries September 2025 and
     September 2026 exactly once each
  2. ONS September 2025 is 3.8, the rate Budget 2025 (HC 1492) states for
     the April 2026 uprating
  3. OBR Table 1.7 has the CPI column under "Year-on-year growth", and
     the rows 2025Q3, 2026Q3 and 2026 each occur exactly once
  4. OBR's 2025Q3 forecast-table value (outturn by March 2026) is within
     0.1 points of the ONS September 2025 rate

Run (needs openpyxl; imported lazily so the helpers stay importable
without it):
    uv run --with openpyxl python sources/uk-benefit-uprating/adapter.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "uk-benefit-uprating.json"

ONS_FILE = "ons_d7g7_cpi_annual_rate.json"
OBR_FILE = "obr_efo_march2026_detailed_forecast_tables_economy.xlsx"
OBR_SHEET = "1.7"
UPRATING_SEPTEMBER = "2026 SEP"
CROSSCHECK_SEPTEMBER = "2025 SEP"
# Budget 2025 (HC 1492): "other working age benefit rates ... by September
# 2025 CPI (3.8%)" — the HM Treasury claim this lane attaches to.
BUDGET_2025_SEPTEMBER_CPI = 3.8
EXPECTED_ROWS = 2


def ons_september(series: dict, label: str) -> float:
    """The D7G7 value for one month label such as '2026 SEP'."""
    hits = [m for m in series["months"] if m["date"] == label]
    if len(hits) != 1:
        raise ValueError(f"ONS D7G7: {label!r} occurs {len(hits)} times")
    return float(hits[0]["value"])


def release_date(stamp: str) -> str:
    """ONS stamps releases in UTC ('2026-10-20T23:00:00.000Z' is midnight
    on 21 October in London); the publication date is the London date."""
    when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return when.astimezone(ZoneInfo("Europe/London")).date().isoformat()


def ons_rows(series: dict) -> list[dict]:
    desc = series["description"]
    if desc["cdid"] != "D7G7" or desc["datasetId"] != "MM23":
        raise ValueError(f"not ONS D7G7/MM23: {desc['cdid']}/{desc['datasetId']}")
    crosscheck = ons_september(series, CROSSCHECK_SEPTEMBER)
    if crosscheck != BUDGET_2025_SEPTEMBER_CPI:
        raise ValueError(
            f"ONS September 2025 CPI is {crosscheck}, but Budget 2025 states "
            f"{BUDGET_2025_SEPTEMBER_CPI}"
        )
    return [
        {
            "source": "ons_cpi",
            "metric": "cpi_inflation_rate",
            "geography": "UK",
            "unit_concept": "percent",
            "period": "2026-09",
            "value": ons_september(series, UPRATING_SEPTEMBER),
            "status": "ok",
            "source_column": f"{ONS_FILE} months[{UPRATING_SEPTEMBER!r}]",
            "series": "D7G7",
            "release_date": release_date(desc["releaseDate"]),
            "publisher": "Office for National Statistics",
        }
    ]


def _cpi_column(rows: list[tuple]) -> int:
    """Index of the CPI year-on-year column in Table 1.7."""
    for i, row in enumerate(rows[:10]):
        if row and "Year-on-year growth" in [c for c in row if isinstance(c, str)]:
            header = rows[i + 1]
            cols = [j for j, c in enumerate(header) if c == "CPI"]
            # The first CPI column is the growth rate; the second is the index.
            if not cols:
                raise ValueError("OBR Table 1.7: no CPI column under the header")
            return cols[0]
    raise ValueError("OBR Table 1.7: no 'Year-on-year growth' header")


def obr_value(rows: list[tuple], label, col: int) -> float:
    hits = [r for r in rows if len(r) > col and r[1] == label]
    if len(hits) != 1:
        raise ValueError(f"OBR Table 1.7: row {label!r} occurs {len(hits)} times")
    return float(hits[0][col])


def obr_rows(rows: list[tuple], ons_crosscheck: float) -> list[dict]:
    col = _cpi_column(rows)
    q3_2025 = obr_value(rows, "2025Q3", col)
    if abs(q3_2025 - ons_crosscheck) > 0.1:
        raise ValueError(
            f"OBR 2025Q3 CPI {q3_2025:.3f} is not within 0.1 of ONS "
            f"September 2025 {ons_crosscheck}"
        )
    return [
        {
            "source": "obr_efo_economy",
            "metric": "cpi_inflation_rate",
            "geography": "UK",
            "unit_concept": "percent",
            "period": "2026Q3",
            "value": obr_value(rows, "2026Q3", col),
            "status": "ok",
            "source_column": f"{OBR_FILE} sheet {OBR_SHEET} row 2026Q3, CPI",
            "calendar_year_value": obr_value(rows, 2026, col),
            "publisher": "Office for Budget Responsibility",
        }
    ]


def extract() -> list[dict]:
    import openpyxl

    series = json.loads((RAW / ONS_FILE).read_text())
    wb = openpyxl.load_workbook(RAW / OBR_FILE, read_only=True, data_only=True)
    table = list(wb[OBR_SHEET].iter_rows(values_only=True))
    rows = ons_rows(series) + obr_rows(
        table, ons_september(series, CROSSCHECK_SEPTEMBER)
    )
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
