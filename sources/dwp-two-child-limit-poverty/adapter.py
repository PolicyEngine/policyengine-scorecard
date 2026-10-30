"""Adapter: DWP, "Removing the two-child limit on Universal Credit: Impact on
low income poverty levels in the United Kingdom" (26 November 2025) -> tidy
rows (lane uk-two-child-limit-poverty).

Input (raw/), each pinned by sha256 in source.json:
    removing_the_two_child_limit.content.json
        the note as GOV.UK's content API serves it (details.body is the
        published HTML), fetched 2026-10-23
    poverty_impacts_budget_2025.publication.json
        the parent publication, whose change history records the
        27 November 2025 corrections
    child_poverty_strategy_impact_dec_2025.content.json
        DWP's Child Poverty Strategy impact note (5 December 2025), which
        republishes the four tables as Tables A1-A4 and adds Table A5
        (children in gaining households)
    hbai_qmi_fye2024.content.json
        the HBAI quality and methodology report FYE 2024 the note cites for
        its low-income measures (annotation basis; the adapter reads its
        absolute-line and dependent-child definitions as a check)
Output: data/externals/dwp-two-child-limit-poverty.json

Rows (123):
  - Tables 1-4: relative and absolute low income, AHC and BHC, for
    children, working-age adults and individuals, as a number and a
    percentage-point change, FYE 2027 to FYE 2031: 4 x 3 x 2 x 5 = 120.
    Values as published: negative = fewer people in low income than in
    the baseline, which keeps the limit.
  - the FYE 2026 figure in the text and footnote 2: "in FYE 2026 there
    would be 300,000 fewer children in poverty if the two-child limit did
    not exist" (relative low income AHC);
  - children in gaining households, FYE 2030: "2 million" in this note,
    restated as 2.0 million in Table A5 of the Child Poverty Strategy
    note;
  - Table A5's 0.6 million of those children in households reporting deep
    material poverty (the Child Poverty Strategy note only).

Years: FYE 2030 is the financial year April 2029 to March 2030. ``period``
is the FYE (the repo's UK convention, the FY end year) and ``fy`` the
"2029-30" label; PolicyEngine runs that year as engine period 2029.

QC (any failure raises):
  1. every raw file matches its source.json digest
  2. the note holds exactly four tables, titled Table 1-4 for the four
     measures, each with the columns FYE 2027-FYE 2031 and the six rows
     Children / Working age adults / Individuals x Number / %pt
  3. Table 2's header cell reads "Change in relative low income AHC
     compared to baseline" under a title that says before housing costs:
     the title governs, and the check proves the header is a typo rather
     than a repeat of Table 1 (its values differ from Table 1's)
  4. every number is a multiple of 50,000 and every %pt has one decimal
     place (the note: "rounded to the nearest 50,000 individuals and the
     nearest 0.1 percentage point")
  5. children plus working-age adults equal individuals within 50,000 in
     every column (two rounded figures plus pensioners, whom the note
     does not report)
  6. the text restates Table 1 FYE 2030 (600,000 individuals, 450,000
     children, 150,000 working-age) and the change history records the
     27 November corrections (Table 1 FYE 2031 individuals -550,000,
     Table 2 FYE 2031 individuals -400,000), which the tables carry
  7. the Child Poverty Strategy note's Tables A1-A4 equal Tables 1-4 cell
     for cell except one: Table A2 gives individuals, FYE 2031, -0.5% where
     Table 2 gives -0.6% (REPUBLICATION_DIFFERS; any other difference
     raises, and the row records the republished value); its Table A5
     restates the 2 million gainers
  8. the HBAI FYE 2024 report the note cites defines absolute low income
     against the FYE 2011 median and a dependent child as under 16, or 16
     to 19 in full-time non-advanced education (the two definitions the
     annotations rest on)

Run (stdlib only):
    python sources/dwp-two-child-limit-poverty/adapter.py
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "dwp-two-child-limit-poverty.json"
NOTE = RAW / "removing_the_two_child_limit.content.json"
PUBLICATION = RAW / "poverty_impacts_budget_2025.publication.json"
STRATEGY = RAW / "child_poverty_strategy_impact_dec_2025.content.json"
QMI = RAW / "hbai_qmi_fye2024.content.json"
RAW_FILES = (NOTE, PUBLICATION, STRATEGY, QMI)

# table number -> (poverty_line, housing_costs, title fragment)
TABLES = {
    1: ("relative", "ahc", "relative low income after housing costs"),
    2: ("relative", "bhc", "relative low income before housing costs"),
    3: ("absolute", "ahc", "absolute low income after housing costs"),
    4: ("absolute", "bhc", "absolute low income before housing costs"),
}
YEARS = (2027, 2028, 2029, 2030, 2031)
GROUPS = {
    "Children": "children",
    "Working age adults": "working_age_adults",
    "Individuals": "individuals",
}
STATISTICS = {"Number": "number", "%pt": "percentage_points"}
# Table 4's last row label reads "Individuals: %" (no "pt"); the statistic
# is the same percentage-point change as every other %pt row.
LABEL_ALIASES = {"Individuals: %": "Individuals: %pt"}
ROUNDING = 50_000
TABLE_2_HEADER = "Change in relative low income AHC compared to baseline"
# The one cell the Child Poverty Strategy note republishes differently:
# Table 2 (relative BHC), individuals, %pt, FYE 2031 reads -0.6% in the
# Budget note (as corrected on 27 November 2025, when that column's number
# became -400,000) and -0.5% in Table A2. The Budget note's value is staged;
# the row carries the republished one. {(table, group, statistic, FYE):
# (Budget note, Table A)}
REPUBLICATION_DIFFERS = {
    (2, "individuals", "percentage_points", 2031): ("-0.6%", "-0.5%"),
}
EXPECTED_ROWS = len(TABLES) * len(YEARS) * len(GROUPS) * len(STATISTICS) + 3
URL = (
    "https://www.gov.uk/government/publications/poverty-impacts-of-social-"
    "security-changes-at-budget-2025/removing-the-two-child-limit-on-universal-"
    "credit-impact-on-low-income-poverty-levels-in-the-united-kingdom"
)
STRATEGY_URL = (
    "https://www.gov.uk/government/publications/child-poverty-strategy-impact-on-"
    "low-income-poverty-levels-and-children-gaining-in-the-uk-december-2025/"
    "child-poverty-strategy-impact-on-low-income-poverty-levels-and-children-"
    "gaining-in-the-uk-december-2025"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_digests() -> None:
    """QC 1."""
    spec = json.loads((HERE / "source.json").read_text())["raw_sha256"]
    for path in RAW_FILES:
        got = sha256(path)
        if got != spec[path.name]:
            raise ValueError(
                f"QC failed: {path.name} sha256 {got} != {spec[path.name]}"
            )


class _Tables(HTMLParser):
    """Headings (h3/h4) and the tables under them, as text cells."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[dict] = []
        self._heading: str | None = None
        self._in_heading = False
        self._buf: list[str] = []
        self._cell: list[str] | None = None
        self._row: list[str] | None = None
        self._table: dict | None = None

    def handle_starttag(self, tag, attrs):
        if tag in ("h3", "h4"):
            self._in_heading, self._buf = True, []
        elif tag == "table":
            self._table = {"title": self._heading, "rows": []}
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("h3", "h4") and self._in_heading:
            self._heading = " ".join("".join(self._buf).split())
            self._in_heading = False
        elif tag in ("td", "th") and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self._table["rows"].append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None

    def handle_data(self, data):
        if self._in_heading:
            self._buf.append(data)
        if self._cell is not None:
            self._cell.append(data)


