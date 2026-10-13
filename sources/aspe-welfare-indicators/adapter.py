"""Adapter: ASPE Welfare Indicators, Indicator 4 (participation among the
eligible) -> tidy rows.

Inputs (raw/):
    25th-welfare-indicators-appendix-tables.pdf  Welfare Indicators and Risk
        Factors, 25th Report to Congress (HHS ASPE, April 2026), Appendix
        Tables 10-12
    24th-welfare-indicators-appendix-tables.pdf  the 24th report's (August
        2025) appendix — the QC's second edition
    25th-welfare-indicators-report.pdf  the report (definitions, Indicator 4)
Output: data/externals/aspe-welfare-indicators.json — tidy rows.

Tables (rows matched by strict per-table patterns; anything else in the
data block raises):
    10  TANF families eligible / participating (millions, 3 decimals) and
        rate (percent), select years 1981-2023 — TRIM3 on the CPS ASEC
    11  SNAP households eligible / participating (millions, 1 decimal) and
        rate — fiscal-year averages from FY 1999, single months before;
        FY 2021 "no data" — FNS program operations, SNAP QC and CPS ASEC
    12  SSI adult units, 1993-2023: one-person aged 65+, one-person
        disabled, married couples — eligible / participating (millions,
        1 decimal) and rate; counts "n.a." before 1998 — TRIM3

Value semantics: counts in raw units (millions x 1e6), rates as fractions;
"no data" and "n.a." cells are status "suppressed" with null values.

QC (any failure raises):
    1. every rate recomputes from its two counts within the published
       rounding (interval arithmetic on the rounded counts and rate)
    2. edition check: every cell the 24th edition shares with the 25th is
       identical (a silent revision fails; a documented one is pinned in
       REVISIONS)
    3. the shape is pinned (EXPECTED_ROWS: 39, 40 and 31 rows), and a line
       that looks like data but fails its table's pattern raises

Run (pypdf, imported lazily):
    uv run --with pypdf python sources/aspe-welfare-indicators/adapter.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "aspe-welfare-indicators.json"
SOURCE_ID = "aspe-welfare-indicators"
EDITIONS = {
    25: RAW / "25th-welfare-indicators-appendix-tables.pdf",
    24: RAW / "24th-welfare-indicators-appendix-tables.pdf",
}
NUM = r"(\d+\.\d+)"
NA = r"(\d+\.\d+|n\.a\.)"

TABLE_10 = re.compile(rf"^((?:19|20)\d\d) {NUM} {NUM} {NUM}$")
TABLE_11 = re.compile(
    r"^(Fiscal Year (?:19|20)\d\d|(?:September|August|February) (?:19|20)\d\d) "
    r"(\d+\.\d|no data) (\d+\.\d|no data) (\d+\.\d|no data)$"
)
TABLE_12 = re.compile(r"^((?:19|20)\d\d)" + rf" {NA}" * 9 + "$")
TITLES = {
    10: "Table 10 Indicator 4.",
    11: "Table 11 Indicator 4.",
    12: "Table 12 Indicator 4.",
}
SSI_CATEGORIES = ("aged_65plus_individuals", "disabled_individuals", "couples")

# Documented revisions between editions (cell -> (24th, 25th)); empty today.
REVISIONS: dict = {}


def _pages(path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("this adapter needs pypdf: uv run --with pypdf ...") from e
    return [p.extract_text() for p in PdfReader(path).pages]


def _table_lines(pages: list[str], number: int, pattern: re.Pattern) -> list[tuple]:
    hits = [p for p in pages if TITLES[number] in p]
    if len(hits) != 1:
        raise ValueError(f"Table {number}: title on {len(hits)} pages, want 1")
    out = []
    for line in hits[0].split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        m = pattern.match(line)
        if m:
            out.append(m.groups())
        elif re.match(
            r"^(Fiscal Year |September |August |February )?(19|20)\d\d "
            r"(\d|no data|n\.a\.)",
            line,
        ):
            raise ValueError(f"Table {number}: unparsed data line {line!r}")
    if not out:
        raise ValueError(f"Table {number}: no rows")
    return out


def _f(cell: str) -> float | None:
    return None if cell in ("no data", "n.a.") else float(cell)


def parse_edition(path: Path) -> dict:
    """{(table, label, column): value} for Tables 10-12 of one edition."""
    pages = _pages(path)
    cells = {}
    for label, part, elig, rate in _table_lines(pages, 10, TABLE_10):
        for col, v in (("participating", part), ("eligible", elig), ("rate", rate)):
            cells[(10, label, col)] = _f(v)
    for label, elig, part, rate in _table_lines(pages, 11, TABLE_11):
        for col, v in (("eligible", elig), ("participating", part), ("rate", rate)):
            cells[(11, label, col)] = _f(v)
    for row in _table_lines(pages, 12, TABLE_12):
        label, vals = row[0], row[1:]
        for k, cat in enumerate(SSI_CATEGORIES):
            for j, col in enumerate(("eligible", "participating", "rate")):
                cells[(12, label, f"{cat}|{col}")] = _f(vals[3 * k + j])
    return cells


def _check_rate(part, elig, rate, count_half, what):
    """rate (whole-percent tenths) must be reachable from the rounded
    counts: interval [ (p-h)/(e+h), (p+h)/(e-h) ] x 100, +/- 0.05."""
    lo = 100 * (part - count_half) / (elig + count_half)
    hi = 100 * (part + count_half) / (elig - count_half)
    if hi < rate - 0.05 or lo > rate + 0.05:
        raise ValueError(f"QC failed: {what}: {rate} not in [{lo:.2f}, {hi:.2f}]")


def qc(current: dict, previous: dict) -> None:
    for (table, label, col), rate in current.items():
        if not col.endswith("rate") or rate is None:
            continue
        stem = col.removesuffix("rate")
        part = current.get((table, label, stem + "participating"))
        elig = current.get((table, label, stem + "eligible"))
        if part is None or elig is None:
            continue  # "n.a." counts (SSI before 1998)
        half = 0.0005 if table == 10 else 0.05
        _check_rate(part, elig, rate, half, f"Table {table} {label} {stem}")
    shared = set(current) & set(previous)
    if not shared:
        raise ValueError("QC failed: the two editions share no cells")
    for key in shared:
        if current[key] != previous[key] and REVISIONS.get(key) != (
            previous[key],
            current[key],
        ):
            raise ValueError(
                f"QC failed: {key} revised {previous[key]} -> {current[key]}"
            )


def _period(table: int, label: str) -> str:
    if table == 11 and label.startswith("Fiscal Year "):
        return "FY " + label.removeprefix("Fiscal Year ")
    return label  # calendar year, or a single month ("September 1998")


def tidy(cells: dict) -> list[dict]:
    rows = []
    for (table, label, col), value in sorted(cells.items(), key=str):
        if table == 12:
            subgroup, col = col.split("|")
            program, unit = "ssi", "benefit_units"
        else:
            subgroup = "total"
            program, unit = (
                ("tanf", "families") if table == 10 else ("snap", "households")
            )
        metric = {
            "eligible": "eligible_count",
            "participating": "participant_count",
            "rate": "participation_rate",
        }[col]
        scaled = (
            None
            if value is None
            else (round(value / 100, 4) if col == "rate" else round(value * 1e6))
        )
        rows.append(
            {
                "source": SOURCE_ID,
                "country": "US",
                "program": program,
                "metric": metric,
                "subgroup": subgroup,
                "variant": None,
                "geography": "US",
                "unit_concept": unit,
                "period": _period(table, label),
                "value": scaled,
                "status": "ok" if value is not None else "suppressed",
                "source_column": f"25th report, Appendix Table {table}: {label}, {col}"
                + (f" ({subgroup})" if table == 12 else ""),
            }
        )
    return rows


# Shape contract: Table 10 39 years x 3; Table 11 40 periods x 3; Table 12
# 31 years x 9.
EXPECTED_ROWS = 39 * 3 + 40 * 3 + 31 * 9


def run() -> list[dict]:
    current = parse_edition(EDITIONS[25])
    previous = parse_edition(EDITIONS[24])
    qc(current, previous)
    rows = tidy(current)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
