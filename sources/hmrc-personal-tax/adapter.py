"""Adapter: HMRC personal tax statistics -> tidy rows.

Input:  raw/income_tax_liabilities_tables_2_1_to_2_6.ods
        (Income Tax liabilities statistics 2023-24 to 2026-27, published
        2026-07-15; SPI-based, projected years on OBR assumptions)
        raw/june_2025_tax_ready_reckoner.ods
        (Direct effects of illustrative tax changes, June 2025 edition —
        still current: the scheduled July 2026 update was deferred by HMRC)
Output: data/externals/hmrc-personal-tax.json — tidy rows in the scorecard
        schema.

Coverage in this build:
    - Table 2.1: Income Tax payer counts by marginal rate / sex / age,
      1990-91 to 2026-27 (levels; program income_tax)
    - Table 2.5 (four year-sheets): payer counts and liabilities by income
      range x marginal-rate band, plus totals and averages
    - the full ready reckoner: revenue effects of illustrative changes
      (program per tax head; these are REFORM DELTAS against HMRC's
      indexed baseline as of Spring Statement 2025, April 2026 start —
      period rows carry that baseline, see annotations)
    Tables 2.2 (region x demographic), 2.4 (shares) and 2.6 (income
    source) are in the same raw file but not yet emitted.

Value semantics:
    - counts are THOUSANDS -> raw individuals
    - liabilities/incomes are £ MILLIONS -> raw GBP; averages are raw £
    - 'Average rate of Income Tax' is percent -> fraction
    - ready-reckoner effects are £ MILLIONS -> raw GBP
    - '[not applicable]' cells (band did not exist that year) are skipped
      entirely; '[not available]' / '[no estimate]' / 'Neg' (>0 but rounds
      to 0) -> status 'suppressed'
    - subgroups for ready-reckoner rows are the verbatim change
      descriptions (they are the claim identity, including (cost)/(yield)
      asymmetry)

Sign convention on ready-reckoner rows (see classify_reckoner_label):
    HMRC publishes these as magnitudes with the direction carried in the
    English label, so a cost row and a yield row can BOTH be positive
    ('Increase additional rate by 1p (yield)' +£145m and 'Decrease
    additional rate by 1p (cost)' +£175m in 2026-27). They are NOT
    (reform - baseline) deltas, and negatives that do appear are HMRC's own
    published signs, not a normalisation. Every revenue_effect row therefore
    carries sign_convention / direction / change_direction so a downstream
    comparison can orient the sign without parsing English.
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "hmrc-personal-tax"

TNS = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS = {"table": TNS, "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}

LIABILITIES_FILE = "income_tax_liabilities_tables_2_1_to_2_6.ods"
RECKONER_FILE = "june_2025_tax_ready_reckoner.ods"

SKIPPED = {"[not applicable]"}
SUPPRESSED = {"[not available]", "[no estimate]", "Neg"}

T21_SUBGROUPS = {
    "All Income Tax payers": "total",
    "Lower or starting rate": "lower_or_starting_rate",
    "Savers rate": "savers_rate",
    "Basic rate": "basic_rate",
    "Higher rate": "higher_rate",
    "Additional rate": "additional_rate",
    "Males": "male",
    "Females": "female",
    "Age under 65": "age_under_65",
    "Age 65 and over": "age_65_plus",
    "State pension age": "state_pension_age",
}

T25_BANDS = {
    "savers rate": "savers_rate",
    "basic rate": "basic_rate",
    "higher rate": "higher_rate",
    "additional rate": "additional_rate",
}

RECKONER_PROGRAMS = {
    "Income Tax rates": "income_tax",
    "Income Tax allowances and reliefs": "income_tax",
    "Income Tax limits": "income_tax",
    "Income Tax allowances, starting and basic rate limits": "income_tax",
    "National Insurance contributions rates": "national_insurance",
    "National Insurance Contribution Limits": "national_insurance",
    "Child Benefit": "child_benefit",
    "Corporation tax": "corporation_tax",
    "Capital Gains Tax": "capital_gains_tax",
    "Inheritance tax": "inheritance_tax",
    "1% change in various duties": "duties",
    "Vehicle excise duty": "vehicle_excise_duty",
    "Air passenger duty": "air_passenger_duty",
    "VAT": "vat",
    "Insurance premium tax": "insurance_premium_tax",
    "Stamp duty land tax": "stamp_duty_land_tax",
}


SIGN_CONVENTION = "magnitude_with_direction_in_label"

# Change verbs HMRC uses to open a ready-reckoner row, mapped to the direction
# of the change itself as the label states it.
CHANGE_VERBS = {
    "Change": "unsigned",
    "Increase": "increase",
    "Raise": "increase",
    "Decrease": "decrease",
    "Cut": "decrease",
}

# Sections whose heading, not the row label, states the change. The rows under
# them are bare commodity names ('Petrol', 'Landfill tax', ...).
SECTIONS_STATING_THE_CHANGE = {"1% change in various duties"}

DIRECTION_MARKER = re.compile(r"\((cost|yield)\)$", re.IGNORECASE)
TRAILING_PAREN = re.compile(r"\([^()]*\)$")


def classify_reckoner_label(label, section):
    """Verbatim label text -> (direction, change_direction).

    direction is the fiscal direction HMRC's figure describes:
        'cost' / 'yield'  the label carries an explicit (cost)/(yield) marker,
                          so the positive magnitude is a revenue loss / gain
        'stated_change'   the label states no fiscal direction; the figure is
                          the effect of the change the label describes

    change_direction is the direction of the change itself, again read off the
    label's own verb: 'increase', 'decrease', or 'unsigned' where the label says
    only 'Change ...' (HMRC's figure applies in either direction) or names a
    duty whose change lives in the section heading.

    Both are derived ONLY from the label text. Nothing is inferred from the
    value's sign or from what the parameter does: an unmarked 'Increase ...' row
    is NOT assumed to be a yield, because HMRC publishes several of them
    negative ('Increase lower Capital Gains Tax rate by 10 percentage points' is
    -£130m in 2026-27, an increase that loses revenue). Unrecognised labels
    raise rather than defaulting to a direction.
    """
    marker = DIRECTION_MARKER.search(label)
    if marker:
        direction = marker.group(1).lower()
    else:
        stray = TRAILING_PAREN.search(label)
        if stray:
            raise ValueError(
                f"reckoner: unclassifiable direction marker {stray.group(0)!r} "
                f"in label {label!r}"
            )
        direction = "stated_change"

    head = label.split(" ", 1)[0]
    if head in CHANGE_VERBS:
        change_direction = CHANGE_VERBS[head]
    elif section in SECTIONS_STATING_THE_CHANGE:
        change_direction = "unsigned"
    else:
        raise ValueError(
            f"reckoner: cannot classify the change stated by label {label!r} "
            f"under section {section!r}"
        )
    return direction, change_direction


def strip_notes(text):
    return re.sub(r"\s*\[note \d+\]", "", text).strip()


def sheet_rows(path, want):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("content.xml"))
    for t in root.findall(".//table:table", NS):
        if t.get(f"{{{TNS}}}name") != want:
            continue
        rows = []
        for r in t.findall("table:table-row", NS):
            row = []
            for c in r.findall("table:table-cell", NS):
                rep = int(c.get(f"{{{TNS}}}number-columns-repeated", "1"))
                txt = " ".join(
                    "".join(p.itertext()) for p in c.findall("text:p", NS)
                ).strip()
                row.extend([txt] * min(rep, 30))
            while row and not row[-1]:
                row.pop()
            rows.append(row)
        return rows
    raise ValueError(f"{path}: sheet {want} not found")


def parse_number(text):
    if text in SKIPPED:
        return None, "skipped"
    if text in SUPPRESSED or text.lower() == "neg":
        return None, "suppressed"
    cleaned = text.replace(",", "").replace("£", "").replace("%", "")
    if not re.match(r"^-?\d+(\.\d+)?$", cleaned):
        return None, "unparsed"
    return float(cleaned), "ok"


def emit(
    rows,
    program,
    metric,
    subgroup,
    variant,
    unit_concept,
    period,
    value,
    status,
    source_column,
    extra=None,
):
    row = {
        "source": SOURCE_ID,
        "country": "UK",
        "program": program,
        "metric": metric,
        "subgroup": subgroup,
        "variant": variant,
        "geography": "UK",
        "unit_concept": unit_concept,
        "period": period,
        "value": value,
        "status": status,
        "source_column": source_column,
    }
    if extra:
        row.update(extra)
    rows.append(row)


def tax_year(label):
    """'2023 to 2024 [note 9]' -> '2023-24'."""
    m = re.match(r"^(\d{4}) to (\d{4})$", strip_notes(label))
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)[2:]}"


def parse_table_2_1(out):
    rows = sheet_rows(HERE / "raw" / LIABILITIES_FILE, "2_1_IT_payers_by_demographic")
    header = next(r for r in rows if r and r[0] == "Tax year")
    cols = []
    for i, label in enumerate(header[1:], 1):
        name = strip_notes(label)
        if name not in T21_SUBGROUPS:
            raise ValueError(f"2_1: unknown column {name!r}")
        cols.append((i, T21_SUBGROUPS[name]))
    for row in rows:
        period = tax_year(row[0]) if row else None
        if period is None:
            continue
        for i, subgroup in cols:
            value, status = parse_number(row[i] if i < len(row) else "")
            if status == "skipped":
                continue
            if status == "unparsed":
                raise ValueError(f"2_1 {period} col {i}: {row[i]!r}")
            emit(
                out,
                "income_tax",
                "taxpayer_count",
                subgroup,
                None,
                "individuals",
                period,
                None if value is None else value * 1000,
                "suppressed" if value is None else "ok",
                f"2_1:{subgroup}",
            )


def classify_2_5_column(label):
    """Header text -> (metric, band_subgroup, scale, unit_concept)."""
    name = strip_notes(label)
    m = re.match(r"^Number of (.+) Income Tax payers$", name)
    if m:
        return ("taxpayer_count", T25_BANDS[m.group(1)], 1000, "individuals")
    m = re.match(r"^Income Tax liability for (.+) Income Tax payers$", name)
    if m:
        return ("tax_liability", T25_BANDS[m.group(1)], 1e6, "gbp_nominal")
    fixed = {
        "Total number of Income Tax payers": (
            "taxpayer_count",
            "all_bands",
            1000,
            "individuals",
        ),
        "Total income": ("total_income", "all_bands", 1e6, "gbp_nominal"),
        "Total Income Tax liability": (
            "tax_liability",
            "all_bands",
            1e6,
            "gbp_nominal",
        ),
        "Average rate of Income Tax": (
            "average_tax_rate",
            "all_bands",
            0.01,
            "fraction_of_income",
        ),
        "Average amount of Income Tax in £": (
            "average_tax_amount",
            "all_bands",
            1,
            "gbp_nominal",
        ),
    }
    if name in fixed:
        return fixed[name]
    raise ValueError(f"2_5: unknown column {name!r}")


def range_slug(text):
    if text == "All Ranges":
        return "all_ranges"
    cleaned = text.replace("£", "").replace(",", "")
    if cleaned.endswith("+"):
        return f"lower_limit_{cleaned[:-1]}_plus"
    return f"lower_limit_{cleaned}"


def parse_table_2_5(out):
    for sheet_year in ("2023-24", "2024-25", "2025-26", "2026-27"):
        rows = sheet_rows(
            HERE / "raw" / LIABILITIES_FILE, f"2_5_IT_Liabilities_{sheet_year}"
        )
        header = next(r for r in rows if r and r[0].startswith("Range of total income"))
        cols = [
            (i, classify_2_5_column(label)) for i, label in enumerate(header[1:], 1)
        ]
        for row in rows:
            first = row[0] if row else ""
            if not (first.startswith("£") or first == "All Ranges"):
                continue
            variant = range_slug(first)
            for i, (metric, band, scale, unit_concept) in cols:
                value, status = parse_number(row[i] if i < len(row) else "")
                if status == "skipped":
                    continue
                if status == "unparsed":
                    raise ValueError(f"2_5 {sheet_year} {first} col {i}: {row[i]!r}")
                emit(
                    out,
                    "income_tax",
                    metric,
                    band,
                    variant,
                    unit_concept,
                    sheet_year,
                    None if value is None else value * scale,
                    "suppressed" if value is None else "ok",
                    f"2_5_{sheet_year}:{band}",
                )


def parse_reckoner(out):
    rows = sheet_rows(HERE / "raw" / RECKONER_FILE, "Publication_Format")
    header = next(r for r in rows if r and r[0] == "Column1")
    periods = []
    for i, label in enumerate(header[1:], 1):
        m = re.match(
            r"^Current Estimate, financial year (\d{4}) to (\d{4}), £ million$",
            label,
        )
        if not m:
            raise ValueError(f"reckoner: unexpected column {label!r}")
        periods.append((i, f"{m.group(1)}-{m.group(2)[2:]}"))
    program = None
    section = None
    for row in rows[3:]:
        if not row:
            continue
        first = row[0]
        if len(row) == 1:
            if first in RECKONER_PROGRAMS:
                program = RECKONER_PROGRAMS[first]
                section = first
            elif first.startswith(("For detailed methodology", "End of worksheet")):
                program = None
                section = None
            else:
                raise ValueError(f"reckoner: unknown section {first!r}")
            continue
        if program is None:
            raise ValueError(f"reckoner: data row outside a section: {first!r}")
        direction, change_direction = classify_reckoner_label(first, section)
        for i, period in periods:
            value, status = parse_number(row[i] if i < len(row) else "")
            if status in ("skipped", "unparsed"):
                raise ValueError(f"reckoner {first!r} {period}: {row[i]!r}")
            emit(
                out,
                program,
                "revenue_effect",
                first,
                None,
                "gbp_nominal",
                period,
                None if value is None else value * 1e6,
                "suppressed" if value is None else "ok",
                "reckoner",
                extra={
                    "sign_convention": SIGN_CONVENTION,
                    "direction": direction,
                    "change_direction": change_direction,
                },
            )


def run():
    rows = []
    parse_table_2_1(rows)
    parse_table_2_5(rows)
    parse_reckoner(rows)

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows))
    print(f"{len(rows)} rows -> {out}")

    # --- validation against HMRC's published summary statistics ---
    def get(metric, subgroup, period, program="income_tax", variant=None):
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
            "2023-24 taxpayers 36.7M",
            get("taxpayer_count", "total", "2023-24"),
            36_700_000,
        ),
        (
            "2026-27 taxpayers 40.8M",
            get("taxpayer_count", "total", "2026-27"),
            40_800_000,
        ),
        (
            "2026-27 basic rate 31.4M",
            get("taxpayer_count", "basic_rate", "2026-27"),
            31_400_000,
        ),
        (
            "2026-27 higher rate 7.70M",
            get("taxpayer_count", "higher_rate", "2026-27"),
            7_700_000,
        ),
        (
            "2026-27 additional rate 1.29M",
            get("taxpayer_count", "additional_rate", "2026-27"),
            1_290_000,
        ),
        (
            "2026-27 savers rate 415k",
            get("taxpayer_count", "savers_rate", "2026-27"),
            415_000,
        ),
        (
            "2023-24 total liability £274bn",
            get("tax_liability", "all_bands", "2023-24", variant="all_ranges"),
            274_000_000_000,
        ),
        # cross-table: 2.5 all-ranges band counts must equal 2.1 marginal-rate counts
        (
            "2.5 basic == 2.1 basic (2026-27)",
            get("taxpayer_count", "basic_rate", "2026-27", variant="all_ranges"),
            get("taxpayer_count", "basic_rate", "2026-27"),
        ),
        (
            "reckoner: basic rate 1p 2026-27 £6.9bn",
            get("revenue_effect", "Change basic rate by 1p", "2026-27"),
            6_900_000_000,
        ),
        (
            "reckoner: employer NICs 1pp 2026-27 £11.15bn",
            get(
                "revenue_effect",
                "Change Class 1 employer rate by 1 percentage point",
                "2026-27",
                program="national_insurance",
            ),
            11_150_000_000,
        ),
    ]
    failed = False
    for label, got, want in checks:
        ok = got is not None and want is not None and abs(got - want) < 1e-6
        print(f"  {'OK ' if ok else 'FAIL'} {label}: {got}")
        failed = failed or not ok
    print(f"  suppressed cells: {sum(r['status'] == 'suppressed' for r in rows)}")
    census = {}
    for r in rows:
        if r["metric"] == "revenue_effect":
            key = (r["direction"], r["change_direction"])
            census[key] = census.get(key, 0) + 1
    for key in sorted(census):
        print(f"  direction {key[0]} / {key[1]}: {census[key]}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