def body(path: Path) -> str:
    return json.loads(path.read_text())["details"]["body"]


def text_of(fragment: str) -> str:
    """Visible text, whitespace collapsed; a tag becomes a space, so
    "(<abbr>FYE</abbr> 2030)" reads "(FYE 2030)" once the space inside a
    bracket is dropped."""
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())
    return re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", text))


def parse_tables(html_body: str, prefix: str) -> dict[int, dict]:
    """{table number: {"title", "header", (group, statistic, year): verbatim}}
    for the tables titled ``<prefix>N:`` (N = 1-4)."""
    p = _Tables()
    p.feed(html_body)
    out: dict[int, dict] = {}
    for t in p.tables:
        m = re.match(rf"{prefix}(\d): ", t["title"] or "")
        if not m or int(m.group(1)) not in TABLES:
            continue
        n = int(m.group(1))
        header, *rows = t["rows"]
        years = [int(re.fullmatch(r"FYE (\d{4})", h).group(1)) for h in header[1:]]
        if tuple(years) != YEARS:
            raise ValueError(f"QC failed: {prefix}{n} columns {years}")
        cells: dict = {}
        labels = []
        for label, *values in rows:
            label = LABEL_ALIASES.get(label, label)
            labels.append(label)
            group, statistic = label.split(": ")
            for year, value in zip(years, values, strict=True):
                cells[(GROUPS[group], STATISTICS[statistic], year)] = value
        want = [f"{g}: {s}" for g in GROUPS for s in STATISTICS]
        if labels != want:
            raise ValueError(f"QC failed: {prefix}{n} rows {labels}")
        out[n] = {"title": t["title"], "header": header[0], "cells": cells}
    return out


