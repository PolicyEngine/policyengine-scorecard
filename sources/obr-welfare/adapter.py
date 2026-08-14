"""Adapter: OBR EFO welfare-spending baseline -> tidy rows (baseline_moment).

Input:  raw/efo_march2026_detailed_expenditure.xlsx — the March 2026
        Economic and fiscal outlook detailed forecast tables (expenditure),
        as fetched from obr.uk. This build emits Table 4.9, the
        post-measures breakdown of welfare spending by benefit.
Output: data/externals/obr-welfare.json — tidy rows in the scorecard
        schema.

These are baseline_moment claims in the sense of the tariff instance
(#29): current-law statistics from an external modeler, not reform
scores. Table 4.9 gives £bn welfare spending per benefit for 2024-25
(outturn) plus the forecast years 2025-26 to 2030-31, split into the
welfare-cap and outside-welfare-cap sections. Universal credit and
several aggregates appear in BOTH sections (the cap excludes the
jobseeking-conditionality portion of UC and the state pension), so the
cap section is carried as the variant, and section totals plus the
all-welfare total are emitted under program 'total_welfare'.

Value semantics:
    - amounts are £ BILLION at full float precision -> raw GBP
    - '*' (less than £0.1bn) -> status 'suppressed'
    - periods are financial years '2024-25'..'2030-31'; 2024-25 is
      outturn, later years are the March 2026 forecast (annotated, not
      encoded per row)

Tables 4.10 (sources of changes since November 2025) and 4.11
(health- and disability-related welfare spending) are in the same raw
workbook but not yet emitted.
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "obr-welfare"
RAW_FILE = "efo_march2026_detailed_expenditure.xlsx"
SHEET = "4.9"

MNS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NSM = {"m": MNS}

# Row label -> program slug. Footnote digits are stripped before lookup.
PROGRAMS = {
    "DWP social security": "dwp_social_security",
    "Housing benefit (not on JSA)": "housing_benefit_not_jsa",
    "Disability living allowance and personal independence payments": "dla_and_pip",
    "Incapacity benefits": "incapacity_benefits",
    "Attendance allowance": "attendance_allowance",
    "Pension credit": "pension_credit",
    "Carer's allowance": "carers_allowance",
    "Statutory maternity pay": "statutory_maternity_pay",
    "Income support (non-incapacity)": "income_support_non_incapacity",
    "Winter fuel payment": "winter_fuel_payment",
    "Universal credit": "universal_credit",
    "Other DWP in welfare cap": "other_dwp",
    "Armed forces independence payment": "armed_forces_independence_payment",
    "Bereavement benefits": "bereavement_benefits",
    "Christmas bonus": "christmas_bonus",
    "Cold weather payments": "cold_weather_payments",
    "Financial assistance scheme": "financial_assistance_scheme",
    "Industrial injuries benefits": "industrial_injuries_benefits",
    "Maternity allowance": "maternity_allowance",
    "Support for mortgage interest loans (write-offs)": "smi_loan_writeoffs",
    "Tax credits transferred debt": "tax_credits_transferred_debt",
    "Statutory sick pay": "statutory_sick_pay",
    "Personal tax credits": "personal_tax_credits",
    "Child benefit": "child_benefit",
    "Tax free childcare": "tax_free_childcare",
    "NI social security in welfare cap": "ni_social_security",
    "Paternity pay": "paternity_pay",
    "State pension": "state_pension",
    "Jobseeker's allowance": "jobseekers_allowance",
    "Housing benefit (on JSA)": "housing_benefit_on_jsa",
    "Other DWP outside welfare cap": "other_dwp",
    "NI social security outside welfare cap": "ni_social_security",
}

SECTION_STARTS = {
    "Welfare cap": "in_welfare_cap",
    "Welfare spending outside the welfare cap": "outside_welfare_cap",
}

TOTALS = {
    "Total welfare cap": ("total_welfare", "in_welfare_cap"),
    "Total welfare outside the welfare cap": ("total_welfare", "outside_welfare_cap"),
    "Total welfare": ("total_welfare", None),
}

SKIP_LABELS = {"of which:"}


def col_index(ref):
    n = 0
    for ch in re.match(r"([A-Z]+)", ref).group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_sheet(path, sheet_name):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    targets = {
        s.get("name"): relmap[s.get(f"{{{RNS}}}id")]
        for s in wb.findall(".//m:sheet", NSM)
    }
    strings = [
        "".join(t.text or "" for t in si.iter(f"{{{MNS}}}t"))
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NSM)
    ]
    target = targets[sheet_name]
    if not target.startswith("xl/"):
        target = "xl/" + target
    rows = []
    for row in ET.fromstring(z.read(target)).findall(".//m:row", NSM):
        cells = {}
        for c in row.findall("m:c", NSM):
            v = c.find("m:v", NSM)
            val = v.text if v is not None else None
            if c.get("t") == "s" and val is not None:
                val = strings[int(val)]
            cells[col_index(c.get("r"))] = val
        rows.append(cells)
    return rows


def run():
    rows_out = []
    sheet = read_sheet(HERE / "raw" / RAW_FILE, SHEET)

    year_row = next(
        r for r in sheet if any(re.match(r"^\d{4}-\d{2}$", str(v)) for v in r.values())
    )
    periods = {i: v for i, v in year_row.items() if re.match(r"^\d{4}-\d{2}$", str(v))}

    variant = None
    for cells in sheet:
        label = cells.get(1)
        if not isinstance(label, str):
            continue
        label = label.strip()
        if label in SECTION_STARTS:
            variant = SECTION_STARTS[label]
            continue
        if label in SKIP_LABELS:
            continue
        base = re.sub(r"\d+$", "", label)  # trailing footnote marker
        if label in TOTALS:
            program, row_variant = TOTALS[label]
        elif base in PROGRAMS:
            if variant is None:
                raise ValueError(f"4.9: benefit row before a section: {label!r}")
            program, row_variant = PROGRAMS[base], variant
        else:
            continue  # title, units, footnote prose
        for i, period in periods.items():
            raw = cells.get(i)
            if raw is None:
                raise ValueError(f"4.9 {label!r} {period}: missing cell")
            if raw == "*":
                value, status = None, "suppressed"
            else:
                value, status = float(raw) * 1e9, "ok"
            rows_out.append(
                {
                    "source": SOURCE_ID,
                    "country": "UK",
                    "program": program,
                    "metric": "welfare_spending",
                    "subgroup": "total",
                    "variant": row_variant,
                    "geography": "UK",  # refined per administration below
                    "unit_concept": "gbp_nominal",
                    "period": period,
                    "value": value,
                    "status": status,
                    "source_column": f"4.9:{label}",
                }
            )

    # Geography per administration: DWP benefit lines are GB (Northern
    # Ireland's mirror payments are the 'NI social security' rows); the
    # HMRC-administered lines (child benefit, tax credits, tax-free
    # childcare, statutory payments) and the totals span the UK.
    UK_WIDE = {
        "child_benefit",
        "personal_tax_credits",
        "tax_free_childcare",
        "statutory_maternity_pay",
        "statutory_sick_pay",
        "paternity_pay",
        "total_welfare",
    }
    for r in rows_out:
        if r["program"] == "ni_social_security":
            r["geography"] = "NI"
        elif r["program"] not in UK_WIDE:
            r["geography"] = "GB"

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows_out))
    print(f"{len(rows_out)} rows -> {out}")

    # --- validation: internal identities + published figures ---
    def get(program, period, variant):
        for r in rows_out:
            if (
                r["program"] == program
                and r["period"] == period
                and r["variant"] == variant
            ):
                return r["value"]
        raise KeyError((program, period, variant))

    failed = False
    checks = [
        (
            "state pension 2025-26 ~£146.2bn",
            get("state_pension", "2025-26", "outside_welfare_cap"),
            146.2e9,
            0.05e9,
        ),
        (
            "UC in cap 2025-26 ~£66.4bn",
            get("universal_credit", "2025-26", "in_welfare_cap"),
            66.4e9,
            0.05e9,
        ),
        (
            "total welfare 2025-26 ~£332.9bn",
            get("total_welfare", "2025-26", None),
            332.9e9,
            0.05e9,
        ),
    ]
    for label, got, want, tol in checks:
        ok = got is not None and abs(got - want) < tol
        print(f"  {'OK ' if ok else 'FAIL'} {label}: {got}")
        failed = failed or not ok
    # identity: cap + outside = total, every year
    for period in sorted({r["period"] for r in rows_out}):
        cap = get("total_welfare", period, "in_welfare_cap")
        outside = get("total_welfare", period, "outside_welfare_cap")
        total = get("total_welfare", period, None)
        ok = abs((cap + outside) - total) < 1e6
        print(f"  {'OK ' if ok else 'FAIL'} identity cap+outside=total {period}")
        failed = failed or not ok
    print(f"  suppressed cells: {sum(r['status'] == 'suppressed' for r in rows_out)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
