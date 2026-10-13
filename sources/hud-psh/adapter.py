"""Adapter: HUD Picture of Subsidized Households (State and U.S.) -> tidy rows.

Input (raw/, HUD USER "Assisted Housing: National and Local", 2020-census
geographies, as fetched 2026-10-06):
    STATE_2025_2020census.xlsx, US_2025_2020census.xlsx   (31 Dec 2025)
    STATE_2024_2020census.xlsx, US_2024_2020census.xlsx   (31 Dec 2024)
    dictionary_2025.pdf  the data dictionary (variable definitions and the
                         missing-value codes this adapter decodes)
Output: data/externals/hud-psh.json — tidy rows of ADMINISTRATIVE facts.

Routing: every row is an administrative outturn (HUD program records, Forms
50058/50059). Under the 2026-08-02 boundary ruling (issue #6) these go to
Chronicle as calibration material, never to scorecard claims; the ingest
(scorecard_db/ingest_us_admin_outturns.py) writes them to
data/ledger/us_admin_outturns.jsonl.

Rows kept: every geography (50 States, DC, territories, HUD's "XX Missing"
bucket, the U.S. total) x every program, at the program level (sub-program
"N/A") plus, for Housing Choice Vouchers, the tenant- and project-based
"All" splits. The MTW / non-MTW administrative splits (2025 only) are
dropped with a tally.

Columns: every column of each file is in exactly one of STAGED, IDENTITY or
NOT_STAGED (with the reason); an unknown column raises. Percents become
fractions; dollars stay nominal USD. Missing-value codes (dictionary p. 6):
-1 missing, -4 suppressed (fewer than 11 reported families), -5
non-reporting (reporting rate below 50%), NA not applicable — each becomes
a status with a null value.

QC (any failure raises):
    1. closed sets: columns, program labels, sub-programs, geographies
    2. U.S. row = sum of geography rows, within 0.5 per row (HUD rounds
       unit-month averages), for total_units; for number_reported and
       people_total the same where no geography cell is coded, else the
       U.S. row must be at least the visible sum
    3. per geography, the all-programs row = sum of program rows (units),
       within 0.5 per program row
    4. 2025: pct_occupied = 100 x total_occupied / total_units, within 1.5
       points (OCCUPANCY_TOLERANCE: HUD's own rounding is not exact)

Run (stdlib only — the xlsx is read as zipped XML):
    python sources/hud-psh/adapter.py
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "hud-psh.json"
SOURCE_ID = "hud-psh"
YEARS = (2025, 2024)
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

PROGRAMS = {
    "Summary of All HUD Programs": "all_hud_programs",
    "Public Housing": "public_housing",
    "Housing Choice Vouchers": "housing_choice_vouchers",
    "Mod Rehab": "moderate_rehabilitation",
    "Project Based Section 8": "project_based_section_8",
    "S236/BMIR": "section_236_bmir",
    "202/PRAC": "section_202_prac",
    "811/PRAC": "section_811_prac",
    "811 Project Rental Assistance (PRA)": "section_811_pra",
}
# sub-program -> subgroup slug; None = dropped with a tally
SUB_PROGRAMS = {
    "N/A": "total",
    "NA": "total",
    "PBV, All": "project_based_vouchers",
    "TBV, All": "tenant_based_vouchers",
    "PBV, MTW": None,
    "PBV, non-MTW": None,
    "TBV, MTW": None,
    "TBV, non-MTW": None,
    "PH, MTW": None,
    "PH, non-MTW": None,
}
TERRITORIES = {"PR", "VI", "GU", "AS", "MP"}
STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}

# column -> (metric, unit, scale). scale converts the published value.
STAGED = {
    "total_units": ("subsidized_units", "units", 1),
    "total_occupied": ("occupied_units", "units", 1),
    "pct_occupied": ("occupancy_share", "share_of_units", 0.01),
    "number_reported": ("reported_households", "households", 1),
    "people_total": ("people", "persons", 1),
    "rent_per_month": (
        "household_rent_contribution",
        "usd_per_household_month",
        1,
    ),
    "spending_per_month": ("hud_spending", "usd_per_unit_month", 1),
    "hh_income": ("household_income", "usd_per_household_year", 1),
    "pct_median": (
        "income_share_of_area_median",
        "share_of_area_median_income",
        0.01,
    ),
    "pct_lt80_median": ("share_below_80pct_ami", "share_of_households", 0.01),
    "pct_lt50_median": ("share_below_50pct_ami", "share_of_households", 0.01),
    "pct_lt30_median": ("share_below_30pct_ami", "share_of_households", 0.01),
}
IDENTITY = {
    "quarter",
    "gsl",
    "states",
    "entities",
    "sumlevel",
    "program_label",
    "program",
    "sub_program",
    "name",
    "code",
    "state",
}
_DISTRIBUTION = "distributional share or average; stays in raw/ for later staging"
_GEO_META = "geography metadata for sub-State summary levels (NA at State level)"
NOT_STAGED = {
    **{
        c: "reporting-process metadata"
        for c in ("pct_reported", "months_since_report", "pct_movein")
    },
    **{c: "derivable from staged counts" for c in ("people_per_unit", "person_income")},
    **{
        c: _DISTRIBUTION
        for c in [
            "pct_noincome",
            "pct_lt5k",
            "pct_5k_lt10k",
            "pct_10k_lt15k",
            "pct_15k_lt20k",
            "pct_20k_lt25k",
            "pct_25k_lt30k",
            "pct_30k_lt40k",
            "pct_ge40k",
            "pct_ge20k",
            "pct_wage_major",
            "pct_welfare_major",
            "pct_other_major",
            "pct_2adults",
            "pct_1adult",
            "pct_chldrn0_5",
            "pct_chldrn6_12",
            "pct_chldrn13_17",
            "pct_0chldrn",
            "pct_female_head",
            "pct_female_head_child",
            "pct_female_head_child0_5",
            "pct_disabled_head",
            "pct_disabled_lt62",
            "pct_disabled_ge62",
            "pct_disabled_mbr",
            "pct_disabled_all",
            "pct_lt62_head",
            "pct_lt24_head",
            "pct_age25_50",
            "pct_age51_61",
            "pct_age62plus",
            "pct_age85plus",
            "pct_minority",
            "pct_black_nonhsp",
            "pct_native_american_nonhsp",
            "pct_asian_pacific_nonhsp",
            "pct_white_nothsp",
            "pct_black_hsp",
            "pct_wht_hsp",
            "pct_oth_hsp",
            "pct_hispanic",
            "pct_multi",
            "months_waiting",
            "months_from_movein",
            "pct_utility_allow",
            "ave_util_allow",
            "pct_bed1",
            "pct_bed2",
            "pct_bed3",
            "pct_overhoused",
            "tpoverty",
            "tminority",
            "tpct_ownsfd",
        ]
    },
    **{
        c: _GEO_META
        for c in (
            [
                "fedhse",
                "cbsa",
                "place",
                "latitude",
                "longitude",
                "pha_total_units",
                "ha_size",
            ]
        )
    },
}
MISSING = {-1: "missing", -4: "suppressed", -5: "non_reporting"}
# HUD's whole-percent occupancy is not exactly round(occupied / units): in
# the 2025 files 462 of 478 cells sit within 0.5 points and the rest within
# 1.4 (small cells; HUD appears to divide unrounded unit-month averages).
# 1.5 points still catches a misaligned column.
OCCUPANCY_TOLERANCE = 0.015


def read_xlsx(path: Path) -> list[dict]:
    """The first worksheet as header-keyed rows (headers lower-cased).
    Shared strings, inline strings and numbers are decoded; nothing else
    is expected in these files."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    grid = []
    for row in sheet.find("m:sheetData", NS).findall("m:row", NS):
        cells = {}
        for c in row.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            kind, v = c.get("t"), c.find("m:v", NS)
            if kind == "s":
                value = shared[int(v.text)]
            elif kind == "inlineStr":
                value = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
            elif kind == "str":
                value = v.text if v is not None else ""
            elif kind in (None, "n"):
                value = None if v is None else float(v.text)
            else:
                raise ValueError(f"{path.name}: unexpected cell type {kind!r}")
            cells[col] = value
        grid.append(cells)
    cols = sorted(grid[0], key=lambda c: (len(c), c))
    header = [str(grid[0][c]).strip().lower() for c in cols]
    return [{h: r.get(c) for h, c in zip(header, cols)} for r in grid[1:]]


