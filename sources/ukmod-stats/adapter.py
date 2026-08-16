"""Adapter: UKMOD Country Report published statistics -> tidy rows.

Input:  raw/cempa8-26_ukmod_country_report_2023-2030.pdf — the UKMOD
        Country Report 2023-2030 (CeMPA WP 8/26, March 2026, UKMOD
        version B2026.01), as fetched from iser.essex.ac.uk.
Output: data/externals/ukmod-stats.json — tidy rows in the scorecard
        schema.

UKMOD is the peer FRS-based UK microsimulation model (EUROMOD platform),
so these are the highest-signal model-vs-model claims the UK side has.
This build emits the report's validation-statistics tables:

    - Table 4.5: simulated caseloads by instrument (thousands), policy
      years 2023-2030, alongside the official estimates the report cites
    - Table 4.6: simulated expenditure by instrument (£ millions), same
      layout
    - Table 4.7: household equivalised disposable income distribution
      (Gini, mean/median, quintile medians and shares), UKMOD years plus
      the un-simulated input data and HBAI reference columns for 2023
    - Table 4.8: poverty rates below 50/60/70% of median (BHC) by age
      group and gender, same three sources

The source variant is carried per row: 'ukmod' (simulated),
'official_as_cited' (the report's own transcription of DWP/HMRC/OBR/SFC
official estimates — provenance is this report, not the primary source),
'input_data' (statistics computed on the raw input data), and 'hbai'
(DWP HBAI as cited). Missing cells ('-', 'na') are absent claims and are
skipped, not suppressed.

Parsing: pypdf text extraction with an ordered row registry anchored on
UKMOD variable names (bsauc_s, tin00_s, ...) and band labels. Anchors
match WHOLE TOKENS, never substrings, and a numeric anchor must sit at
the start of its line — the first build matched substrings of flattened
text, so Table 4.7's bare '2' anchor matched the trailing digit of
'1352' and shifted five quintile rows onto their neighbours' values.
Values come from the anchor's own line, continuing onto later lines only
while those hold nothing but values (Table 4.6 wraps two rows). Any
anchor miss or token shortfall fails the run, and structural_invariants()
checks the table identities that spot-checks cannot see.

pypdf is imported lazily (see _pdf_reader) so the parsing helpers and the
invariants stay importable — and CI-testable — without it; everything
else is stdlib.

Value semantics:
    - caseloads are THOUSANDS -> raw units (families unless noted:
      (c) children, (h) households, (i) individuals — carried as
      unit_concept per row)
    - expenditure is £ MILLIONS -> raw GBP
    - Gini, quintile shares and poverty rates are percents -> fractions
    - mean/median/quintile incomes are £ per month, as printed
"""

import json
import re
from pathlib import Path


def _pdf_reader():
    """Imported lazily so the parsing helpers and structural_invariants()
    stay importable (and CI-testable) without pypdf installed."""
    try:
        from pypdf import PdfReader
    except ImportError as e:  # pragma: no cover - environment-dependent
        raise SystemExit("this adapter needs pypdf: pip install pypdf") from e
    return PdfReader


HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "ukmod-stats"
RAW_FILE = "cempa8-26_ukmod_country_report_2023-2030.pdf"
YEARS = [str(y) for y in range(2023, 2031)]

