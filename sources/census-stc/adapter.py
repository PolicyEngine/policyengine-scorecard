"""Adapter: Census Annual Survey of State Government Tax Collections (STC),
item T40 Individual Income Taxes -> tidy rows (lane census-stc, issue #176).

Input (raw/, the Census flat files as fetched 2026-10-15):
    FY2023-Flat-File.txt, FY2024-Flat-File.txt, FY2025-Flat-File.txt
    One CSV per fiscal year: a header ``ITEM,US,AL,...,WY`` (the nation,
    the 50 States and DC) and one row per tax item (T01-T99), in thousands
    of dollars; ``X`` marks a tax the jurisdiction does not levy.
Output: data/externals/census-stc.json.

Rows: T40 for every jurisdiction that levies it (the 50 States, DC and the
nation, less the six with ``X``), each fiscal year — values in dollars.
Other items are read for the QC only.

QC (any failure raises):
  1. each file's header is exactly the nation, the 50 States and DC, and
     its items are exactly ITEMS, each once
  2. every cell is a whole number of thousands or ``X``
  3. for every item, the US column equals the sum of the 50 State columns
     (``X`` as zero) — the nation excludes DC, verified on all 25 items
  4. the jurisdictions without T40 are exactly NO_INCOME_TAX in every year

Run (stdlib only):
    python sources/census-stc/adapter.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "census-stc.json"
YEARS = (2023, 2024, 2025)
ITEM = "T40"
STATES = (
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV "
    "WI WY"
).split()
HEADER = ["ITEM", "US", *STATES[:8], "DC", *STATES[8:]]
ITEMS = (
    "T01 T09 T10 T11 T12 T13 T15 T16 T18 T19 T20 T21 T22 T23 T24 T25 T27 "
    "T28 T29 T40 T41 T50 T51 T53 T99"
).split()
NO_INCOME_TAX = frozenset({"AK", "FL", "NV", "SD", "TX", "WY"})
EXPECTED_ROWS = len(YEARS) * (len(STATES) + 2 - len(NO_INCOME_TAX))


def read_year(year: int) -> dict[str, dict[str, int | None]]:
    """{item: {jurisdiction: thousands of dollars, or None for X}}; QC 1-2."""
    path = RAW / f"FY{year}-Flat-File.txt"
    rows = list(csv.reader(path.open(newline="")))
    if rows[0] != HEADER:
        raise ValueError(f"QC failed: FY{year} header changed: {rows[0]}")
    table = {}
    for row in rows[1:]:
        if len(row) != len(HEADER):
            raise ValueError(f"QC failed: FY{year} {row[0]} has {len(row)} cells")
        cells = {}
        for code, cell in zip(HEADER[1:], row[1:]):
            if cell == "X":
                cells[code] = None
            elif cell.isdigit():
                cells[code] = int(cell)
            else:
                raise ValueError(f"QC failed: FY{year} {row[0]} {code}: {cell!r}")
        if row[0] in table:
            raise ValueError(f"QC failed: FY{year} {row[0]} appears twice")
        table[row[0]] = cells
    if list(table) != ITEMS:
        raise ValueError(f"QC failed: FY{year} items changed: {list(table)}")
    return table


def qc(year: int, table: dict) -> None:
    """QC 3-4."""
    for item, cells in table.items():
        states = sum(cells[s] or 0 for s in STATES)
        if (cells["US"] or 0) != states:
            raise ValueError(
                f"QC failed: FY{year} {item}: US {cells['US']} != 50 States {states}"
            )
    none = {code for code, v in table[ITEM].items() if v is None}
    if none != NO_INCOME_TAX:
        raise ValueError(f"QC failed: FY{year} jurisdictions without T40: {none}")


def tidy(year: int, table: dict) -> list[dict]:
    rows = []
    for code in HEADER[1:]:
        value = table[ITEM][code]
        if value is None:
            continue
        rows.append(
            {
                "source": "census-stc",
                "country": "US",
                "item": ITEM,
                "metric": "tax_collections",
                "geography": code,
                "unit_concept": "usd",
                "period": f"FY {year}",
                "value": value * 1000,
                "status": "ok",
                "source_column": f"FY{year}-Flat-File.txt: {ITEM}, {code}",
            }
        )
    return rows


def run() -> list[dict]:
    rows = []
    for year in YEARS:
        table = read_year(year)
        qc(year, table)
        rows += tidy(year, table)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
