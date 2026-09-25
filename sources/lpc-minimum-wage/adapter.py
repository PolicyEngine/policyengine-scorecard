"""Adapter: Low Pay Commission minimum-wage coverage and bite (#88).

Inputs (raw/, GOV.UK originals with SHA-256 pins — see raw/README.md):

  lpc_2025_main_report_data.xlsx
      5.2         bite and coverage of the adult rate, UK, 1999-2025
      6.7 right   bite by age band, UK, 2013-2025
  lpc_2025_coverage_by_la_region_nation.xlsx
      Region and nation   coverage (jobs and per cent), April 2025

Output: data/externals/lpc-minimum-wage.json — tidy rows.

PolicyEngine-UK carries a minimum-wage implementation — `minimum_wage`,
`minimum_wage_category`, and a parameter tree at
`gov.hmrc.minimum_wage` — and nothing on the scorecard validates any of
it. This is the external side.

Two quantities, and they are NOT the same shape as anything else in this
repo:

  coverage   how many jobs are paid at or below the applicable rate,
             as a COUNT OF JOBS and as a per cent of jobs
  bite       the rate as a per cent of median hourly pay

A JOB IS NOT A PERSON and not a household. One person can hold two jobs
and one household several; every population already in this repo counts
people, households, benefit units or families. Coverage counts jobs, so
it carries its own unit concept rather than being mapped onto `persons`
because that unit happened to exist.

BITE IS A DIFFERENT-DATA COMPARISON BEFORE IT IS ANYTHING ELSE. Its
denominator is the ASHE median hourly wage of full-time workers; ASHE is
a JOBS survey of employers and PolicyEngine-UK's certified world is
FRS-based, a household survey. A PE-vs-LPC bite divergence therefore
starts as a survey-population difference and only becomes an engine
question after that axis is sized. The adapter records the denominator
on every bite row so the axis is visible on the claim rather than
remembered.

Periods are ASHE April reference years, carried as calendar years.
"""

import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "lpc-minimum-wage"
EDITION = "Low Pay Commission Report 2025"

MNS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

SHA256 = {
    "lpc_2025_main_report_data.xlsx": (
        "bd0c10dc42bc04d5af09792731464b9549f971a3ff36f9c2ddf0ee69281f08ee"
    ),
    "lpc_2025_coverage_by_la_region_nation.xlsx": (
        "2cab42281f0b8094ab1a9077016cf21b91e1069da1fe7dd07f7bb771e108498d"
    ),
}

# The coverage annex's reference year: the 2025 report's coverage tables
# are April 2025 ASHE. Stated here rather than inferred from the filename.
COVERAGE_YEAR = 2025

# LPC's region labels -> the repo's registered UK geography vocabulary.
# Closed: an unregistered label raises rather than minting a geography.
REGIONS = {
    "East Midlands": "East Midlands",
    "East of England": "East",
    "London": "London",
    "North East": "North East",
    "North West": "North West",
    "Northern Ireland": "Northern Ireland",
    "Scotland": "Scotland",
    "South East": "South East",
    "South West": "South West",
    "Wales": "Wales",
    "West Midlands": "West Midlands",
    "Yorkshire and the Humber": "Yorkshire and the Humber",
    "UK": "UK",
}

# Age bands in figure 6.7 right, as published.
AGE_BANDS = {
    "16-17 (per cent)": "age_16_17",
    "18-20 (per cent)": "age_18_20",
    "25+ (per cent)": "age_25_plus",
}

# The bite denominator, recorded on every bite claim: this is the axis a
# PE counterpart diverges on first.
BITE_DENOMINATOR = (
    "ASHE median hourly wage of full-time workers (employer jobs survey); "
    "PolicyEngine-UK's certified world is FRS-based, a household survey, "
    "so a PE-vs-LPC bite gap is a survey-population difference before it "
    "is an engine question"
)

# Sheets in the 193-sheet main annex that this adapter reads. Everything
# else is surveyed and tallied as unread, never silently consumed.
MAIN_SHEETS_READ = ("5.2", "6.7 right")


def _check_sha(fname):
    digest = hashlib.sha256((RAW / fname).read_bytes()).hexdigest()
    if digest != SHA256[fname]:
        raise RuntimeError(
            f"{fname}: sha256 {digest} != pinned {SHA256[fname]} — the raw "
            "file drifted from the bytes this adapter was written against"
        )


