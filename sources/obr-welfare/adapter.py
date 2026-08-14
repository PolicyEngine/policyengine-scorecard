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

Hierarchy (aggregate_level / parent):
    Table 4.9 is NESTED, not flat. 'DWP social security' is the sum of
    the eleven rows under its 'of which:' marker, and 'Other DWP in
    welfare cap' is itself the sum of the ten rows under a second,
    deeper 'of which:'. Emitting all rows as siblings makes any naive
    aggregation double-count: the in-cap non-total rows sum to
    £319.85bn for 2025-26 against a published cap total of £169.13bn,
    a 1.89x overstatement.

    So every row carries:
      - aggregate_level: 'component' (a leaf), 'subtotal' (an
        aggregate that is itself inside a larger one), or 'total' (a
        section total / the all-welfare total)
      - parent: the program slug of the aggregate this row rolls into,
        resolved within the SAME variant and period; None for the
        three total rows

    The hierarchy is read from the workbook, never assumed: an
    'of which:' marker at indentation level L declares the preceding
    level-L row to be the parent of the following level-L+1 rows, and
    the levels come from each label cell's style indent. A row that is
    indented without a governing 'of which:' marker is a hard error.

    The three total rows relate by the cap + outside = total identity
    rather than by parent links, since all three share the
    'total_welfare' program slug and are distinguished by variant.

Tolerances used by the checks below:
    - PARENT_TOL = £1. Values arrive as full float64 £bn and are scaled
      by 1e9, so summing <= 11 terms of order 1e2 carries only ~1e-13
      £bn (~£1e-4) of representation error; in practice every parent
      whose components are all published reconciles to exactly 0.0.
      £1 sits ~4 orders above that noise and ~8 orders below the
      smallest published component (£0.093bn), so it cannot mask a
      dropped, renamed or misparented row.
    - Where a parent has suppressed ('*') components the sum CANNOT be
      exact, because '*' only tells us |x| < £0.1bn. Those parents are
      checked against the bound n_suppressed * £0.1bn instead. Two
      parents are in this position: 'Other DWP in welfare cap' (5 of
      its 10 components suppressed) and the outside-cap section total
      (1 suppressed component, which is negative in the early years).

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

# An 'of which:' marker declares the hierarchy: the row above it is the
# parent of the rows below it, one indent level deeper.
OF_WHICH_LABELS = {"of which:"}

# Column B carries the benefit label and its indentation level.
LABEL_COL = 1

PARENT_TOL = 1.0  # £1; see module docstring
SUPPRESSED_BOUND = 0.1e9  # '*' means |x| < £0.1bn


def col_index(ref):
    n = 0
    for ch in re.match(r"([A-Z]+)", ref).group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_sheet(path, sheet_name):
    """Return [(cells, indents)] per sheet row, both keyed by column index.

    `indents` carries each cell's style indentation level, which is how
    Table 4.9 encodes the depth of a benefit line under its 'of which:'
    marker. Without it the nesting is invisible.
    """
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
    styles = ET.fromstring(z.read("xl/styles.xml"))
    xf_indent = []
    for xf in styles.find("m:cellXfs", NSM).findall("m:xf", NSM):
        alignment = xf.find("m:alignment", NSM)
        xf_indent.append(
            int(alignment.get("indent", "0")) if alignment is not None else 0
        )
    target = targets[sheet_name]
    if not target.startswith("xl/"):
        target = "xl/" + target
    rows = []
    for row in ET.fromstring(z.read(target)).findall(".//m:row", NSM):
        cells, indents = {}, {}
        for c in row.findall("m:c", NSM):
            v = c.find("m:v", NSM)
            val = v.text if v is not None else None
            if c.get("t") == "s" and val is not None:
                val = strings[int(val)]
            i = col_index(c.get("r"))
            cells[i] = val
            s = int(c.get("s", "0"))
            indents[i] = xf_indent[s] if s < len(xf_indent) else 0
        rows.append((cells, indents))
    return rows


