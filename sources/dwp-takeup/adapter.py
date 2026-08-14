"""Adapter: DWP Income-related benefits estimates of take-up -> tidy rows.

Input:  raw/pension_credit_tables_fye_2324.ods
        raw/housing_benefit_tables_fye_2324.ods
        (FYE 2024 publication, 2025-10-30, tables as fetched from gov.uk)
Output: data/externals/dwp-takeup.json — tidy rows in the scorecard schema.

Table grammar (verified against the full 12-sheet inventory):
    - caseload sheets (PC odd, HB1): 'Number of recipients',
      'Estimated number of entitled non-recipients (with range)' (Thousands),
      'Estimated caseload take-up (with range)' (%)
    - expenditure sheets (PC even, HB2): mean/median weekly amounts
      (£ nominal), 'Total amount claimed' / 'Estimated amount unclaimed
      (with range)' (£ millions nominal), 'Estimated expenditure take-up
      (with range)' (%)
    - column groups of 3 (central, range-low, range-high); range cells are
      text like '(1,550,' / '1,730)'
    - PC1/PC2 break Pension Credit down by entitlement: the 'Guarantee
      Credit' column is the same concept as the PC5-PC10 Guarantee Credit
      tables' 'All' column, so both map to program=guarantee_credit and the
      exact-duplicate rows are deduplicated under an equality assertion

Value semantics:
    - counts are in THOUSANDS -> emitted as raw benefit units
    - take-up rates are integer percents -> emitted as fractions 0-1
    - 'Total amount claimed'/'amount unclaimed' are £ millions -> raw £
    - '[x]' = FYE 2021 COVID suppression; '[u]' = small sample (<50);
      both -> status 'suppressed'
    - no FYE 2011/2012 rows exist (methodology break, by design)
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "dwp-takeup"
GEOGRAPHY = "GB"  # private households, Great Britain only (no subnational)

TNS = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
TEXTNS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
NS = {"table": TNS, "text": TEXTNS}

FILES = {
    "pension_credit_tables_fye_2324.ods": r"^PC\d+$",
    "housing_benefit_tables_fye_2324.ods": r"^HB\d+$",
}

# Column-group label -> (program, subgroup). Family-type/age groups keep the
# sheet's program (resolved from the table title) and set only the subgroup.
GROUPS = {
    "Pension Credit Overall": ("pension_credit", "total"),
    "Guarantee Credit": ("guarantee_credit", "total"),
    "Savings Credit only": ("savings_credit_only", "total"),
    "All": (None, "total"),
    "Couples": (None, "couples"),
    "Single Males": (None, "single_male"),
    "Single Females": (None, "single_female"),
    "Aged under 75": (None, "age_under_75"),
    "Aged 75 or over": (None, "age_75_plus"),
}

# Table-title program phrases -> program id (for sheets whose columns are
# family-type/age subgroups rather than entitlement components).
TITLE_PROGRAMS = [
    ("of Guarantee Credit", "guarantee_credit"),
    ("of Pension Credit", "pension_credit"),
    ("of Housing Benefit for Pensioners", "housing_benefit_pensioners"),
]

# Section label -> (metric, scale, unit_concept, has_range).
# Counts and rates count DWP 'families' = benefit units (single pensioner or
# couple); money is nominal GBP.
SECTIONS = {
    "Number of recipients": ("recipients_count", 1000, "benefit_units", False),
    "Estimated number of entitled non-recipients (with range)": (
        "entitled_nonrecipients_count",
        1000,
        "benefit_units",
        True,
    ),
    "Estimated caseload take-up (with range)": (
        "caseload_takeup_rate",
        0.01,
        "benefit_units",
        True,
    ),
    "Mean weekly amount claimed": (
        "mean_weekly_amount_claimed",
        1,
        "gbp_per_week_nominal",
        False,
    ),
    "Mean weekly amount unclaimed": (
        "mean_weekly_amount_unclaimed",
        1,
        "gbp_per_week_nominal",
        False,
    ),
    "Median weekly amount unclaimed": (
        "median_weekly_amount_unclaimed",
        1,
        "gbp_per_week_nominal",
        False,
    ),
    "Total amount claimed": (
        "total_amount_claimed",
        1_000_000,
        "gbp_annual_nominal",
        False,
    ),
    "Estimated amount unclaimed (with range)": (
        "amount_unclaimed",
        1_000_000,
        "gbp_annual_nominal",
        True,
    ),
    "Estimated expenditure take-up (with range)": (
        "expenditure_takeup_rate",
        0.01,
        "benefit_units",
        True,
    ),
}

UNIT_MARKERS = {"Thousands", "%", "£, nominal terms", "£ millions, nominal terms"}
SUPPRESSED = {"[x]", "[u]"}


def sheet_rows(path):
    """Yield (sheet_name, rows) where rows are lists of cell display text."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("content.xml"))
    for t in root.findall(".//table:table", NS):
        name = t.get(f"{{{TNS}}}name")
        rows = []
        for r in t.findall("table:table-row", NS):
            row = []
            for c in r.findall("table:table-cell", NS):
                rep = int(c.get(f"{{{TNS}}}number-columns-repeated", "1"))
                txt = " ".join(
                    "".join(p.itertext()) for p in c.findall("text:p", NS)
                ).strip()
                row.extend([txt] * min(rep, 30))
            rows.append(row)
        yield name, rows


