"""Adapter: DWP workplace pension participation (#98).

Input:  raw/dwp_workplace_pension_participation_2009_2025.xlsx — the DWP
        "Workplace pension participation and savings trends: 2009 to
        2025" data tables (published 2026-07-30; see raw/README.md).
Output: data/externals/dwp-pension-participation.json — tidy rows.

PolicyEngine-UK models pensions — contributions, relief, the age limit,
the salary-sacrifice interaction — and until now not one of the 15,858
UK external claims said anything about pensions at all. This is the
external side.

The measure is PARTICIPATION: the share of ELIGIBLE employees saving
into a workplace pension, by earnings band, age band and region, split
Public / Private / Overall, 2009-2025.

Three things the publication forces, each handled explicitly:

1. **Eligibility is part of the identity, not a footnote.** The
   denominator is employees ELIGIBLE for automatic enrolment — which is
   itself defined by an earnings trigger and an age range that have
   moved over the series. A participation rate whose denominator is
   unstated is uninterpretable, so every row carries the population it
   is a share of.

2. **The sheets hold SIX tables side by side and only the first is
   labelled.** Row 6 of each sheet describes block 1 ("Percentage of
   eligible employees participating") and is blank above the other five.
   Rather than guess what the unlabelled blocks measure, this adapter
   reads block 1 and TALLIES the other five as deliberately unread. A
   number whose meaning is inferred from position is not a claim.

3. **The source is ASHE**, an employer survey of jobs — the same survey
   behind the Low Pay Commission lane (#88). So the same divergence axis
   applies: PE-UK's certified world is FRS-based, a household survey,
   and a PE-vs-DWP participation gap is a survey-population difference
   before it is an engine question. That axis rides on every row.
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

SOURCE_ID = "dwp-pension-participation"
EDITION = "Workplace pension participation and savings trends: 2009 to 2025"

MNS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

WORKBOOK = "dwp_workplace_pension_participation_2009_2025.xlsx"
SHA256 = {
    WORKBOOK: "4d4bd871b23f9ef763101b4491bce437f3c02e622ce9394c857c0346fb326e41"
}

# Block 1 is the only labelled table on each sheet; its descriptor sits
# at row 6 column 1 and is anchored so a re-shuffled workbook fails.
BLOCK1_ANCHOR = "Percentage of eligible employees participating"
BLOCK_WIDTH = 18  # label column + 17 years
HEADER_ROW = 8
BLOCKS_PER_SHEET = 6

SECTORS = {"Public": "public", "Private": "private", "Overall": "all"}

# sheet -> (axis name, {published label: canonical value})
SHEETS = {
    "1.3a": (
        "earnings_band",
        {
            "£10,000 - under £20,000": "gbp_10k_20k",
            "£20,000 - under £30,000": "gbp_20k_30k",
            "£30,000 - under £40,000": "gbp_30k_40k",
            "£40,000 - under £50,000": "gbp_40k_50k",
            "£50,000 - under £60,000": "gbp_50k_60k",
            "£60,000 - under £70,000": "gbp_60k_70k",
            "£70,000+": "gbp_70k_plus",
        },
    ),
    "1.4": (
        "age_band",
        {
            "22 to 25": "age_22_25",
            "26 to 30": "age_26_30",
            "31 to 35": "age_31_35",
            "36 to 40": "age_36_40",
            "41 to 45": "age_41_45",
            "46 to 50": "age_46_50",
            "51 to 55": "age_51_55",
            "56 to 60": "age_56_60",
            "61 to 65": "age_61_65",
        },
    ),
    "1.9a": (
        "region",
        {
            "North East": "North East",
            "North West": "North West",
            "Yorkshire & The Humber": "Yorkshire and the Humber",
            "East Midlands": "East Midlands",
            "West Midlands": "West Midlands",
            "South West": "South West",
            "East": "East",
            "London": "London",
            "South East": "South East",
            "Wales": "Wales",
            "Scotland": "Scotland",
        },
    ),
}

DENOMINATOR = (
    "Employees ELIGIBLE for automatic enrolment — an earnings-trigger and "
    "age-range definition that has moved over the series. A participation "
    "rate whose denominator is unstated is uninterpretable, so it is carried "
    "on every row rather than left in a methodology note."
)
SURVEY_AXIS = (
    "DWP estimates derived from ONS ASHE, an employer survey of JOBS in "
    "Great Britain. PolicyEngine-UK's certified world is FRS-based, a "
    "household survey, so a PE-vs-DWP participation gap is a "
    "survey-population difference before it is an engine question — the same "
    "axis the Low Pay Commission lane (#88) carries."
)
GEOGRAPHY = "GB"


def _check_sha(fname):
    digest = hashlib.sha256((RAW / fname).read_bytes()).hexdigest()
    if digest != SHA256[fname]:
        raise RuntimeError(
            f"{fname}: sha256 {digest} != pinned {SHA256[fname]} — the raw "
            "file drifted from the bytes this adapter was written against"
        )


def _grid(path, sheet_name):
    z = zipfile.ZipFile(path)
    ss = [
        "".join(t.text or "" for t in si.iter(MNS + "t"))
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(MNS + "si")
    ]
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
    raise KeyError(f"no sheet {sheet_name!r}")


def _closed(registry, key, what):
    try:
        return registry[key]
    except KeyError:
        raise RuntimeError(
            f"unregistered {what}: {key!r} — the published table changed. "
            "Register it deliberately, never pass it through"
        ) from None


def parse_sheet(sheet, out):
    """Block 1 of one sheet: sector x category x year participation rates."""
    grid = _grid(RAW / WORKBOOK, sheet)
    descriptor = str(grid.get((6, 1), "")).strip()
    if not descriptor.startswith(BLOCK1_ANCHOR):
        raise RuntimeError(
            f"{sheet}: block-1 anchor failed ({descriptor!r}); the workbook "
            "was re-shuffled and the unlabelled blocks make position-based "
            "reading unsafe"
        )
    axis, categories = SHEETS[sheet]

    # years live on the header row within block 1 only
    years = {
        c: int(str(v).strip())
        for (r, c), v in grid.items()
        if r == HEADER_ROW and 2 <= c <= BLOCK_WIDTH and str(v).strip().isdigit()
    }
    if not years:
        raise RuntimeError(f"{sheet}: no year headers in block 1")

    sector = None
    n = 0
    for r in sorted({r for (r, c) in grid if c == 1 and r >= HEADER_ROW}):
        label = str(grid.get((r, 1), "")).strip()
        if label in SECTORS:
            sector = SECTORS[label]
            continue
        if not label or sector is None:
            continue
        category = _closed(categories, label, f"{sheet} {axis}")
        for c, year in sorted(years.items()):
            if (r, c) not in grid:
                continue
            out.append(
                {
                    "source": SOURCE_ID,
                    "country": "UK",
                    "geography": GEOGRAPHY,
                    "program": "workplace_pension",
                    "metric": "participation_rate",
                    "unit_concept": "share",
                    "sector": sector,
                    "axis": axis,
                    "subgroup": category,
                    "period": year,
                    "value": float(grid[(r, c)]),
                    "denominator": DENOMINATOR,
                    "survey_axis": SURVEY_AXIS,
                    "status": "ok",
                    "edition": EDITION,
                    "source_column": f"{sheet}:block1:{label}:{sector}:{year}",
                }
            )
            n += 1
    return n


def build():
    for fname in SHA256:
        _check_sha(fname)
    rows = []
    counts = {sheet: parse_sheet(sheet, rows) for sheet in SHEETS}

    # What is deliberately NOT read, tallied rather than implied.
    z = zipfile.ZipFile(RAW / WORKBOOK)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    all_sheets = [s.get("name") for s in wb.iter(MNS + "sheet")]
    unread = {
        "unlabelled_side_by_side_blocks": {
            "blocks": (BLOCKS_PER_SHEET - 1) * len(SHEETS),
            "reason": (
                "Each sheet holds six tables side by side and only the first "
                "carries a descriptor (row 6). The other five are unlabelled, "
                "and a number whose meaning is inferred from its column "
                "position is not a claim. They are read when DWP labels them "
                "or the methodology note is transcribed deliberately."
            ),
        },
        "sheets_not_read": {
            "sheets": len(all_sheets) - len(SHEETS) - 4,  # less Cover/Contents/Guidance/Notes
            "reason": (
                "The other data sheets — by sector, employer size, gender, "
                "working pattern, industry, occupation, and the savings-level "
                "tables — are each their own population decision rather than "
                "something to sweep in because the file was already open."
            ),
        },
    }

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"wrote {len(rows)} rows -> {out}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    for k, v in unread.items():
        print(f"  NOT READ {k}: {v.get('blocks', v.get('sheets'))}")
    return rows, counts, unread


if __name__ == "__main__":
    build()