def _sheet_names(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    return [s.get("name") for s in wb.iter(MNS + "sheet")]


def _grid(path, sheet_name):
    """Sheet -> {(row, col): value} with shared strings resolved."""
    z = zipfile.ZipFile(path)
    try:
        ss = [
            "".join(t.text or "" for t in si.iter(MNS + "t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(MNS + "si")
        ]
    except KeyError:
        ss = []
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {
        r.get("Id"): r.get("Target")
        for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    }
    for s in wb.iter(MNS + "sheet"):
        if s.get("name") != sheet_name:
            continue
        root = ET.fromstring(z.read("xl/" + rels[s.get(RNS + "id")].lstrip("/")))
        grid = {}
        for row in root.iter(MNS + "row"):
            for c in row.iter(MNS + "c"):
                v = c.find(MNS + "v")
                if v is None:
                    continue
                m = re.match(r"([A-Z]+)(\d+)", c.get("r"))
                col = 0
                for ch in m.group(1):
                    col = col * 26 + (ord(ch) - 64)
                grid[(int(m.group(2)), col)] = (
                    ss[int(v.text)] if c.get("t") == "s" else v.text
                )
        return grid
    raise KeyError(f"{path.name}: no sheet {sheet_name!r}")


def _title(grid, expect_prefix, cell=(1, 1)):
    got = str(grid.get(cell, "")).strip()
    if not got.startswith(expect_prefix):
        raise RuntimeError(f"title anchor failed: {got!r} !~ {expect_prefix!r}")
    return got


def _closed(registry, key, what):
    try:
        return registry[key]
    except KeyError:
        raise RuntimeError(
            f"unregistered {what}: {key!r} — the published table changed. "
            "Register it deliberately, never pass it through"
        ) from None


def _row(**kw):
    base = {
        "source": SOURCE_ID,
        "country": "UK",
        "edition": EDITION,
        "status": "ok",
    }
    base.update(kw)
    return base


def parse_adult_series(out):
    """Figure 5.2: bite and coverage of the adult rate, UK, 1999-2025."""
    path = RAW / "lpc_2025_main_report_data.xlsx"
    grid = _grid(path, "5.2")
    _title(grid, "Figure 5.2: Bite and coverage rate of the adult minimum wage")
    n = 0
    for r in sorted({r for (r, c) in grid if r > 2 and (r, 1) in grid}):
        year = int(str(grid[(r, 1)]).strip())
        for col, (metric, unit, extra) in {
            2: ("minimum_wage_bite", "percent", {"denominator": BITE_DENOMINATOR}),
            3: ("minimum_wage_coverage_rate", "percent", {}),
        }.items():
            if (r, col) not in grid:
                continue
            out.append(
                _row(
                    metric=metric,
                    unit_concept=unit,
                    geography="UK",
                    subgroup="age_25_plus",
                    period=year,
                    value=float(grid[(r, col)]),
                    rate_scope="adult_rate",
                    source_column=f"5.2:{'bite' if col == 2 else 'coverage'}:{year}",
                    **extra,
                )
            )
            n += 1
    return n


def parse_bite_by_age(out):
    """Figure 6.7 right: bite by age band, UK, 2013-2025."""
    path = RAW / "lpc_2025_main_report_data.xlsx"
    grid = _grid(path, "6.7 right")
    _title(grid, "Figure 6.7 right: Bite, by age")
    headers = {
        c: str(v).strip() for (r, c), v in grid.items() if r == 2 and c >= 2
    }
    n = 0
    for r in sorted({r for (r, c) in grid if r > 2 and (r, 1) in grid}):
        year = int(str(grid[(r, 1)]).strip())
        for c, label in sorted(headers.items()):
            if (r, c) not in grid:
                continue
            out.append(
                _row(
                    metric="minimum_wage_bite",
                    unit_concept="percent",
                    geography="UK",
                    subgroup=_closed(AGE_BANDS, label, "age band"),
                    period=year,
                    value=float(grid[(r, c)]),
                    rate_scope="age_band_rate",
                    denominator=BITE_DENOMINATOR,
                    source_column=f"6.7 right:{label}:{year}",
                )
            )
            n += 1
    return n


def parse_regional_coverage(out):
    """Coverage annex, `Region and nation`: jobs and per cent, April 2025."""
    path = RAW / "lpc_2025_coverage_by_la_region_nation.xlsx"
    grid = _grid(path, "Region and nation")
    _title(grid, "Table 2: Coverage of the N")
    n = 0
    for r in sorted({r for (r, c) in grid if r > 2 and (r, 1) in grid}):
        label = str(grid[(r, 1)]).strip()
        geography = _closed(REGIONS, label, "region/nation")
        for col, (metric, unit) in {
            2: ("minimum_wage_coverage", "jobs"),
            3: ("minimum_wage_coverage_rate", "percent"),
        }.items():
            if (r, col) not in grid:
                continue
            out.append(
                _row(
                    metric=metric,
                    unit_concept=unit,
                    geography=geography,
                    subgroup="age_16_plus",
                    period=COVERAGE_YEAR,
                    value=float(grid[(r, col)]),
                    rate_scope="all_nmw_nlw_rates",
                    source_column=f"Region and nation:{label}:{metric}",
                )
            )
            n += 1
    return n


def build():
    for fname in SHA256:
        _check_sha(fname)
    rows = []
    counts = {
        "adult_series": parse_adult_series(rows),
        "bite_by_age": parse_bite_by_age(rows),
        "regional_coverage": parse_regional_coverage(rows),
    }

    # What was NOT read, tallied rather than implied.
    main_sheets = _sheet_names(RAW / "lpc_2025_main_report_data.xlsx")
    coverage_sheets = _sheet_names(RAW / "lpc_2025_coverage_by_la_region_nation.xlsx")
    la_grid = _grid(
        RAW / "lpc_2025_coverage_by_la_region_nation.xlsx", "Local authority"
    )
    la_rows = len({r for (r, c) in la_grid if r > 2 and (r, 1) in la_grid})
    unread = {
        "main_annex_sheets_unread": {
            "sheets": len(main_sheets) - len(MAIN_SHEETS_READ),
            "reason": (
                "The other published figures of the report — earnings "
                "distributions, employment effects, international "
                "comparisons. Each is its own population decision, not "
                "something to sweep in because the file was already open."
            ),
        },
        "local_authority_coverage_rows": {
            "rows": la_rows,
            "reason": (
                "Local-authority geography is finer than any UK geography "
                "this repo registers, and the certified policyengine-uk "
                "world cannot resolve it either. Opening an LA vocabulary "
                "for one table would create identities nothing else can "
                "join to."
            ),
        },
    }
    if len(coverage_sheets) != 4:
        raise RuntimeError(f"coverage annex changed shape: {coverage_sheets}")

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"wrote {len(rows)} rows -> {out}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    for k, v in unread.items():
        print(f"  NOT READ {k}: {v.get('sheets', v.get('rows'))}")
    return rows, counts, unread


if __name__ == "__main__":
    build()