def check_structure(tables: dict[int, dict]) -> None:
    """QC 2 and 3."""
    if sorted(tables) != [1, 2, 3, 4]:
        raise ValueError(f"QC failed: tables {sorted(tables)}")
    for n, (_, _, fragment) in TABLES.items():
        if fragment not in tables[n]["title"]:
            raise ValueError(f"QC failed: Table {n} title {tables[n]['title']!r}")
    if tables[2]["header"] != TABLE_2_HEADER:
        raise ValueError(f"QC failed: Table 2 header {tables[2]['header']!r}")
    if tables[2]["cells"] == tables[1]["cells"]:
        raise ValueError("QC failed: Table 2 repeats Table 1")


def number(verbatim: str) -> int:
    m = re.fullmatch(r"(-?)([\d,]+)", verbatim)
    if not m:
        raise ValueError(f"QC failed: number cell {verbatim!r}")
    return int(m.group(1) + m.group(2).replace(",", ""))


def points(verbatim: str) -> float:
    m = re.fullmatch(r"-?\d+\.\d%", verbatim)
    if not m:
        raise ValueError(f"QC failed: %pt cell {verbatim!r}")
    return float(verbatim.rstrip("%"))


def check_rounding_and_sums(tables: dict[int, dict]) -> None:
    """QC 4 and 5."""
    for n, t in tables.items():
        for (group, statistic, year), v in t["cells"].items():
            if statistic == "number" and number(v) % ROUNDING:
                raise ValueError(f"QC failed: Table {n} {group} {year} {v}")
            if statistic == "percentage_points":
                points(v)
        for year in YEARS:
            c = t["cells"]
            parts = number(c[("children", "number", year)]) + number(
                c[("working_age_adults", "number", year)]
            )
            whole = number(c[("individuals", "number", year)])
            if abs(parts - whole) > ROUNDING:
                raise ValueError(f"QC failed: Table {n} FYE {year}: {parts} vs {whole}")


def check_text_and_corrections(note_text: str, tables: dict[int, dict]) -> None:
    """QC 6."""
    for phrase in (
        "600,000 fewer individuals in relative low income after housing costs "
        "in the final year of parliament (FYE 2030)",
        "This includes 450,000 children and 150,000 working age individuals",
    ):
        if phrase not in note_text:
            raise ValueError(f"QC failed: text {phrase!r} missing")
    c = tables[1]["cells"]
    if (
        c[("individuals", "number", 2030)],
        c[("children", "number", 2030)],
        c[("working_age_adults", "number", 2030)],
    ) != ("-600,000", "-450,000", "-150,000"):
        raise ValueError("QC failed: Table 1 FYE 2030 differs from the text")
    history = json.loads(PUBLICATION.read_text())["details"]["change_history"]
    notes = " ".join(h["note"] for h in history)
    for fragment in (
        "In Table 1 for FYE 2031 the figure for Individuals has been corrected to -550,000",
        "in Table 2 for FYE 2031 the figure for Individuals has been corrected to -400,000",
    ):
        if fragment not in notes:
            raise ValueError(f"QC failed: change history lacks {fragment!r}")
    if tables[1]["cells"][("individuals", "number", 2031)] != "-550,000":
        raise ValueError("QC failed: Table 1 FYE 2031 individuals not corrected")
    if tables[2]["cells"][("individuals", "number", 2031)] != "-400,000":
        raise ValueError("QC failed: Table 2 FYE 2031 individuals not corrected")


def check_strategy(tables: dict[int, dict], strategy_text: str) -> dict:
    """QC 7; returns Table A5's two cells and the republication's one
    differing cell, {(table, group, statistic, year): its value}."""
    a = parse_tables(body(STRATEGY), "Table A")
    diff = {}
    for n in TABLES:
        if set(a[n]["cells"]) != set(tables[n]["cells"]):
            raise ValueError(f"QC failed: Table A{n} cells differ from Table {n}'s")
        for k, v in tables[n]["cells"].items():
            if a[n]["cells"][k] != v:
                diff[(n, *k)] = (v, a[n]["cells"][k])
    if diff != REPUBLICATION_DIFFERS:
        raise ValueError(f"QC failed: Tables A1-A4 differ from Tables 1-4: {diff}")
    m = re.search(
        r"Table A5: Gainers from the removal of the two-child limit in FYE ?2030, UK "
        r"Children in gaining households Number of children "
        r"Children: all ([\d.]+) million Children: in deep material poverty ([\d.]+) million",
        strategy_text,
    )
    if not m:
        raise ValueError("QC failed: Table A5 not found")
    if m.group(1) != "2.0":
        raise ValueError(f"QC failed: Table A5 gainers {m.group(1)} != 2.0")
    return {"all": m.group(1), "deep_material_poverty": m.group(2), "differs": diff}


