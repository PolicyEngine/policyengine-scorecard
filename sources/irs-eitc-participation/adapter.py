"""Adapter: IRS/Census EITC participation rates -> tidy rows.

Inputs (raw/):
    irs-eitc-participation-rate-by-state_2026-10-06.html
        IRS EITC Central, "EITC participation rates by state", as fetched
        2026-10-06: 50 States, DC and national, tax years 2014-2022. ACS
        records linked to IRS returns; eligibility modeled on ACS, receipt
        from IRS records (the page's footnote 1).
    irs-eitc-participation-rate-by-states_wayback-20240527172311.html
        The same table's May 2024 edition (old eitc.irs.gov URL, Wayback
        Machine capture), tax years 2013-2020 — the QC's second edition.
    CES-WP-24-75.pdf
        Coleman et al., "EITC Participation Results and IRS-Census Match
        Methodology, Tax Year 2021" (Census CES working paper, December
        2024): the CPS-based national series, TY2019-2021 (Tables 1-3).
Output: data/externals/irs-eitc-participation.json — tidy rows.

Variants: the State table is ACS-based (variant null); the national
CPS-based series is variant "cps" — the page's footnote 2 calls CPS 78%
"the reported national estimate" for TY2022 against the table's ACS
80.8%. Rates are fractions; counts are tax units; dollars are USD.

QC (any failure raises):
    1. the State table: one table, the exact header, a closed row-label
       set (51 + national), every cell a one-decimal percent
    2. edition check: every cell the May 2024 edition shares with the
       current one (TY2014-2020) is identical — a silent revision fails
    3. footnote 1's "19.2% ... didn't claim" equals 100 - national TY2022
    4. CES Tables 1-3, recomputed within the published rounding:
       eligible x (1 - taxpayer rate) = Table 2 non-claimants;
       eligible dollars x (1 - dollar rate) = Table 3 unclaimed dollars;
       Table 2 and Table 3 components sum to their totals

Run (needs pypdf; imported lazily so the parsing helpers stay importable
without it):
    uv run --with pypdf python sources/irs-eitc-participation/adapter.py
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "irs-eitc-participation.json"
PAGE = RAW / "irs-eitc-participation-rate-by-state_2026-10-06.html"
OLD_PAGE = RAW / "irs-eitc-participation-rate-by-states_wayback-20240527172311.html"
CES = RAW / "CES-WP-24-75.pdf"

SOURCE_ID = "irs-eitc-participation"
YEARS = tuple(range(2022, 2013, -1))  # the current table's column order
OLD_YEARS = tuple(range(2020, 2012, -1))

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
NATIONAL = "National"
PERCENT = re.compile(r"(\d{2}\.\d)%")


def _clean(fragment: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def _label(cell: str) -> str:
    """'National 2' -> 'National' (footnote marker); 'NEW YORK' -> 'New
    York' (the 2024 edition is upper case). Unknown labels raise."""
    base = re.sub(r"\s*\d+$", "", cell).strip()
    for name in [*STATES, NATIONAL]:
        if base.lower() == name.lower():
            return name
    raise ValueError(f"unknown row label {cell!r}")


def parse_state_table(page: str, years: tuple[int, ...]) -> dict[str, dict]:
    """label -> {tax year: percent}. Fails on any deviation from the
    expected header, row set or cell format."""
    tables = re.findall(r"<table.*?</table>", page, flags=re.DOTALL)
    if len(tables) != 1:
        raise ValueError(f"expected one table, found {len(tables)}")
    rows = [
        [
            _clean(c)
            for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.DOTALL)
        ]
        for r in re.findall(r"<tr.*?</tr>", tables[0], flags=re.DOTALL)
    ]
    header = [h.lower() for h in rows[0]]
    want = ["participation rate by state", *(f"tax year {y}" for y in years)]
    if header != want:
        raise ValueError(f"header {rows[0]} != {want}")
    out: dict[str, dict] = {}
    for row in rows[1:]:
        label = _label(row[0])
        if label in out:
            raise ValueError(f"row {label} appears twice")
        if len(row) != len(years) + 1:
            raise ValueError(f"{label}: {len(row) - 1} cells, want {len(years)}")
        cells = {}
        for year, cell in zip(years, row[1:]):
            m = PERCENT.fullmatch(cell)
            if m is None:
                raise ValueError(f"{label} {year}: unparsed cell {cell!r}")
            cells[year] = float(m.group(1))
        out[label] = cells
    if set(out) != {*STATES, NATIONAL}:
        raise ValueError(f"row set {sorted(set(out) ^ {*STATES, NATIONAL})}")
    return out