def _snapshot(quarter) -> str:
    """'31DEC2025' as published, or an Excel date serial (the 2024 files:
    45657 = 2024-12-31) normalized to the same form."""
    if isinstance(quarter, float):
        day = date(1899, 12, 30) + timedelta(days=int(quarter))
        return day.strftime("%d%b%Y").upper()
    return str(quarter).strip().upper()


def _geography(name: str, level: str) -> str:
    if level == "us":
        return "US"
    code = name.split(" ", 1)[0]
    if code in STATES or code in TERRITORIES or code == "XX":
        return code
    raise ValueError(f"unknown geography {name!r}")


def _decode(raw, scale):
    """(value, status) from a published cell."""
    if raw is None or (isinstance(raw, str) and raw.strip() in ("", "NA")):
        return None, "not_applicable"
    if isinstance(raw, str):
        raw = float(raw.strip())
    if raw < 0:
        code = int(raw)
        if code not in MISSING or raw != code:
            raise ValueError(f"unexpected negative value {raw}")
        return None, MISSING[code]
    return round(raw * scale, 6) if scale != 1 else raw, "ok"


def parse_file(path: Path, level: str, year: int) -> tuple[list[dict], Counter]:
    rows = read_xlsx(path)
    columns = set(rows[0])
    unknown = columns - set(STAGED) - IDENTITY - set(NOT_STAGED)
    if unknown:
        raise ValueError(f"{path.name}: unaccounted columns {sorted(unknown)}")
    drops: Counter = Counter()
    out = []
    for r in rows:
        label, sub = r["program_label"], r["sub_program"]
        if label not in PROGRAMS:
            raise ValueError(f"{path.name}: unknown program {label!r}")
        if sub not in SUB_PROGRAMS:
            raise ValueError(f"{path.name}: unknown sub-program {sub!r}")
        if _snapshot(r["quarter"]) != f"31DEC{year}":
            raise ValueError(f"{path.name}: snapshot {r['quarter']!r} is not {year}")
        subgroup = SUB_PROGRAMS[sub]
        if subgroup is None:
            drops["mtw_split_rows"] += 1
            continue
        geo = _geography(r["name"], level)
        for column, (metric, unit, scale) in STAGED.items():
            if column not in columns:
                continue
            value, status = _decode(r[column], scale)
            out.append(
                {
                    "source": SOURCE_ID,
                    "country": "US",
                    "program": PROGRAMS[label],
                    "metric": metric,
                    "subgroup": subgroup,
                    "variant": None,
                    "geography": geo,
                    "unit_concept": unit,
                    "period": f"31 Dec {year}",
                    "value": value,
                    "status": status,
                    "source_column": f"{path.name}:{r['name']}|{label}|{sub}|{column}",
                }
            )
    return out, drops


