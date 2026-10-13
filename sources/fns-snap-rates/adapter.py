"""Adapter: FNS state SNAP participation rates (FY 2020 and FY 2022) -> tidy rows.

Input:  raw/ear-SNAP-Participation-Rates-2022.pdf
        Cunnyngham, "Empirical Bayes Shrinkage Estimates of State SNAP
        Participation Rates: Fiscal Year 2020 and Fiscal Year 2022",
        Mathematica for USDA FNS, February 2025 (71 pages)
        raw/ear-snap-Reaching-Those-in-Need-2022.pdf — the 7-page brief
        whose figures are the report's Appendix B; kept for provenance,
        not parsed (its numbers are B.1a-B.6, a rounded subset).
Output: data/externals/fns-snap-rates.json — tidy rows in the scorecard schema.

Tables parsed (each by its exact title; rows by a CLOSED label set):
    III.1  headline rates (whole percent) and eligible people (thousands)
    A.1    people receiving SNAP, monthly average (FNS program operations,
           disaster-only participants excluded) — administrative
    A.2    % of participants correctly receiving and eligible under
           FEDERAL rules (SNAP QC) — excludes BBCE-only eligibility
    A.3    A.1 x A.2: eligible participants, monthly average
    A.17   final shrinkage participation rates + standard errors
    A.18   final shrinkage eligible people + standard errors
    Exhibit A.2  direct CPS ASEC national eligible totals + the
           benchmarking factor the State estimates were scaled by
    Exhibit A.3  implied rates above 100% before the cap
    B.2b   regional and national rates (whole percent)

Value semantics:
    - percents -> fractions (89.88 -> 0.8988); counts in persons
    - final rates are CAPPED at 100%: FNS raised eligible counts in States
      whose implied rate exceeded 100% (Exhibit A.3) so eligible =
      participants there. A capped cell's uncapped value rides as variant
      "uncapped_implied"
    - standard errors ride as variant "standard_error" (same unit as the
      estimate); 90% CIs are estimate +/- 1.645 SE (report eq. 45-46)
    - FY 2020 covers October 2019-February 2020 only (pre-pandemic) and
      is an underestimate by the report's own account (seasonality)

Independent-recompute QC (the issue #2 contract; any failure raises):
    1. A.17 == 100 x A.3 / A.18 (to the published 2 decimals)
    2. A.3 == A.1 x A.2 / 100 (to the rounding of A.2)
    3. A.1 and A.3 "United States" == sum of the State rows
    4. sum of A.18 State rows == Exhibit A.2 direct national total
    5. capped cells (A.17 == 100.00) are exactly Exhibit A.3's cells plus
       the pinned SECONDARY_CAPS,
       and A.3 == A.18 in each of them
    6. III.1 == A.17 / A.18 rounded (whole percent; thousands)
    7. B.2b national == 100 x sum(A.3) / Exhibit A.2 total, rounded

Run (needs pypdf; imported lazily so the parsing helpers stay importable
without it):
    uv run --with pypdf python sources/fns-snap-rates/adapter.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "data" / "externals" / "fns-snap-rates.json"
PDF = HERE / "raw" / "ear-SNAP-Participation-Rates-2022.pdf"

SOURCE_ID = "fns-snap-rates"
YEARS = ("FY 2020", "FY 2022")

STATES = {
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
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}
US = "United States"
# FNS administrative regions (B.2b rows). Parsed and checked as a closed
# set; emitted with geography "fns_region:<slug>".
REGIONS = {
    "Mid-Atlantic Region": "mid_atlantic",
    "Midwest Region": "midwest",
    "Mountain Plains Region": "mountain_plains",
    "Northeast Region": "northeast",
    "Southeast Region": "southeast",
    "Southwest Region": "southwest",
    "Western Region": "western",
}

# key -> (exact title line, closed row-label set, values per row)
TABLES = {
    "III.1": (
        (
            "Table III.1. Final shrinkage estimates of SNAP participation rates "
            "and number of people eligible"
        ),
        set(STATES) | {US},
        4,
    ),
    "A.1": (
        "Table A.1. Number of people receiving SNAP benefits, monthly average",
        set(STATES) | {US},
        2,
    ),
    "A.2": (
        (
            "Table A.2. Estimated percentage of participants who are correctly "
            "receiving SNAP benefits and"
        ),
        set(STATES),
        2,
    ),
    "A.3": (
        (
            "Table A.3. Estimated number of participants who are correctly "
            "receiving SNAP benefits and"
        ),
        set(STATES) | {US},
        2,
    ),
    "A.17": (
        (
            "Table A.17. Final shrinkage estimates of SNAP participation rates, "
            "with standard errors"
        ),
        set(STATES),
        4,
    ),
    "A.18": (
        (
            "Table A.18. Final shrinkage estimates of number of people eligible "
            "for SNAP, with standard"
        ),
        set(STATES),
        4,
    ),
    "B.2b": (
        "Table B.2b. Estimates of participation rates (Regions and national)",
        set(REGIONS) | {US},
        2,
    ),
    "Exhibit A.2": (
        "Exhibit A.2. Direct estimates of national totals and adjustment factors",
        set(YEARS),
        2,
    ),
    "Exhibit A.3": (
        "Exhibit A.3. Estimated participation rates higher than 100 percent",
        set(STATES),
        None,  # one or two values: a blank cell for the uncapped year
    ),
}

NUM = r"\d[\d,]*(?:\.\d+)?"
FOOTER = re.compile(r"^(Source: .*|Appendix [AB] .*|Mathematica® Inc\. \d+|\s*)$")


def _number(text: str) -> float:
    return float(text.replace(",", ""))


def _row_regex(labels: set[str]) -> re.Pattern:
    alts = "|".join(re.escape(x) for x in sorted(labels, key=len, reverse=True))
    return re.compile(rf"^({alts})((?:\s+{NUM})+)\s*$")


def _skip_header(lines: list[str], i: int, row_re: re.Pattern, key: str) -> int:
    """Skip the caption lines (wrapped title, column headers, page header
    and footer) that precede the first data row on a page."""
    first = i
    while i < len(lines) and not row_re.match(lines[i].strip()):
        if i - first > 6:
            raise ValueError(f"{key}: no data row within 6 lines")
        i += 1
    return i


def parse_table(pages: list[str], key: str) -> dict[str, list[float]]:
    """Rows of one table: label -> values. Fails on a missing or repeated
    label, a wrong value count, or a non-row line inside the table. A
    table whose rows reach the end of its page continues on the next page
    after the repeated column headers."""
    title, labels, width = TABLES[key]
    hits = [n for n, p in enumerate(pages) if title in p]
    if len(hits) != 1:
        raise ValueError(f"{key}: title found on {len(hits)} pages, want 1")
    page = hits[0]
    lines = pages[page].split("\n")
    start = next(i for i, ln in enumerate(lines) if title in ln)
    row_re = _row_regex(labels)
    rows: dict[str, list[float]] = {}
    i = _skip_header(lines, start + 1, row_re, key)
    while True:
        while i < len(lines):
            m = row_re.match(lines[i].strip())
            if not m:
                break
            label = m.group(1)
            values = [_number(x) for x in m.group(2).split()]
            if width is not None and len(values) != width:
                raise ValueError(
                    f"{key}: {label} has {len(values)} values, want {width}"
                )
            if label in rows:
                raise ValueError(f"{key}: {label} appears twice")
            rows[label] = values
            i += 1
        at_page_end = all(not ln.strip() for ln in lines[i:])
        if not (at_page_end and set(rows) < labels and page + 1 < len(pages)):
            break
        page += 1
        lines = pages[page].split("\n")
        i = _skip_header(lines, 0, row_re, key)
    if key == "Exhibit A.3":
        # Exhibit A.3 lists only the capped cells; its label set is the
        # capped States, checked against A.17 by the QC, not here.
        if not rows:
            raise ValueError(f"{key}: no rows parsed")
    elif set(rows) != labels:
        raise ValueError(
            f"{key}: rows {sorted(set(labels) - set(rows))} missing, "
            f"{sorted(set(rows) - set(labels))} unexpected"
        )
    # Tables end at a source note or the page footer; exhibits run on
    # into prose, which is why their row sets are closed and checked.
    if i < len(lines) and not key.startswith("Exhibit"):
        tail = lines[i].strip()
        if not FOOTER.match(tail):
            raise ValueError(f"{key}: unparsed line after the last row: {tail!r}")
    return rows


def _pages() -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("this adapter needs pypdf: uv run --with pypdf ...") from e
    return [p.extract_text() for p in PdfReader(PDF).pages]


# Capped cells that Exhibit A.3 does not list. Michigan FY 2022: A.3 ==
# A.18 == 1,026,970 (rate exactly 100.00) although its preliminary
# shrinkage rate was 95.32 (Table A.16). Exhibit A.3 lists the 16 cells
# whose rate exceeded 100% after the national benchmarking; the cap's own
# redistribution then raised the other States by 1.4-2.4 points (report
# ch. II.D), which put Michigan over 100 and capped it too. Pinned so any
# other unlisted cap still fails the QC. Michigan carries no
# uncapped_implied row: the report prints no uncapped value for it.
SECONDARY_CAPS = {("Michigan", "FY 2022")}


def _close(a: float, b: float, tol: float, what: str) -> None:
    if abs(a - b) > tol:
        raise ValueError(f"QC failed: {what}: {a} vs {b} (tolerance {tol})")


def qc(t: dict) -> dict:
    """The independent recompute (module docstring, checks 1-7)."""
    capped = {y: set() for y in YEARS}
    for name in STATES:
        for k, year in enumerate(YEARS):
            rate, elig = t["A.17"][name][k], t["A.18"][name][k]
            part, admin, eps = t["A.3"][name][k], t["A.1"][name][k], t["A.2"][name][k]
            _close(100 * part / elig, rate, 0.006, f"A.17 {name} {year}")  # 1
            _close(admin * eps / 100, part, admin * 0.00005 + 1, f"A.3 {name} {year}")
            if rate == 100.0:
                capped[year].add(name)
                _close(part, elig, 0, f"capped {name} {year}: A.3 == A.18")
            _close(round(rate), t["III.1"][name][k], 0, f"III.1 rate {name} {year}")
            _close(round(elig / 1000), t["III.1"][name][2 + k], 0, f"III.1 {name}")
    for k, year in enumerate(YEARS):
        # 3: both tables print rounded monthly averages, so a total may
        # differ from the sum of its State rows by 0.5 per row
        for tab in ("A.1", "A.3"):
            total = sum(t[tab][s][k] for s in STATES)
            _close(total, t[tab][US][k], len(STATES) / 2, f"{tab} US {year}")
        direct = t["Exhibit A.2"][year][0]
        _close(sum(t["A.18"][s][k] for s in STATES), direct, 51, f"A.18 sum {year}")
        national = 100 * sum(t["A.3"][s][k] for s in STATES) / direct
        _close(round(national), t["B.2b"][US][k], 0, f"B.2b national {year}")  # 7
        _close(t["III.1"][US][k], t["B.2b"][US][k], 0, f"III.1 US rate {year}")
        _close(round(direct / 1000), t["III.1"][US][2 + k], 0, f"III.1 US {year}")
    # 5: Exhibit A.3 lists exactly the capped cells, less the pinned
    # secondary caps. A one-value row is the year whose A.17 cell is capped
    # (the other column is blank in the PDF).
    for name, year in SECONDARY_CAPS:
        if name not in capped[year]:
            raise ValueError(f"QC failed: pinned secondary cap {name} {year} is gone")
        capped[year].discard(name)
    listed = {y: set() for y in YEARS}
    uncapped: dict[tuple[str, str], float] = {}
    for name, values in t["Exhibit A.3"].items():
        years = [y for y in YEARS if name in capped[y]]
        if len(values) != len(years):
            raise ValueError(
                f"QC failed: Exhibit A.3 {name} {values} vs capped {years}"
            )
        for y, v in zip(years, values):
            if v <= 100:
                raise ValueError(f"QC failed: Exhibit A.3 {name} {y} = {v} <= 100")
            listed[y].add(name)
            uncapped[(name, y)] = v
    if listed != capped:
        raise ValueError(f"QC failed: capped cells {capped} vs Exhibit A.3 {listed}")
    return uncapped


def _row(metric, geography, period, value, unit, column, variant=None):
    return {
        "source": SOURCE_ID,
        "country": "US",
        "program": "snap",
        "metric": metric,
        "subgroup": "total",
        "variant": variant,
        "geography": geography,
        "unit_concept": unit,
        "period": period,
        "value": value,
        "status": "ok",
        "source_column": column,
    }


def tidy(t: dict, uncapped: dict) -> list[dict]:
    rows = []
    for name, code in STATES.items():
        for k, year in enumerate(YEARS):
            cell = f"{name}, {year}"
            rate, se = t["A.17"][name][k], t["A.17"][name][2 + k]
            elig, elig_se = t["A.18"][name][k], t["A.18"][name][2 + k]
            rows += [
                _row(
                    "participation_rate",
                    code,
                    year,
                    round(rate / 100, 6),
                    "persons",
                    f"Table A.17: {cell}",
                ),
                _row(
                    "participation_rate",
                    code,
                    year,
                    round(se / 100, 7),
                    "persons",
                    f"Table A.17 standard error: {cell}",
                    "standard_error",
                ),
                _row(
                    "eligible_count", code, year, elig, "persons", f"Table A.18: {cell}"
                ),
                _row(
                    "eligible_count",
                    code,
                    year,
                    elig_se,
                    "persons",
                    f"Table A.18 standard error: {cell}",
                    "standard_error",
                ),
                _row(
                    "participant_count",
                    code,
                    year,
                    t["A.1"][name][k],
                    "persons",
                    f"Table A.1: {cell}",
                ),
                _row(
                    "federal_rules_eligible_share",
                    code,
                    year,
                    round(t["A.2"][name][k] / 100, 6),
                    "persons",
                    f"Table A.2: {cell}",
                ),
                _row(
                    "federal_rules_eligible_participant_count",
                    code,
                    year,
                    t["A.3"][name][k],
                    "persons",
                    f"Table A.3: {cell}",
                ),
            ]
            if (name, year) in uncapped:
                rows.append(
                    _row(
                        "participation_rate",
                        code,
                        year,
                        round(uncapped[(name, year)] / 100, 6),
                        "persons",
                        f"Exhibit A.3: {cell}",
                        "uncapped_implied",
                    )
                )
    for k, year in enumerate(YEARS):
        direct, factor = t["Exhibit A.2"][year]
        rows += [
            _row(
                "eligible_count",
                "US",
                year,
                direct,
                "persons",
                f"Exhibit A.2: direct estimate, {year}",
            ),
            _row(
                "benchmark_adjustment_factor",
                "US",
                year,
                factor,
                "ratio",
                f"Exhibit A.2: adjustment factor, {year}",
            ),
            _row(
                "participant_count",
                "US",
                year,
                t["A.1"][US][k],
                "persons",
                f"Table A.1: United States, {year}",
            ),
            _row(
                "participation_rate",
                "US",
                year,
                t["B.2b"][US][k] / 100,
                "persons",
                f"Table B.2b: United States, {year} (whole percent)",
            ),
        ]
        for label, slug in REGIONS.items():
            rows.append(
                _row(
                    "participation_rate",
                    f"fns_region:{slug}",
                    year,
                    t["B.2b"][label][k] / 100,
                    "persons",
                    f"Table B.2b: {label}, {year} (whole percent)",
                )
            )
    return rows


# Shape contract: a republished PDF that changes any table's size fails.
EXPECTED_ROWS = 51 * 2 * 7 + 16 + 2 * 4 + 2 * 7


def run() -> list[dict]:
    pages = _pages()
    tables = {key: parse_table(pages, key) for key in TABLES}
    uncapped = qc(tables)
    rows = tidy(tables, uncapped)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