def parse_number(text):
    """'2,590' / '(1,550,' / '1,730)' / '62' -> float; suppression -> marker."""
    if text in SUPPRESSED:
        return None, "suppressed"
    cleaned = re.sub(r"[(),\s]", "", text)
    if cleaned in ("", "-"):
        return None, "empty"
    return float(cleaned), "ok"


def parse_sheet(sheet, rows):
    title = next((r[0] for r in rows if r and r[0].startswith(f"Table {sheet}:")), None)
    if title is None:
        raise ValueError(f"{sheet}: no table title row")
    sheet_program = next((p for phrase, p in TITLE_PROGRAMS if phrase in title), None)
    if sheet_program is None:
        raise ValueError(f"{sheet}: unrecognized program in title: {title}")

    # Column groups: the header row is the first row with an empty first cell
    # whose non-empty cells are all known group labels.
    groups = None  # list of (start_col, program, subgroup)
    section = None
    out = []
    for row in rows:
        non_empty = [(i, x) for i, x in enumerate(row) if x]
        if not non_empty:
            continue
        first = row[0] if row else ""
        if not first:
            labels = [x for _, x in non_empty]
            if all(x in UNIT_MARKERS for x in labels):
                continue  # unit marker row; units are fixed per section
            if all(x in GROUPS for x in labels):
                groups = []
                for i, label in non_empty:
                    program, subgroup = GROUPS[label]
                    groups.append((i, program or sheet_program, subgroup, label))
                continue
            raise ValueError(f"{sheet}: unrecognized header row: {labels}")
        if first in SECTIONS:
            section = first
            continue
        m = re.match(r"^FYE (\d{4})$", first)
        if not m:
            section = None  # prose row (title, navigation, notes pointer)
            continue
        if section is None or groups is None:
            raise ValueError(f"{sheet}: data row outside a section: {first}")
        period = f"FYE {m.group(1)}"
        metric, scale, unit_concept, has_range = SECTIONS[section]
        for start, program, subgroup, label in groups:
            cells = [(row[c] if c < len(row) else "") for c in range(start, start + 3)]
            variants = [(0, None)]
            if has_range:
                variants += [(1, "range_low"), (2, "range_high")]
            for offset, variant in variants:
                value, status = parse_number(cells[offset])
                if status == "empty":
                    if variant is None:
                        raise ValueError(
                            f"{sheet} {period} {label} {section}: empty central cell"
                        )
                    continue
                out.append(
                    {
                        "source": SOURCE_ID,
                        "country": "UK",
                        "program": program,
                        "metric": metric,
                        "subgroup": subgroup,
                        "variant": variant,
                        "geography": GEOGRAPHY,
                        "unit_concept": unit_concept,
                        "period": period,
                        "value": None if value is None else value * scale,
                        "status": "suppressed" if value is None else "ok",
                        "source_column": f"{sheet}:{label}",
                    }
                )
    return out