def page_footnotes(page: str) -> dict:
    """The two footnote figures the QC and the CPS row read."""
    text = _clean(
        re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.DOTALL)
    )
    m1 = re.search(
        r"Approximately,\s*(\d+\.\d)% of all eligible earned income taxpayers in "
        r"TY(\d{4}) didn.t claim",
        text,
    )
    m2 = re.search(
        r"tax year (\d{4}) national estimate, based on the Current Population "
        r"Survey \(CPS\) is (\d+)%",
        text,
    )
    if m1 is None or m2 is None:
        raise ValueError("footnote 1 or 2 not found on the page")
    return {
        "unclaimed_share": (int(m1.group(2)), float(m1.group(1))),
        "cps_national": (int(m2.group(1)), float(m2.group(2))),
    }


def _ces_text() -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("this adapter needs pypdf: uv run --with pypdf ...") from e
    return "\n".join(p.extract_text() for p in PdfReader(CES).pages)


def parse_ces_tables(text: str) -> dict:
    """CES-WP-24-75 Tables 1-3, TY2019-2021, in raw units."""
    num = r"(\d+(?:\.\d)?)"
    t1 = re.findall(
        rf"(20(?:19|20|21))\s+{num} million\s+{num} percent\s+\${num} billion\s+"
        rf"{num} percent",
        text,
    )
    t2 = re.findall(
        rf"(20(?:19|20|21))\s+{num} million\s+{num} million\s+{num} million", text
    )
    t3 = re.findall(
        rf"(20(?:19|20|21))\s+\${num} billion\s+\${num} billion\s+\${num} billion\s+"
        rf"\${num} billion",
        text,
    )
    years = ["2019", "2020", "2021"]
    for name, rows in (("Table 1", t1), ("Table 2", t2), ("Table 3", t3)):
        if [r[0] for r in rows] != years:
            raise ValueError(f"CES {name}: rows {[r[0] for r in rows]} != {years}")
    m, b = 1e6, 1e9
    return {
        int(r1[0]): {
            "eligible_tax_units": float(r1[1]) * m,
            "taxpayer_rate": float(r1[2]),
            "eligible_dollars": float(r1[3]) * b,
            "dollar_rate": float(r1[4]),
            "nonclaimants_nonfilers": float(r2[1]) * m,
            "nonclaimants_filers": float(r2[2]) * m,
            "nonclaimants_total": float(r2[3]) * m,
            "unclaimed_nonfilers": float(r3[1]) * b,
            "unclaimed_filers_no_eitc": float(r3[2]) * b,
            "unclaimed_underclaimants": float(r3[3]) * b,
            "unclaimed_total": float(r3[4]) * b,
        }
        for r1, r2, r3 in zip(t1, t2, t3)
    }


def _interval_check(lo: float, hi: float, target: float, half: float, what: str):
    """Published value `target` (rounded to +/- half) must be reachable
    from the interval [lo, hi] the rounded inputs allow."""
    if hi < target - half or lo > target + half:
        raise ValueError(
            f"QC failed: {what}: inputs give [{lo:.4g}, {hi:.4g}], "
            f"published {target:.4g} +/- {half:.2g}"
        )


def qc(current: dict, old: dict, notes: dict, ces: dict) -> None:
    # 2: edition check
    for label, cells in old.items():
        for year, value in cells.items():
            if year in current[label] and current[label][year] != value:
                raise ValueError(
                    f"QC failed: {label} TY{year} revised {value} -> "
                    f"{current[label][year]} between editions"
                )
    # 3: footnote 1 against the national cell
    year, unclaimed = notes["unclaimed_share"]
    if abs(100 - current[NATIONAL][year] - unclaimed) > 1e-9:
        raise ValueError(f"QC failed: footnote 1 {unclaimed}% vs national TY{year}")
    # 4: CES Tables 1-3 within the published rounding (0.05 million / 0.05
    # billion on counts and dollars; 0.5 points on whole-percent rates)
    for year, c in ces.items():
        e, r = c["eligible_tax_units"], c["taxpayer_rate"]
        _interval_check(
            (e - 5e4) * (1 - (r + 0.5) / 100),
            (e + 5e4) * (1 - (r - 0.5) / 100),
            c["nonclaimants_total"],
            5e4,
            f"TY{year} non-claimants = eligible x (1 - rate)",
        )
        d, dr = c["eligible_dollars"], c["dollar_rate"]
        _interval_check(
            (d - 5e7) * (1 - (dr + 0.5) / 100),
            (d + 5e7) * (1 - (dr - 0.5) / 100),
            c["unclaimed_total"],
            5e7,
            f"TY{year} unclaimed dollars = eligible dollars x (1 - rate)",
        )
        parts = c["nonclaimants_nonfilers"] + c["nonclaimants_filers"]
        _interval_check(
            parts - 1e5, parts + 1e5, c["nonclaimants_total"], 5e4, "T2 sum"
        )
        parts = (
            c["unclaimed_nonfilers"]
            + c["unclaimed_filers_no_eitc"]
            + c["unclaimed_underclaimants"]
        )
        _interval_check(
            parts - 1.5e8, parts + 1.5e8, c["unclaimed_total"], 5e7, "T3 sum"
        )


