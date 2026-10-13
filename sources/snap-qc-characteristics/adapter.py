"""Adapter: Characteristics of SNAP Households, FY 2023 (SNAP QC), State tables
B.1 and B.2 -> tidy rows of ADMINISTRATIVE facts.

Input:  raw/snap-FY23-Characteristics-Report.pdf
        Monkovic and Ward, "Characteristics of Supplemental Nutrition
        Assistance Program Households: Fiscal Year 2023", USDA FNS, 2025
        (169 pages).
Output: data/externals/snap-qc-characteristics.json

Routing: the SNAP QC sample (43,776 households) is weighted to SNAP Program
Operations totals by State — monthly participating households,
participants and benefits — after removing erroneously paid and
disaster-only households (Appendix D, "Weighting"). B.1 is therefore an
administrative caseload table and B.2 the caseload's average
characteristics: Chronicle material under the 2026-08-02 boundary ruling
(issue #6), written to data/ledger/us_admin_outturns.jsonl by
scorecard_db/ingest_us_admin_outturns.py. No scorecard claims.

Tables (exact title; a closed row-label set: 50 States, DC, Guam, the
Virgin Islands and the total):
    B.1  SNAP households (000), participants (000), monthly SNAP benefits
         ($000), each with a column percent (column percents are not
         staged: they are the counts' shares)
    B.2  averages: gross countable income as % of poverty guidelines,
         gross and net countable income ($), total deductions ($), SNAP
         benefit ($), household size (people), certification period
         (months)

QC (any failure raises):
    1. B.1: each count's State rows sum to the total within 0.5 per row
       (thousands rounding); each column percent sums to 100 within 0.05
       per row
    2. B.2 household size = B.1 participants / households, and B.2 SNAP
       benefit = B.1 benefits / households, within the published rounding,
       for every jurisdiction and the total
Run (pypdf, imported lazily):
    uv run --with pypdf python sources/snap-qc-characteristics/adapter.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF = HERE / "raw" / "snap-FY23-Characteristics-Report.pdf"
OUT = HERE.parent.parent / "data" / "externals" / "snap-qc-characteristics.json"
SOURCE_ID = "snap-qc-characteristics"
PERIOD = "FY 2023"
SOURCE_LINE = "Source:  FY 2023 SNAP QC sample."

JURISDICTIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Guam": "GU",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virgin Islands": "VI",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}
TOTALS = {"Total": "US", "Totala": "US"}  # B.1 prints "Totala" (footnote a)

TABLES = {
    "B.1": (
        (
            "Table B.1. Distribution of participating households, individuals, "
            "and benefits by State"
        ),
        6,
    ),
    "B.2": ("Table B.2. Average values of selected characteristics by State", 7),
}
# (table, column index) -> (metric, unit, scale); None = not staged
COLUMNS = {
    ("B.1", 0): ("households", "households", 1000),
    ("B.1", 1): None,  # column % of households
    ("B.1", 2): ("participants", "persons", 1000),
    ("B.1", 3): None,  # column % of participants
    ("B.1", 4): ("monthly_benefits", "usd_per_month", 1000),
    ("B.1", 5): None,  # column % of benefits
    ("B.2", 0): ("avg_gross_income_pct_poverty", "percent_of_poverty_guideline", 1),
    ("B.2", 1): ("avg_gross_countable_income", "usd_per_household_month", 1),
    ("B.2", 2): ("avg_net_countable_income", "usd_per_household_month", 1),
    ("B.2", 3): ("avg_total_deductions", "usd_per_household_month", 1),
    ("B.2", 4): ("avg_snap_benefit", "usd_per_household_month", 1),
    ("B.2", 5): ("avg_household_size", "persons_per_household", 1),
    ("B.2", 6): ("avg_certification_period", "months", 1),
}
NUM = r"\d[\d,]*(?:\.\d+)?"


def _number(text: str) -> float:
    return float(text.replace(",", ""))


def parse_table(pages: list[str], key: str) -> dict[str, list[float]]:
    title, width = TABLES[key]
    hits = [p for p in pages if title in p and SOURCE_LINE in p]
    if len(hits) != 1:
        raise ValueError(f"{key}: data page found {len(hits)} times, want 1")
    labels = {**JURISDICTIONS, **TOTALS}
    alts = "|".join(re.escape(x) for x in sorted(labels, key=len, reverse=True))
    row_re = re.compile(rf"^({alts})((?:\s+{NUM})+)\s*$")
    rows: dict[str, list[float]] = {}
    for line in hits[0].split("\n"):
        line = line.strip()
        m = row_re.match(line)
        if not m:
            continue
        values = [_number(x) for x in m.group(2).split()]
        if len(values) != width:
            raise ValueError(f"{key}: {m.group(1)} has {len(values)} values")
        code = labels[m.group(1)]
        if code in rows:
            raise ValueError(f"{key}: {m.group(1)} appears twice")
        rows[code] = values
    want = set(JURISDICTIONS.values()) | {"US"}
    if set(rows) != want:
        raise ValueError(f"{key}: rows {sorted(want ^ set(rows))} wrong")
    return rows


def _within(a: float, b: float, tol: float, what: str) -> None:
    if abs(a - b) > tol + 1e-9:
        raise ValueError(f"QC failed: {what}: {a} vs {b} (tolerance {tol})")


def qc(b1: dict, b2: dict) -> None:
    states = [c for c in b1 if c != "US"]
    n = len(states)
    for col in range(6):
        total = sum(b1[s][col] for s in states)
        if col % 2 == 0:
            _within(total, b1["US"][col], 0.5 * n, f"B.1 column {col} sum")
        else:
            _within(total, 100.0, 0.05 * n, f"B.1 column {col} percent sum")
    for code in b1:
        hh, people, benefits = b1[code][0], b1[code][2], b1[code][4]
        # household size: B.1 counts are in thousands (+/- 0.5), B.2 to 0.1
        lo = (people - 0.5) / (hh + 0.5)
        hi = (people + 0.5) / (hh - 0.5)
        size = b2[code][5]
        if hi < size - 0.05 or lo > size + 0.05:
            raise ValueError(
                f"QC failed: {code} household size {size} vs [{lo:.3f}, {hi:.3f}]"
            )
        # benefit per household: $000 / 000 households, B.2 in whole dollars
        lo = (benefits - 0.5) / (hh + 0.5)
        hi = (benefits + 0.5) / (hh - 0.5)
        benefit = b2[code][4]
        if hi < benefit - 0.5 or lo > benefit + 0.5:
            raise ValueError(
                f"QC failed: {code} benefit {benefit} vs [{lo:.1f}, {hi:.1f}]"
            )


def tidy(tables: dict) -> list[dict]:
    rows = []
    for key, by_code in tables.items():
        for code in sorted(by_code):
            for col, value in enumerate(by_code[code]):
                spec = COLUMNS[(key, col)]
                if spec is None:
                    continue
                metric, unit, scale = spec
                rows.append(
                    {
                        "source": SOURCE_ID,
                        "country": "US",
                        "program": "snap",
                        "metric": metric,
                        "subgroup": "total",
                        "variant": None,
                        "geography": code,
                        "unit_concept": unit,
                        "period": PERIOD,
                        "value": value * scale if scale != 1 else value,
                        "status": "ok",
                        "source_column": f"Table {key}: {code}, column {col + 1}",
                    }
                )
    return rows


EXPECTED_ROWS = 54 * (3 + 7)


def _pages() -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("this adapter needs pypdf: uv run --with pypdf ...") from e
    return [p.extract_text() for p in PdfReader(PDF).pages]


def run() -> list[dict]:
    pages = _pages()
    tables = {key: parse_table(pages, key) for key in TABLES}
    qc(tables["B.1"], tables["B.2"])
    rows = tidy(tables)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