def run():
    rows = []
    for fname, sheet_pat in FILES.items():
        for sheet, raw_rows in sheet_rows(HERE / "raw" / fname):
            if re.match(sheet_pat, sheet):
                rows.extend(parse_sheet(sheet, raw_rows))

    # The GC column of PC1/PC2 and the All column of PC5-PC10 (and the PC
    # overall column vs PC3/PC4/PC7/PC8 All) state the same cells twice;
    # collapse exact key duplicates, refusing silently-divergent values.
    deduped = {}
    for r in rows:
        key = (r["program"], r["metric"], r["subgroup"], r["variant"], r["period"])
        if key in deduped:
            if deduped[key]["value"] != r["value"]:
                raise SystemExit(
                    f"duplicate key with divergent values: {key}: "
                    f"{deduped[key]['value']} ({deduped[key]['source_column']}) "
                    f"vs {r['value']} ({r['source_column']})"
                )
            continue
        deduped[key] = r
    rows = list(deduped.values())

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows))
    print(f"{len(rows)} rows -> {out}")

    # --- validation against the FYE 2024 publication's headline numbers ---
    def get(program, metric, subgroup="total", variant=None, period="FYE 2024"):
        for r in rows:
            if (
                r["program"] == program
                and r["metric"] == metric
                and r["subgroup"] == subgroup
                and r["variant"] == variant
                and r["period"] == period
            ):
                return r["value"]
        raise KeyError((program, metric, subgroup, variant, period))

    checks = [
        (
            "PC caseload take-up 62%",
            get("pension_credit", "caseload_takeup_rate"),
            0.62,
        ),
        (
            "PC expenditure take-up 71%",
            get("pension_credit", "expenditure_takeup_rate"),
            0.71,
        ),
        ("PC recipients 1.32M", get("pension_credit", "recipients_count"), 1_320_000),
        (
            "PC ENR central 820k",
            get("pension_credit", "entitled_nonrecipients_count"),
            820_000,
        ),
        (
            "PC ENR 'up to 910,000'",
            get("pension_credit", "entitled_nonrecipients_count", variant="range_high"),
            910_000,
        ),
        # the report headline rounds the table's £2,480m to 'up to £2.5bn'
        (
            "PC unclaimed 'up to £2.5bn'",
            get("pension_credit", "amount_unclaimed", variant="range_high"),
            2_480_000_000,
        ),
        (
            "GC caseload take-up 69%",
            get("guarantee_credit", "caseload_takeup_rate"),
            0.69,
        ),
        (
            "HB pensioner caseload take-up 85%",
            get("housing_benefit_pensioners", "caseload_takeup_rate"),
            0.85,
        ),
        (
            "HB pensioner expenditure take-up 87%",
            get("housing_benefit_pensioners", "expenditure_takeup_rate"),
            0.87,
        ),
        (
            "HB pensioner recipients 1.10M",
            get("housing_benefit_pensioners", "recipients_count"),
            1_100_000,
        ),
        (
            "HB ENR 'up to 230,000'",
            get(
                "housing_benefit_pensioners",
                "entitled_nonrecipients_count",
                variant="range_high",
            ),
            230_000,
        ),
        (
            "HB unclaimed 'up to £1.1bn'",
            get("housing_benefit_pensioners", "amount_unclaimed", variant="range_high"),
            1_100_000_000,
        ),
    ]
    failed = False
    for label, got, want in checks:
        ok = got is not None and abs(got - want) < 1e-9
        print(f"  {'OK ' if ok else 'FAIL'} {label}: {got}")
        failed = failed or not ok
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