def _row(metric, geography, year, value, unit, column, variant=None, subgroup="total"):
    return {
        "source": SOURCE_ID,
        "country": "US",
        "program": "eitc",
        "metric": metric,
        "subgroup": subgroup,
        "variant": variant,
        "geography": geography,
        "unit_concept": unit,
        "period": f"TY {year}",
        "value": value,
        "status": "ok",
        "source_column": column,
    }


def tidy(current: dict, notes: dict, ces: dict) -> list[dict]:
    page = "IRS EITC participation rates by state (fetched 2026-10-06)"
    rows = []
    for label, cells in current.items():
        geo = "US" if label == NATIONAL else STATES[label]
        for year, pct in cells.items():
            rows.append(
                _row(
                    "participation_rate",
                    geo,
                    year,
                    round(pct / 100, 4),
                    "tax_units",
                    f"{page}: {label}, Tax year {year}",
                )
            )
    year, pct = notes["cps_national"]
    rows.append(
        _row(
            "participation_rate",
            "US",
            year,
            pct / 100,
            "tax_units",
            f"{page}: footnote 2, TY{year} CPS national estimate (whole percent)",
            "cps",
        )
    )
    ces_col = "CES-WP-24-75 {table}, Tax Year {year}: {column}"
    for year, c in ces.items():

        def add(metric, value, unit, table, column, subgroup="total", year=year):
            rows.append(
                _row(
                    metric,
                    "US",
                    year,
                    value,
                    unit,
                    ces_col.format(table=table, year=year, column=column),
                    "cps",
                    subgroup,
                )
            )

        add(
            "eligible_count",
            c["eligible_tax_units"],
            "tax_units",
            "Table 1",
            "Tax Units Modeled Eligible (0.1 million)",
        )
        add(
            "participation_rate",
            c["taxpayer_rate"] / 100,
            "tax_units",
            "Table 1",
            "Taxpayer Participation Rate (whole percent)",
        )
        add(
            "eligible_amount",
            c["eligible_dollars"],
            "usd",
            "Table 1",
            "EITC Dollars Modeled Eligible ($0.1 billion)",
        )
        add(
            "dollar_participation_rate",
            c["dollar_rate"] / 100,
            "usd",
            "Table 1",
            "Dollar Participation Rate (whole percent)",
        )
        for sub, key in (
            ("non_filers", "nonclaimants_nonfilers"),
            ("filers", "nonclaimants_filers"),
            ("total", "nonclaimants_total"),
        ):
            add(
                "participation_gap_count",
                c[key],
                "tax_units",
                "Table 2",
                f"Eligible Non-Claimants, {sub} (0.1 million)",
                sub,
            )
        for sub, key in (
            ("non_filers", "unclaimed_nonfilers"),
            ("filers_claimed_no_eitc", "unclaimed_filers_no_eitc"),
            ("under_claimants", "unclaimed_underclaimants"),
            ("total", "unclaimed_total"),
        ):
            add(
                "unclaimed_benefit_amount",
                c[key],
                "usd",
                "Table 3",
                f"Unclaimed EITC Dollars, {sub} ($0.1 billion)",
                sub,
            )
    return rows


# Shape contract: 52 rows x 9 tax years + the CPS footnote + 3 CES years x
# (4 Table 1 + 3 Table 2 + 4 Table 3) cells.
EXPECTED_ROWS = 52 * 9 + 1 + 3 * 11


def run() -> list[dict]:
    page = PAGE.read_text(encoding="utf-8")
    current = parse_state_table(page, YEARS)
    old = parse_state_table(OLD_PAGE.read_text(encoding="utf-8"), OLD_YEARS)
    notes = page_footnotes(page)
    ces = parse_ces_tables(_ces_text())
    qc(current, old, notes, ces)
    rows = tidy(current, notes, ces)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