def run():
    rows_out = []
    sheet = read_sheet(HERE / "raw" / RAW_FILE, SHEET)

    year_row = next(
        cells
        for cells, _ in sheet
        if any(re.match(r"^\d{4}-\d{2}$", str(v)) for v in cells.values())
    )
    periods = {i: v for i, v in year_row.items() if re.match(r"^\d{4}-\d{2}$", str(v))}

    variant = None
    # indent level -> (program, variant) of the aggregate that governs it,
    # as declared by the most recent 'of which:' marker one level up.
    parent_at_indent = {}
    # indent level -> key of the last data row seen at that level, i.e. the
    # candidate parent when an 'of which:' marker follows it.
    last_at_indent = {}
    # keys of rows an 'of which:' marker has revealed to be aggregates.
    subtotal_keys = set()
    by_key = {}  # (program, variant) -> emitted row dicts, for later upgrade
    ignored_prose = []
    unlabelled = 0

    def is_value(v):
        """A £bn figure or a '*' suppression marker, not header prose."""
        if v is None:
            return False
        if v == "*":
            return True
        try:
            float(v)
            return True
        except (TypeError, ValueError):
            return False

    for cells, indents in sheet:
        label = cells.get(LABEL_COL)
        has_data = any(is_value(cells.get(i)) for i in periods)
        if not isinstance(label, str) or not label.strip():
            # header band / blank spacer rows; they must not carry benefit data
            if has_data:
                raise ValueError(f"4.9: unlabelled row carries data: {cells!r}")
            unlabelled += 1
            continue
        label = label.strip()
        indent = indents.get(LABEL_COL, 0)

        if label in SECTION_STARTS:
            variant = SECTION_STARTS[label]
            parent_at_indent.clear()
            last_at_indent.clear()
            continue

        if label in OF_WHICH_LABELS:
            if has_data:
                raise ValueError(f"4.9: 'of which:' marker carries data: {label!r}")
            parent_key = last_at_indent.get(indent)
            if parent_key is None:
                raise ValueError(
                    f"4.9: 'of which:' at indent {indent} has no preceding row at "
                    "that indent to act as parent"
                )
            parent_at_indent[indent + 1] = parent_key
            subtotal_keys.add(parent_key)
            for r in by_key[parent_key]:
                r["aggregate_level"] = "subtotal"
            continue

        base = re.sub(r"\d+$", "", label)  # trailing footnote marker
        if label in TOTALS:
            program, row_variant = TOTALS[label]
            level, parent = "total", None
        elif base in PROGRAMS:
            if variant is None:
                raise ValueError(f"4.9: benefit row before a section: {label!r}")
            program, row_variant = PROGRAMS[base], variant
            level = "component"  # upgraded to 'subtotal' by a following marker
            # a deeper context ended when the indent stepped back out
            for lvl in [x for x in parent_at_indent if x > indent]:
                del parent_at_indent[lvl]
            for lvl in [x for x in last_at_indent if x > indent]:
                del last_at_indent[lvl]
            if indent == 0:
                parent = "total_welfare"  # rolls straight into the section total
            else:
                governing = parent_at_indent.get(indent)
                if governing is None:
                    raise ValueError(
                        f"4.9: {label!r} sits at indent {indent} but no 'of which:' "
                        "marker established a parent for that level; refusing to "
                        "guess the hierarchy"
                    )
                parent = governing[0]
            last_at_indent[indent] = (program, row_variant)
        else:
            # Never vanish silently: prose is tallied, anything with data raises.
            if has_data:
                raise ValueError(
                    f"4.9: unmapped row label carrying data: {label!r} — add it to "
                    "PROGRAMS/TOTALS or the table has changed shape"
                )
            ignored_prose.append(label)
            continue

        key = (program, row_variant)
        if key in subtotal_keys:
            level = "subtotal"
        emitted = []
        for i, period in periods.items():
            raw = cells.get(i)
            if raw is None:
                raise ValueError(f"4.9 {label!r} {period}: missing cell")
            if raw == "*":
                value, status = None, "suppressed"
            else:
                value, status = float(raw) * 1e9, "ok"
            row = {
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
                "aggregate_level": level,
                "parent": parent,
                "source_column": f"4.9:{label}",
            }
            rows_out.append(row)
            emitted.append(row)
        if key in by_key:
            raise ValueError(f"4.9: duplicate (program, variant) key {key!r}")
        by_key[key] = emitted

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

    # --- the check the published-totals identity was blind to ---
    # cap + outside = total holds even if a component is dropped or
    # renamed, because all three are published figures. Reconciling each
    # aggregate against its own components is not: it fails the moment a
    # row goes missing, changes parent, or is double-counted.
    all_periods = sorted({r["period"] for r in rows_out})

    def reconcile(name, children, parent_row):
        """Children must sum to their published parent, every year."""
        nonlocal failed
        known = [c for c in children if c["status"] != "suppressed"]
        n_sup = len(children) - len(known)
        got = sum(c["value"] for c in known)
        want = parent_row["value"]
        if want is None:
            raise ValueError(f"4.9: {name}: parent value is suppressed")
        # '*' only bounds a component at |x| < £0.1bn, so a parent with
        # suppressed children can only ever be bounded, never matched.
        tol = PARENT_TOL if n_sup == 0 else n_sup * SUPPRESSED_BOUND
        ok = want is not None and abs(got - want) < tol
        kind = "exact" if n_sup == 0 else f"bounded<{n_sup}x£0.1bn"
        print(
            f"  {'OK ' if ok else 'FAIL'} {name}: "
            f"{len(children)} children sum {got:,.0f} vs published {want:,.0f} "
            f"(resid {got - want:+,.2f}, {kind})"
        )
        failed = failed or not ok

    # every aggregate reconciles against the rows that name it as parent
    aggregates = [r for r in rows_out if r["aggregate_level"] in ("subtotal", "total")]
    if not aggregates:
        raise ValueError("4.9: no aggregate rows found — hierarchy not detected")
    for agg in aggregates:
        if agg["parent"] is None and agg["variant"] is None:
            continue  # grand total: covered by the cap+outside identity
        children = [
            r
            for r in rows_out
            if r["parent"] == agg["program"]
            and r["variant"] == agg["variant"]
            and r["period"] == agg["period"]
        ]
        if not children:
            raise ValueError(
                f"4.9: aggregate {agg['program']}/{agg['variant']}/{agg['period']} "
                "has no components — hierarchy is broken"
            )
        reconcile(f"{agg['program']}[{agg['variant']}] {agg['period']}", children, agg)

    # every component names a parent that actually exists, same variant/period
    for r in rows_out:
        if r["parent"] is None:
            if r["aggregate_level"] != "total":
                raise ValueError(f"4.9: non-total row without a parent: {r!r}")
            continue
        if not any(
            o["program"] == r["parent"]
            and o["variant"] == r["variant"]
            and o["period"] == r["period"]
            and o["aggregate_level"] in ("subtotal", "total")
            for o in rows_out
        ):
            raise ValueError(
                f"4.9: {r['program']}/{r['variant']}/{r['period']} names parent "
                f"{r['parent']!r}, which is not an aggregate in that section"
            )

    # leaves-only flat sum == published section total. THIS is the
    # assertion that would have caught the flat emission: summing every
    # non-total row gave £319.85bn against a £169.13bn cap total.
    for variant in ("in_welfare_cap", "outside_welfare_cap"):
        for period in all_periods:
            leaves = [
                r
                for r in rows_out
                if r["variant"] == variant
                and r["period"] == period
                and r["aggregate_level"] == "component"
            ]
            total_row = next(
                r
                for r in rows_out
                if r["program"] == "total_welfare"
                and r["variant"] == variant
                and r["period"] == period
            )
            reconcile(f"leaves-only {variant} {period}", leaves, total_row)

    levels = {}
    for r in rows_out:
        levels[r["aggregate_level"]] = levels.get(r["aggregate_level"], 0) + 1
    print(f"  aggregate_level tally: {levels}")
    print(f"  non-data prose rows ignored: {len(ignored_prose)} {ignored_prose}")
    print(f"  unlabelled/structural rows: {unlabelled}")
    print(f"  suppressed cells: {sum(r['status'] == 'suppressed' for r in rows_out)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