# (anchor, program, subgroup, unit_concept, band_row)
# anchor is the UKMOD variable-name string printed in the table row; band
# rows (marginal-rate breakdowns) are anchored on their label and carry a
# leading '-' variable placeholder before the value tokens.
INSTRUMENT_ROWS = [
    (
        "bmascmt01_s, \nbmascmt_s",
        "best_start_grant_and_foods",
        "total",
        "families",
        False,
    ),
    ("bchkid_s", "child_benefit", "children_covered", "children", False),
    ("bch_s", "child_benefit", "total", "families", False),
    ("bfamt_s, \nbwkmt_s", "child_and_working_tax_credits", "total", "families", False),
    ("bmu_s", "council_tax_reduction", "total", "households", False),
    ("bsadi_s", "esa_income_based", "total", "families", False),
    ("bched01_s", "free_school_meals", "total", "families", False),
    ("bmamt01_s", "healthy_start_food", "total", "families", False),
    ("bho_s", "housing_benefit", "total", "households", False),
    ("bsa_s", "income_support", "total", "families", False),
    ("bunct_s", "jsa_contribution_based", "total", "families", False),
    ("boamt_s", "pension_credit", "total", "families", False),
    ("bched02_s", "school_clothing_grant", "total", "families", False),
    (
        "bcrdicm_s",
        "scottish_carers_allowance_supplement",
        "total",
        "individuals",
        False,
    ),
    ("bchmt_s", "scottish_child_payment", "total", "children", False),
    ("bchht_s", "scottish_child_winter_heating", "total", "children", False),
    ("bmamt_s", "sure_start_maternity_grant", "total", "families", False),
    ("bsauc_s", "universal_credit", "total", "families", False),
    ("boaht_s", "winter_fuel_allowance", "total", "households", False),
    ("brd_s", "benefit_cap_housing_benefit", "total", "households", False),
    ("brduc_s", "benefit_cap_universal_credit", "total", "households", False),
    ("tscee_s", "nic_employees", "total", "individuals", False),
    ("tscse_s", "nic_self_employed", "total", "individuals", False),
    ("tscer_s", "nic_employers", "total", "individuals", False),
    ("tin_s", "income_tax", "total", "individuals", False),
    ("tin00_s", "income_tax_non_devolved", "total", "individuals", False),
    ("Savers rate", "income_tax_non_devolved", "savers_rate", "individuals", True),
    ("Basic rate", "income_tax_non_devolved", "basic_rate", "individuals", True),
    ("Higher rate", "income_tax_non_devolved", "higher_rate", "individuals", True),
    (
        "Additional rate",
        "income_tax_non_devolved",
        "additional_rate",
        "individuals",
        True,
    ),
    ("tin11_s", "income_tax_welsh", "total", "individuals", False),
    ("tin12_s", "income_tax_scottish", "total", "individuals", False),
    ("Starter rate", "income_tax_scottish", "starter_rate", "individuals", True),
    ("Basic rate", "income_tax_scottish", "basic_rate", "individuals", True),
    (
        "Intermediate rate",
        "income_tax_scottish",
        "intermediate_rate",
        "individuals",
        True,
    ),
    ("Higher rate", "income_tax_scottish", "higher_rate", "individuals", True),
    ("Advanced rate", "income_tax_scottish", "advanced_rate", "individuals", True),
    ("Top rate", "income_tax_scottish", "top_rate", "individuals", True),
]

# Table 4.6 adds the NIC total row (between brduc_s and tscee_s) and has a
# single Child Benefit row (no children-covered caseload analogue).
EXPENDITURE_ROWS = (
    [r for r in INSTRUMENT_ROWS[:21] if r[0] != "bchkid_s"]
    + [("NIC all", "nic_all", "total", "individuals", True)]
    + INSTRUMENT_ROWS[21:]
)

TOKEN = re.compile(r"^(-|na|-?\d+(?:\.\d+)?)$")


def page_text(reader, indices):
    return "\n".join(reader.pages[i].extract_text() or "" for i in indices)


def tokenize(text):
    """[(token, line_index, is_line_start)] over the extracted page text.

    Tokens, not characters, are the matching unit. Substring matching on
    flattened text is what made a bare '2' anchor match the trailing digit
    of '1352' in Table 4.7, shifting five quintile rows onto their
    neighbours' values; whole-token equality cannot do that.
    """
    out = []
    for line_no, line in enumerate(text.split("\n")):
        for i, tok in enumerate(line.split()):
            out.append((tok, line_no, i == 0))
    return out