def check_methodology() -> None:
    """QC 8."""
    q = text_of(body(QMI))
    for phrase in (
        "Absolute low income measures the proportion of individuals who have "
        "household incomes a certain proportion below the average in FYE 2011, "
        "adjusted for inflation.",
        "A dependent child is aged 16 or under, or is 16 to 19 years old, "
        "unmarried and in full-time non-advanced education.",
        "Relative low income is the comparison to the median of the current year",
    ):
        if phrase not in q:
            raise ValueError(f"QC failed: HBAI FYE 2024 report lacks {phrase!r}")


def _row(**kw) -> dict:
    return {
        "source": "dwp-two-child-limit-poverty",
        "country": "UK",
        "republished_as": None,
        **kw,
    }


def tidy(tables: dict[int, dict], a5: dict) -> list[dict]:
    rows = []
    for n, (line, housing, _) in TABLES.items():
        for (group, statistic, year), verbatim in tables[n]["cells"].items():
            value = number(verbatim) if statistic == "number" else points(verbatim)
            republished = a5["differs"].get((n, group, statistic, year))
            rows.append(
                _row(
                    republished_as=None
                    if republished is None
                    else f"Child Poverty Strategy note Table A{n}: {republished[1]}",
                    publication="budget_2025_note",
                    table=f"Table {n}",
                    metric=(
                        "poverty_count_change"
                        if statistic == "number"
                        else "poverty_rate_change"
                    ),
                    group=group,
                    poverty_line=line,
                    housing_costs=housing,
                    fye=year,
                    fy=f"{year - 1}-{year % 100:02d}",
                    period=year,
                    value=value,
                    value_verbatim=verbatim,
                    rounding="nearest 50,000"
                    if statistic == "number"
                    else "nearest 0.1 percentage point",
                    status="ok",
                    source_column=f"Table {n}, {group}: {statistic}, FYE {year}",
                )
            )
    rows.append(
        _row(
            publication="budget_2025_note",
            table="text and footnote 2",
            metric="poverty_count_change",
            group="children",
            poverty_line="relative",
            housing_costs="ahc",
            fye=2026,
            fy="2025-26",
            period=2026,
            value=300_000,
            value_verbatim=(
                "in FYE 2026 there would be 300,000 fewer children in poverty if "
                "the two-child limit did not exist"
            ),
            rounding="'around 300,000' (main text)",
            status="ok",
            source_column="Poverty impacts, paragraph 4, and footnote 2",
        )
    )
    rows.append(
        _row(
            publication="budget_2025_note",
            table="text",
            metric="gainer_count",
            group="children",
            poverty_line=None,
            housing_costs=None,
            fye=2030,
            fy="2029-30",
            period=2030,
            value=2_000_000,
            value_verbatim=(
                "2 million children will live in households that see an increase in "
                "income as a result of the removal of the two-child limit"
            ),
            rounding="2 million (restated as 2.0 million in Child Poverty Strategy Table A5)",
            status="ok",
            source_column="Poverty impacts, paragraph 2",
        )
    )
    rows.append(
        _row(
            publication="child_poverty_strategy_note",
            table="Table A5",
            metric="gainer_count",
            group="children_in_deep_material_poverty",
            poverty_line=None,
            housing_costs=None,
            fye=2030,
            fy="2029-30",
            period=2030,
            value=float(a5["deep_material_poverty"]) * 1_000_000,
            value_verbatim=f"{a5['deep_material_poverty']} million",
            rounding="0.1 million",
            status="ok",
            source_column="Table A5, Children: in deep material poverty",
        )
    )
    return rows


def run() -> list[dict]:
    check_digests()
    note_html = body(NOTE)
    tables = parse_tables(note_html, "Table ")
    check_structure(tables)
    check_rounding_and_sums(tables)
    check_text_and_corrections(text_of(note_html), tables)
    a5 = check_strategy(tables, text_of(body(STRATEGY)))
    check_methodology()
    rows = tidy(tables, a5)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
