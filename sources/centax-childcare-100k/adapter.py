"""Adapter: CenTax, "Removing the childcare cliff-edge" (September 2026),
Table 4.2 -> tidy rows (lane uk-childcare-100k).

Input (raw/):
    AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf
        the report as published (108 pages), pinned by sha256 in source.json
    pages_layout.txt
        ``pdftotext -layout`` (poppler 26.09.0) of the twelve PDF pages the
        rows and annotations cite, each under a ``=== PDF page N (printed
        page M) ===`` header; pinned by sha256. tests/test_uk_childcare_100k.py
        re-extracts the pages from the PDF and compares, where pdftotext
        is installed.
Output: data/externals/centax-childcare-100k.json

Rows: Table 4.2 (printed page 41), "Fiscal cost estimates of removing
£100,000 threshold, 2028 and 2030": three scenarios (central, high cost,
low cost) x two tax years (2028, 2030) x six columns — the number of
parents bunching before and after removal, the static cost, the intensive-
and extensive-margin behavioural gains, and the net fiscal cost. 36 rows.
Money is in pounds (the table's £m x 1e6), sign as published (negative =
cost to the Exchequer); counts are parents.

Years: the report names tax years by their later year (editorial note,
printed page 2: "tax year 2021-22 is given as 2022"), so 2028 is 2027-28.
``period`` is that later year, the repo's UK convention (FY end year), and
``fy`` the explicit label.

QC (any failure raises):
  1. the PDF and the extract match their source.json digests
  2. the table block parses to exactly six rows, years 2028, 2030 in each
     scenario, scenario labels in the order central, high, low
  3. every money cell is a multiple of £10m (the table's rounding)
  4. static + intensive + extensive = net within £20m in every row: four
     figures each rounded to the nearest £10m can disagree by at most
     3 x 5 + 5 (the notes: "Figures may not sum due to rounding")
  5. Table 4.3's "Abolish the threshold" rows (printed page 44) equal the
     central rows of Table 4.2 cell for cell (static, both margins, net,
     and the after-removal bunching count)
  6. the prose under the table (printed pages 41-42) restates the central
     2030 figures: £340 million between static and net cost, £210 million
     from the intensive margin, £130 million from the extensive margin

Run (stdlib only):
    python sources/centax-childcare-100k/adapter.py
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "centax-childcare-100k.json"
PDF = RAW / "AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf"
PAGES = RAW / "pages_layout.txt"

SCENARIOS = ("central", "high_cost", "low_cost")
SCENARIO_LABELS = {
    "central": "Central Scenario",
    "high_cost": "High-Cost Scenario",
    "low_cost": "Low-Cost Scenario",
}
YEARS = (2028, 2030)
# Table 4.2's columns, in order, after the tax year.
COUNTS = ("bunching_before_removal", "bunching_after_removal")
MONEY = ("static_cost", "intensive_margin", "extensive_margin", "net_fiscal_cost")
COLUMN_LABELS = {
    "bunching_before_removal": "Number Bunching, Before Removal",
    "bunching_after_removal": "Number Bunching, After Removal",
    "static_cost": "Static Cost (£)",
    "intensive_margin": "Behavioural Gain (£), Intensive Margin",
    "extensive_margin": "Behavioural Gain (£), Extensive Margin",
    "net_fiscal_cost": "Net Fiscal Cost (£)",
}
ROUNDING_GBP_M = 10
SUM_TOLERANCE_GBP_M = 3 * ROUNDING_GBP_M // 2 + ROUNDING_GBP_M // 2  # 20
EXPECTED_ROWS = len(SCENARIOS) * len(YEARS) * (len(COUNTS) + len(MONEY))

_NUM = r"[\d,]+"
_MONEY = r"[+-][\d,]+m"
_T42_ROW = re.compile(
    rf"(20\d\d)\s+({_NUM})\s+({_NUM})\s+({_MONEY})\s+({_MONEY})\s+({_MONEY})\s+({_MONEY})\s*$"
)
_T43_ROW = re.compile(
    rf"(20\d\d)\s+({_NUM})\s+({_MONEY})\s+({_MONEY})\s+({_MONEY})\s+({_MONEY})\s*$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_digests() -> dict:
    """QC 1."""
    spec = json.loads((HERE / "source.json").read_text())["raw_sha256"]
    for path in (PDF, PAGES):
        got = sha256(path)
        if got != spec[path.name]:
            raise ValueError(
                f"QC failed: {path.name} sha256 {got} != {spec[path.name]}"
            )
    return spec


def pages() -> dict[int, str]:
    """{PDF page number: layout text} from the vendored extract."""
    out: dict[int, str] = {}
    current = None
    for line in PAGES.read_text().splitlines(keepends=True):
        m = re.match(
            r"=== PDF page (\d+) \(printed page (\d+)\) ===$", line.rstrip("\n")
        )
        if m:
            current = int(m.group(1))
            if int(m.group(2)) != current - 1:
                raise ValueError(f"QC failed: page header {line!r}")
            out[current] = ""
            continue
        if current is None:
            raise ValueError("QC failed: extract text before the first page header")
        out[current] += line
    return out


def _gbp_m(cell: str) -> int:
    """'-1,010m' -> -1010 (£m, sign as printed)."""
    return int(cell.removesuffix("m").replace(",", ""))


def _count(cell: str) -> int:
    return int(cell.replace(",", ""))


def parse_table_4_2(text: str) -> dict[tuple[str, int], dict[str, int]]:
    """QC 2-3: {(scenario, year): {column: value}} from printed page 41."""
    start = text.index(
        "Table 4.2: Fiscal cost estimates of removing £100,000 threshold"
    )
    end = text.index("Notes: This table presents the results", start)
    block = text[start:end]
    order = [block.find(w) for w in ("Central", "High-", "Low-")]
    if -1 in order or order != sorted(order):
        raise ValueError(f"QC failed: scenario labels out of order {order}")
    rows = [m.groups() for line in block.splitlines() if (m := _T42_ROW.search(line))]
    if len(rows) != len(SCENARIOS) * len(YEARS):
        raise ValueError(f"QC failed: Table 4.2 parsed {len(rows)} rows, want 6")
    out = {}
    for i, groups in enumerate(rows):
        scenario = SCENARIOS[i // len(YEARS)]
        year = int(groups[0])
        if year != YEARS[i % len(YEARS)]:
            raise ValueError(f"QC failed: {scenario} row {i} has year {year}")
        values = {c: _count(v) for c, v in zip(COUNTS, groups[1:3])}
        values |= {c: _gbp_m(v) for c, v in zip(MONEY, groups[3:])}
        for c in MONEY:
            if values[c] % ROUNDING_GBP_M:
                raise ValueError(
                    f"QC failed: {scenario} {year} {c} not a £10m multiple"
                )
        out[(scenario, year)] = values
        out[(scenario, year)]["_verbatim"] = dict(zip((*COUNTS, *MONEY), groups[1:]))
    return out


def check_sums(table: dict) -> None:
    """QC 4."""
    for (scenario, year), v in table.items():
        gap = (
            v["static_cost"]
            + v["intensive_margin"]
            + v["extensive_margin"]
            - v["net_fiscal_cost"]
        )
        if abs(gap) > SUM_TOLERANCE_GBP_M:
            raise ValueError(
                f"QC failed: {scenario} {year} components miss net by £{gap}m"
            )


def check_table_4_3(table: dict, text: str) -> None:
    """QC 5: Table 4.3's abolition rows equal Table 4.2's central rows."""
    start = text.index("Table 4.3: Fiscal cost estimates of childcare policy reforms")
    rows = [
        m.groups() for line in text[start:].splitlines() if (m := _T43_ROW.search(line))
    ]
    for groups in rows[:2]:
        year = int(groups[0])
        central = table[("central", year)]
        got = {
            "bunching_after_removal": _count(groups[1]),
            **{c: _gbp_m(v) for c, v in zip(MONEY, groups[2:])},
        }
        want = {k: central[k] for k in got}
        if got != want:
            raise ValueError(
                f"QC failed: Table 4.3 abolition {year} {got} != Table 4.2 {want}"
            )
    if [int(g[0]) for g in rows[:2]] != list(YEARS):
        raise ValueError(
            "QC failed: Table 4.3's first rows are not the abolition years"
        )


def check_prose(table: dict, text: str) -> None:
    """QC 6: the sentences under the table restate the central 2030 row."""
    # the page footers ("41   © CenTax") split a sentence across pages
    body = "\n".join(
        line
        for line in text.splitlines()
        if not re.fullmatch(r"\s*\d+\s+© CenTax\s*", line)
    )
    flat = " ".join(body.split())
    c = table[("central", 2030)]
    claims = {
        "around £340 million less than the static cost": c["net_fiscal_cost"]
        - c["static_cost"],
        "£210 million of this is estimated to arise": c["intensive_margin"],
        "Another £130 million is expected": c["extensive_margin"],
    }
    for phrase, value in claims.items():
        if phrase not in flat:
            raise ValueError(f"QC failed: prose phrase missing: {phrase!r}")
        stated = int(re.search(r"£(\d+) million", phrase).group(1))
        if stated != value:
            raise ValueError(f"QC failed: prose {phrase!r} != table {value}")


def tidy(table: dict) -> list[dict]:
    rows = []
    for (scenario, year), values in table.items():
        fy = f"{year - 1}-{year % 100:02d}"
        for column in (*COUNTS, *MONEY):
            money = column in MONEY
            rows.append(
                {
                    # the tidy-row core (docs/ARCHITECTURE.md); variant is
                    # CenTax's friction scenario
                    "source": "centax-childcare-100k",
                    "program": "free_childcare_hours",
                    "metric": "revenue_change" if money else "parents_bunching",
                    "subgroup": None,
                    "variant": scenario,
                    "geography": "England",
                    # the costing facets beside it
                    "country": "UK",
                    "table": "4.2",
                    "printed_page": 41,
                    "column": column,
                    "tax_year_label": str(year),
                    "fy": fy,
                    "period": year,
                    "unit_concept": "gbp" if money else "persons",
                    "value": values[column] * 1_000_000 if money else values[column],
                    "value_verbatim": values["_verbatim"][column],
                    "status": "ok",
                    "source_column": (
                        f"Table 4.2, {SCENARIO_LABELS[scenario]}, tax year {year}: "
                        f"{COLUMN_LABELS[column]}"
                    ),
                }
            )
    return rows


def run() -> list[dict]:
    check_digests()
    text = pages()
    table = parse_table_4_2(text[42])
    check_sums(table)
    check_table_4_3(table, text[45])
    check_prose(table, text[42] + text[43])
    rows = tidy(table)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