def _match_anchor(stream, start, anchor_tokens, numeric_anchor):
    """First index >= start where anchor_tokens match consecutively."""
    n = len(anchor_tokens)
    for i in range(start, len(stream) - n + 1):
        if [t for t, _, _ in stream[i : i + n]] != anchor_tokens:
            continue
        # A numeric label ('2', '3', '4' — the quintile rows) is only a row
        # label at the start of its line; anywhere else it is a data value.
        if numeric_anchor and not stream[i][2]:
            continue
        return i
    return -1


def parse_rows(text, registry, n_values):
    """Walk the registry in order, reading n_values values after each anchor.

    A row's values are taken from the anchor's OWN line, and continue onto
    following lines only while the anchor line has not yet supplied enough
    (Table 4.6 wraps the two benefit-cap rows) and each continuation line
    holds nothing but values. That bound is what stops a row from running
    on into the next labelled row.
    """
    lines = text.split("\n")
    pure_value_line = [
        bool(line.split()) and all(TOKEN.match(t) for t in line.split())
        for line in lines
    ]
    stream = tokenize(text)
    cursor = 0
    out = []
    for anchor, program, subgroup, unit_concept, band in registry:
        anchor_tokens = anchor.split()
        numeric_anchor = all(TOKEN.match(t) for t in anchor_tokens)
        i = _match_anchor(stream, cursor, anchor_tokens, numeric_anchor)
        if i < 0:
            raise ValueError(f"anchor not found: {anchor!r}")
        start = i + len(anchor_tokens)
        # values start on the LAST anchor token's line: wrapped anchors
        # ("bmascmt01_s,\nbmascmt_s") put the label and the data on
        # different lines
        anchor_line = stream[start - 1][1]
        want = n_values + 1 if band else n_values
        tokens = []
        for tok, line_no, _ in stream[start:]:
            if len(tokens) >= want:
                break
            if line_no != anchor_line and not pure_value_line[line_no]:
                break
            if not TOKEN.match(tok):
                break
            tokens.append(tok)
        if band and len(tokens) == n_values + 1:
            tokens = tokens[1:]  # leading variable-column placeholder
        if len(tokens) < n_values:
            raise ValueError(
                f"{anchor!r}: expected {n_values} tokens, got {len(tokens)}: {tokens}"
            )
        out.append((program, subgroup, unit_concept, tokens[:n_values]))
        cursor = start
    return out


def emit(
    rows, program, metric, subgroup, variant, unit_concept, period, value, source_column
):
    rows.append(
        {
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
            "status": "ok",
            "source_column": source_column,
        }
    )


def emit_instrument_table(text, registry, metric, scale, rows, table_id):
    absent = 0
    for program, subgroup, unit_concept, tokens in parse_rows(text, registry, 16):
        for k, tok in enumerate(tokens):
            if tok in ("-", "na"):
                absent += 1  # claim not published, not a suppressed value
                continue
            variant = "ukmod" if k < 8 else "official_as_cited"
            period = YEARS[k % 8]
            emit(
                rows,
                program,
                metric,
                subgroup,
                variant,
                # the caseload registry supplies the counting unit; money
                # rows are GBP whatever their instrument counts
                "gbp_nominal" if metric == "expenditure" else unit_concept,
                period,
                float(tok) * scale,
                f"{table_id}:{program}/{subgroup}",
            )
    return absent


DISTRIBUTION_ROWS = [
    ("Gini", "gini", "total", 0.01, "fraction"),
    ("Mean (£ per month)", "mean_income", "total", 1, "gbp_per_month_equivalised"),
    ("Median (£ per month)", "median_income", "total", 1, "gbp_per_month_equivalised"),
    ("lowest", "quintile_median_income", "q1", 1, "gbp_per_month_equivalised"),
    ("2", "quintile_median_income", "q2", 1, "gbp_per_month_equivalised"),
    ("3", "quintile_median_income", "q3", 1, "gbp_per_month_equivalised"),
    ("4", "quintile_median_income", "q4", 1, "gbp_per_month_equivalised"),
    ("highest", "quintile_median_income", "q5", 1, "gbp_per_month_equivalised"),
    ("lowest", "quintile_income_share", "q1", 0.01, "fraction"),
    ("2", "quintile_income_share", "q2", 0.01, "fraction"),
    ("3", "quintile_income_share", "q3", 0.01, "fraction"),
    ("4", "quintile_income_share", "q4", 0.01, "fraction"),
    ("highest", "quintile_income_share", "q5", 0.01, "fraction"),
]