def _sum_check(rows, metric, tolerance_per_row, what, allow_coded_gap):
    """U.S. value vs the sum over geographies, per (program, subgroup)."""
    groups = defaultdict(lambda: {"us": None, "sum": 0.0, "n": 0, "coded": 0})
    for r in rows:
        if r["metric"] != metric:
            continue
        g = groups[(r["period"], r["program"], r["subgroup"])]
        if r["geography"] == "US":
            g["us"] = r["value"]
        elif r["status"] == "ok":
            g["sum"] += r["value"]
            g["n"] += 1
        elif r["status"] != "not_applicable":
            g["coded"] += 1
    for key, g in groups.items():
        if g["us"] is None:
            raise ValueError(f"QC failed: no U.S. row for {what} {key}")
        tol = tolerance_per_row * max(g["n"], 1)
        if g["coded"] and allow_coded_gap:
            if g["us"] < g["sum"] - tol:
                raise ValueError(
                    f"QC failed: {what} {key}: U.S. {g['us']} < {g['sum']}"
                )
        elif abs(g["us"] - g["sum"]) > tol:
            raise ValueError(
                f"QC failed: {what} {key}: U.S. {g['us']} vs sum {g['sum']}"
            )


def qc(rows: list[dict]) -> None:
    _sum_check(rows, "subsidized_units", 0.5, "units", allow_coded_gap=False)
    for metric in ("reported_households", "people"):
        _sum_check(rows, metric, 0.5, metric, allow_coded_gap=True)
    # 3: all-programs row = sum of program rows (units), per geography
    units = defaultdict(dict)
    for r in rows:
        if r["metric"] == "subsidized_units" and r["subgroup"] == "total":
            units[(r["period"], r["geography"])][r["program"]] = r["value"]
    for key, by in units.items():
        total = by.pop("all_hud_programs")
        parts = [v for v in by.values() if v is not None]
        if abs(total - sum(parts)) > 0.5 * len(parts):
            raise ValueError(
                f"QC failed: all-programs units {key}: {total} vs {sum(parts)}"
            )
    # 4: occupancy share (2025 files carry the occupied count)
    cells = defaultdict(dict)
    for r in rows:
        if r["metric"] in ("subsidized_units", "occupied_units", "occupancy_share"):
            key = (r["period"], r["geography"], r["program"], r["subgroup"])
            cells[key][r["metric"]] = r["value"]
    for key, c in cells.items():
        if None in (
            c.get("occupied_units"),
            c.get("subsidized_units"),
            c.get("occupancy_share"),
        ):
            continue
        if c["subsidized_units"] == 0:
            continue
        share = c["occupied_units"] / c["subsidized_units"]
        if abs(share - c["occupancy_share"]) > OCCUPANCY_TOLERANCE:
            raise ValueError(
                f"QC failed: occupancy {key}: {share:.4f} vs {c['occupancy_share']}"
            )


def run() -> tuple[list[dict], dict]:
    rows, drops = [], Counter()
    for year in YEARS:
        for level, stem in (("state", "STATE"), ("us", "US")):
            got, dropped = parse_file(
                RAW / f"{stem}_{year}_2020census.xlsx", level, year
            )
            rows += got
            drops += dropped
    qc(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows, dict(drops)


if __name__ == "__main__":
    out, dropped = run()
    by_status = Counter(r["status"] for r in out)
    print(f"wrote {len(out)} rows to {OUT}; drops {dropped}; status {dict(by_status)}")