POVERTY_ROWS = [
    (anchor, metric, subgroup, 0.01, "fraction")
    for anchor, metric, subgroup in [
        ("below 50% of median", "poverty_rate_below_50pct_median", "total"),
        ("below 60% of median", "poverty_rate_below_60pct_median", "total"),
        ("below 70% of median", "poverty_rate_below_70pct_median", "total"),
        ("below 50% of median", "poverty_rate_below_50pct_median", "children"),
        ("below 60% of median", "poverty_rate_below_60pct_median", "children"),
        ("below 70% of median", "poverty_rate_below_70pct_median", "children"),
        ("below 50% of median", "poverty_rate_below_50pct_median", "over_spa"),
        ("below 60% of median", "poverty_rate_below_60pct_median", "over_spa"),
        ("below 70% of median", "poverty_rate_below_70pct_median", "over_spa"),
        ("men", "poverty_rate_below_60pct_median", "men"),
        ("women", "poverty_rate_below_60pct_median", "women"),
    ]
]


def emit_reference_table(text, registry, program, rows, table_id):
    """Tables 4.7/4.8: 8 UKMOD years + input-data 2023 + HBAI 2023."""
    reg = [
        (anchor, metric, subgroup, scale, unit)
        for anchor, metric, subgroup, scale, unit in registry
    ]
    parsed = parse_rows(
        text,
        [(a, m, s, u, False) for a, m, s, _, u in reg],
        10,
    )
    for (anchor, metric, subgroup, scale, unit), (_, _, _, tokens) in zip(reg, parsed):
        for k, tok in enumerate(tokens):
            if tok in ("-", "na"):
                continue
            if k < 8:
                variant, period = "ukmod", YEARS[k]
            elif k == 8:
                variant, period = "input_data", "2023"
            else:
                variant, period = "hbai", "2023"
            emit(
                rows,
                program,
                metric,
                subgroup,
                variant,
                unit,
                period,
                float(tok) * scale,
                f"{table_id}:{metric}/{subgroup}",
            )


QUINTILES = ("q1", "q2", "q3", "q4", "q5")


def structural_invariants(rows):
    """[(label, ok)] — table-level identities the source guarantees.

    Shared with tests/test_ukmod_adapter.py so CI enforces them too (CI
    runs pytest, never sources/).
    """
    index = {}
    for r in rows:
        index[(r["metric"], r["subgroup"], r["variant"], r["period"])] = r["value"]
    variants = ("ukmod", "input_data", "hbai")
    out = []

    for variant in variants:
        periods = sorted(
            {
                p
                for (m, _, v, p) in index
                if m == "quintile_income_share" and v == variant
            }
        )
        for period in periods:
            shares = [
                index[("quintile_income_share", q, variant, period)] for q in QUINTILES
            ]
            # published as whole percents; five roundings bound the error
            out.append(
                (
                    f"{variant} {period} quintile shares sum to 1",
                    abs(sum(shares) - 1.0) <= 0.025,
                )
            )
            medians = [
                index[("quintile_median_income", q, variant, period)] for q in QUINTILES
            ]
            out.append(
                (
                    f"{variant} {period} quintile medians increase q1<..<q5",
                    all(a < b for a, b in zip(medians, medians[1:])),
                )
            )
            # the middle quintile's median IS the population median
            out.append(
                (
                    f"{variant} {period} q3 median == overall median",
                    abs(medians[2] - index[("median_income", "total", variant, period)])
                    <= 1,  # the report rounds the two rows independently
                )
            )
            out.append(
                (
                    f"{variant} {period} median <= mean (right-skewed incomes)",
                    index[("median_income", "total", variant, period)]
                    <= index[("mean_income", "total", variant, period)],
                )
            )
    return out


def run():
    reader = _pdf_reader()(HERE / "raw" / RAW_FILE)
    rows = []

    text = page_text(reader, range(89, 92))
    text = text[text.find("Table 4.5") :]
    absent = emit_instrument_table(text, INSTRUMENT_ROWS, "caseload", 1000, rows, "4.5")

    text = page_text(reader, range(92, 95))
    text = text[text.find("Table 4.6") :]
    absent += emit_instrument_table(
        text, EXPENDITURE_ROWS, "expenditure", 1e6, rows, "4.6"
    )

    text = page_text(reader, [98])
    text = text[text.find("Table 4.7") :]
    emit_reference_table(text, DISTRIBUTION_ROWS, "income_distribution", rows, "4.7")

    text = page_text(reader, [100])
    text = text[text.find("Full population") :]
    emit_reference_table(text, POVERTY_ROWS, "poverty", rows, "4.8")

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows))
    print(f"{len(rows)} rows -> {out}")

    # --- validation against the report's printed values ---
    def get(program, metric, period, variant, subgroup="total"):
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
            "UC caseload 2025 (UKMOD) 6.941M",
            get("universal_credit", "caseload", "2025", "ukmod"),
            6_941_000,
        ),
        (
            "UC caseload 2025 (official) 6.493M",
            get("universal_credit", "caseload", "2025", "official_as_cited"),
            6_493_000,
        ),
        (
            "UC expenditure 2025 (official) £79,525m",
            get("universal_credit", "expenditure", "2025", "official_as_cited"),
            79_525_000_000,
        ),
        (
            "child benefit children 2024 (UKMOD) 12.863M",
            get(
                "child_benefit",
                "caseload",
                "2024",
                "ukmod",
                subgroup="children_covered",
            ),
            12_863_000,
        ),
        (
            "Scottish advanced-rate payers 2026 (UKMOD) 144k",
            get(
                "income_tax_scottish",
                "caseload",
                "2026",
                "ukmod",
                subgroup="advanced_rate",
            ),
            144_000,
        ),
        (
            "income tax expenditure 2023 (official) £297,480m",
            get("income_tax", "expenditure", "2023", "official_as_cited"),
            297_480_000_000,
        ),
        (
            "Gini 2023 (UKMOD) 0.32",
            get("income_distribution", "gini", "2023", "ukmod"),
            0.32,
        ),
        (
            "Gini 2023 (HBAI) 0.33",
            get("income_distribution", "gini", "2023", "hbai"),
            0.33,
        ),
        (
            "median income 2023 (input data) £2,818/mo",
            get("income_distribution", "median_income", "2023", "input_data"),
            2818,
        ),
        (
            "child poverty <60% 2025 (UKMOD) 19%",
            get(
                "poverty",
                "poverty_rate_below_60pct_median",
                "2025",
                "ukmod",
                subgroup="children",
            ),
            0.19,
        ),
        (
            "child poverty <60% 2023 (HBAI) 20%",
            get(
                "poverty",
                "poverty_rate_below_60pct_median",
                "2023",
                "hbai",
                subgroup="children",
            ),
            0.20,
        ),
        (
            "women poverty <60% 2023 (UKMOD) 15%",
            get(
                "poverty",
                "poverty_rate_below_60pct_median",
                "2023",
                "ukmod",
                subgroup="women",
            ),
            0.15,
        ),
    ]
    failed = False
    for label, got, want in checks:
        ok = got is not None and abs(got - want) < 1e-9
        print(f"  {'OK ' if ok else 'FAIL'} {label}: {got}")
        failed = failed or not ok

    # --- structural invariants -----------------------------------------
    # Spot-checks on hand-picked cells cannot see a whole row shifted onto
    # its neighbour's values: the first build of this adapter passed all 12
    # checks above while five quintile rows of Table 4.7 were wrong. These
    # invariants are what catch that class of defect.
    for label, ok in structural_invariants(rows):
        print(f"  {'OK ' if ok else 'FAIL'} invariant: {label}")
        failed = failed or not ok
    print(f"  absent (unpublished) cells skipped: {absent}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
