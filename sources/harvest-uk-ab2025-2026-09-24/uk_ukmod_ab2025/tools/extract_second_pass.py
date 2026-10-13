"""Second-pass extraction of CeMPA WP 3/26 (Frimpong, Feb 2026) Tables 4/4.1, 5/5.1/5.2
and the §8 gainers/losers tables (6, 6.1, 6.2, 6.3) + the prose-only share_no_change.

Every value_raw is machine-checked against the pypdf text; every table-row quote too.
"""

import json
import re
import sys
from pathlib import Path

# Usage: uv run --with pypdf python extract_second_pass.py <cempa3-26.pdf> [out.jsonl]
# The PDF is the primary in ../manifest.jsonl (sha256 7c3f48bd…), fetched from
# its URL; the text is extracted here with pypdf, never read from a cached copy.
HERE = Path(__file__).parent
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "cempa3-26.pdf"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "second_pass_rows.jsonl"


def _pdf_text(path: Path) -> str:
    """pypdf text with a marker before each page, the layout the table
    parsers below were written against (printed page = PDF page - 2)."""
    from pypdf import PdfReader

    return "".join(
        f"\n\n===== PAGE {i} =====\n" + (page.extract_text() or "")
        for i, page in enumerate(PdfReader(str(path)).pages, start=1)
    )


TEXT = _pdf_text(PDF)

# Task convention: the paper's calendar label "2026" = UKMOD policy year UK_2026 = FY 2026-27,
# staged with period = FY END year.
YEAR = {
    "2026": {"period": 2027, "fy": "2026-27"},
    "2030": {"period": 2031, "fy": "2030-31"},
}

NATIONS = ["England", "Scotland", "Wales", "Northern Ireland"]

DECILE_NOTE = (
    "Paper (§1 'What this analysis compares'): 'The poverty line and decile groups are held fixed at "
    "baseline levels for each year.' 'All monetary values are expressed in nominal terms for each "
    "respective year.' Deciles are of the AHC disposable income distribution; the paper does not "
    "state whether deciles are of households or individuals, nor the equivalisation scale."
)
THRESH_NOTE = (
    "§8: 'This analysis identifies households experiencing income changes exceeding 1% or 5% thresholds "
    "after housing costs. Gainers see income increases while losers experience income decreases from the "
    "reform.' Executive Summary: 'gain more than 1% of equivalised disposable income'."
)

rows = []


def pct_to_share(s):
    return round(float(s.rstrip("%")) / 100.0, 6)


def gbp_to_num(s):
    return float(s.replace("£", "").replace(",", "").replace("+", ""))


def row(
    source_table,
    source_column,
    metric,
    unit,
    value,
    value_raw,
    normalization,
    period,
    conditions,
    quote,
    note,
    conf="high",
):
    rows.append(
        {
            "source_table": source_table,
            "source_column": source_column,
            "proposed_metric": metric,
            "proposed_unit": unit,
            "value": value,
            "value_raw": value_raw,
            "normalization": normalization,
            "value_kind": "point",
            "period": period,
            "conditions": conditions,
            "quote": quote,
            "note": note,
            "parse_confidence": conf,
        }
    )


def table_lines(start_pat, end_pat):
    m = re.search(start_pat, TEXT)
    assert m, start_pat
    tail = TEXT[m.start() :]
    e = re.search(end_pat, tail)
    return tail[: e.start()]


def join_nation_breaks(block):
    return block.replace("Northern \nIreland", "Northern Ireland")


# ---------------------------------------------------------------- Table 4 (PDF p.25 / printed p.23)
T4 = "Table 4: Income shares by decile (after housing costs, 2026 and 2030)"
blk = table_lines(
    r"Table 4: Income shares by decile", r"\nIncome shares remain unchanged"
)
pat = re.compile(r"^(Decile (\d+)) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)\s*$", re.M)
n4 = 0
for m in pat.finditer(blk):
    label, d, b26, r26, c26, b30, r30, c30 = m.groups()
    quote = m.group(0).strip()
    ig = f"decile_{d}"
    for yr, b, r, c in (("2026", b26, r26, c26), ("2030", b30, r30, c30)):
        Y = YEAR[yr]
        base_cond = {
            "fy": Y["fy"],
            "geography": "UK",
            "income_group": ig,
            "housing_costs": "ahc",
        }
        row(
            T4,
            f"{yr} Baseline",
            "income_share",
            "share",
            pct_to_share(b),
            b,
            "percent / 100 -> share",
            Y["period"],
            {**base_cond, "scenario": "baseline"},
            quote,
            DECILE_NOTE,
        )
        row(
            T4,
            f"{yr} Reform",
            "income_share",
            "share",
            pct_to_share(r),
            r,
            "percent / 100 -> share",
            Y["period"],
            {**base_cond, "scenario": "reform"},
            quote,
            DECILE_NOTE,
        )
        row(
            T4,
            f"{yr} Change",
            "income_share",
            "percentage_points",
            float(c.replace("pp", "")),
            c,
            "as printed, percentage points ('pp' suffix stripped); reform minus baseline income share",
            Y["period"],
            {**base_cond, "scenario": "reform_minus_baseline"},
            quote,
            DECILE_NOTE
            + " Change printed as 0.00pp for every decile; §6: 'all changes rounding to 0.00 percentage points'.",
        )
        n4 += 3
assert n4 == 60, n4

# ---------------------------------------------------------------- Table 4.1 (PDF p.26 / printed p.24)
T41 = "Table 4.1: Income shares by nation - Bottom and Top Deciles (2026 and 2030, AHC)"
blk = join_nation_breaks(
    table_lines(r"Table 4\.1: Income shares by nation", r"\nGeographic patterns:")
)
pat = re.compile(
    r"^(England|Scotland|Wales|Northern Ireland) (\S+%) (\S+%) (\S+%) (\S+%)\s*$", re.M
)
n41 = 0
NOTE41 = (
    "Table 4.1 does not label a scenario (no baseline/reform columns). §6.1 'Reform impacts': 'Income share "
    "changes remain negligible across all nations and deciles. In 2026, the largest change is Northern "
    "Ireland's Decile 4 (+0.012 percentage points), while most deciles show changes under 0.002 percentage "
    "points. By 2030, all nations show changes rounding to zero for most deciles.' Staged as baseline because "
    "baseline and reform coincide at the printed 2 d.p.; scenario is an inference, hence medium confidence. "
    "Deciles appear to be within-nation deciles of the nation's own AHC income distribution (the paper does "
    "not say). " + DECILE_NOTE
)
for m in pat.finditer(blk):
    nation, d1_26, d10_26, d1_30, d10_30 = m.groups()
    quote = m.group(0).strip()
    for yr, dec, v in (
        ("2026", "1", d1_26),
        ("2026", "10", d10_26),
        ("2030", "1", d1_30),
        ("2030", "10", d10_30),
    ):
        Y = YEAR[yr]
        row(
            T41,
            f"{yr} Decile {dec}",
            "income_share",
            "share",
            pct_to_share(v),
            v,
            "percent / 100 -> share",
            Y["period"],
            {
                "fy": Y["fy"],
                "geography": nation,
                "scenario": "baseline",
                "income_group": f"decile_{dec}",
                "housing_costs": "ahc",
            },
            quote,
            NOTE41,
            conf="medium",
        )
        n41 += 1
assert n41 == 16, n41

# ---------------------------------------------------------------- Table 5 (PDF p.27 / printed p.25)
T5 = "Table 5: Mean household income by decile ( After Housing Costs, 2026 and 2030)"
blk = table_lines(
    r"Table 5: Mean household income by decile", r"\nDistribution patterns:"
)
pat = re.compile(
    r"^(Decile \d+|All|Poor) (£[\d,]+) (£[\d,]+) ([+-]£[\d.]+) (£[\d,]+) (£[\d,]+) ([+-]£[\d.]+)\s*$",
    re.M,
)
NOTE5 = (
    DECILE_NOTE
    + " Levels are printed rounded to whole £/week (Executive Summary gives Decile 1 2026 as "
    "£158.75 -> £159.19), so reform minus baseline of the printed levels does not reproduce the printed Change "
    "column; the Change column is printed to the penny and is the paper's own figure. Mean is per household "
    "('Mean household income shows average weekly income across the distribution', §7)."
)
n5 = 0
for m in pat.finditer(blk):
    label, b26, r26, c26, b30, r30, c30 = m.groups()
    quote = m.group(0).strip()
    if label.startswith("Decile"):
        ig = "decile_" + label.split()[1]
        extra = ""
    elif label == "All":
        ig = "all"
        extra = ""
    else:
        ig = "poor"
        extra = (
            " Row label 'Poor' is the paper's own group (not in the decile_1..decile_10/all set); the paper "
            "does not define it in §7 — its poverty analysis (§4) uses a fixed-line AHC poverty threshold "
            "('poverty line ... held fixed at baseline levels for each year'), so read as households below "
            "the AHC poverty line."
        )
    for yr, b, r, c in (("2026", b26, r26, c26), ("2030", b30, r30, c30)):
        Y = YEAR[yr]
        base_cond = {
            "fy": Y["fy"],
            "geography": "UK",
            "income_group": ig,
            "housing_costs": "ahc",
            "statistic": "mean_weekly_income",
        }
        row(
            T5,
            f"{yr} Baseline (£/week)",
            "income_statistic",
            "gbp_per_week",
            gbp_to_num(b),
            b,
            "as printed, GBP per week ('£' and thousands separator stripped)",
            Y["period"],
            {**base_cond, "scenario": "baseline"},
            quote,
            NOTE5 + extra,
            conf="high" if ig != "poor" else "medium",
        )
        row(
            T5,
            f"{yr} Reform (£/week)",
            "income_statistic",
            "gbp_per_week",
            gbp_to_num(r),
            r,
            "as printed, GBP per week ('£' and thousands separator stripped)",
            Y["period"],
            {**base_cond, "scenario": "reform"},
            quote,
            NOTE5 + extra,
            conf="high" if ig != "poor" else "medium",
        )
        row(
            T5,
            f"{yr} Change",
            "average_household_income_change",
            "gbp_per_week",
            gbp_to_num(c),
            c,
            "as printed, GBP per week (sign kept, '£' stripped); reform minus baseline mean weekly AHC income",
            Y["period"],
            {
                "fy": Y["fy"],
                "geography": "UK",
                "income_group": ig,
                "housing_costs": "ahc",
                "scenario": "reform_minus_baseline",
            },
            quote,
            NOTE5 + extra,
            conf="high" if ig != "poor" else "medium",
        )
        n5 += 3
assert n5 == 72, n5

# ---------------------------------------------------------------- Table 5.1 (PDF p.28 / printed p.26)
T51 = "Table 5.1: Mean household income by nation (After Housing Costs, 2026 and 2030)"
blk = join_nation_breaks(
    table_lines(
        r"Table 5\.1: Mean household income by nation",
        r"\nEngland maintains the highest",
    )
)
pat = re.compile(
    r"^(England|Scotland|Wales|Northern Ireland) (£[\d,]+) (£[\d,]+) ([+-]£[\d.]+) (£[\d,]+) (£[\d,]+) ([+-]£[\d.]+)\s*$",
    re.M,
)
NOTE51 = (
    "Column headers print '2026 All Baseline', '2026 All Reform', 'Change', '2030 All Baseline', "
    "'2030 All Reform', 'Change'; the year prefix on 'Change' here is added for disambiguation. "
    "Mean weekly AHC household income for all households in the nation. " + DECILE_NOTE
)
n51 = 0
for m in pat.finditer(blk):
    nation, b26, r26, c26, b30, r30, c30 = m.groups()
    quote = m.group(0).strip()
    for yr, b, r, c in (("2026", b26, r26, c26), ("2030", b30, r30, c30)):
        Y = YEAR[yr]
        base_cond = {
            "fy": Y["fy"],
            "geography": nation,
            "income_group": "all",
            "housing_costs": "ahc",
            "statistic": "mean_weekly_income",
        }
        row(
            T51,
            f"{yr} All Baseline",
            "income_statistic",
            "gbp_per_week",
            gbp_to_num(b),
            b,
            "as printed, GBP per week ('£' stripped)",
            Y["period"],
            {**base_cond, "scenario": "baseline"},
            quote,
            NOTE51,
        )
        row(
            T51,
            f"{yr} All Reform",
            "income_statistic",
            "gbp_per_week",
            gbp_to_num(r),
            r,
            "as printed, GBP per week ('£' stripped)",
            Y["period"],
            {**base_cond, "scenario": "reform"},
            quote,
            NOTE51,
        )
        row(
            T51,
            f"{yr} Change",
            "average_household_income_change",
            "gbp_per_week",
            gbp_to_num(c),
            c,
            "as printed, GBP per week (sign kept, '£' stripped); reform minus baseline",
            Y["period"],
            {
                "fy": Y["fy"],
                "geography": nation,
                "income_group": "all",
                "housing_costs": "ahc",
                "scenario": "reform_minus_baseline",
            },
            quote,
            NOTE51,
        )
        n51 += 3
assert n51 == 24, n51

# ---------------------------------------------------------------- Table 5.2 (PDF p.29 / printed p.27)
T52 = "Table 5.2: Bottom and top decile patterns by nation (2026)"
blk = join_nation_breaks(
    table_lines(
        r"Table 5\.2: Bottom and top decile patterns by nation",
        r"\nNorthern Ireland shows the highest bottom decile",
    )
)
pat = re.compile(
    r"^(England|Scotland|Wales|Northern Ireland) (£[\d,]+) (£[\d,]+) ([+-]£[\d.]+) (£[\d,]+) (£[\d,]+) ([+-]£[\d.]+)\s*$",
    re.M,
)
NOTE52 = (
    "Not explicitly requested (task named Tables 5 and 5.1); staged because it is the decile-1/decile-10 "
    "twin of Table 5.1 — drop by source_table if unwanted. Table title does not state the housing-cost "
    "basis; it sits in §7.1 under Table 5.1 (AHC) and §7 opens 'After housing costs (AHC), see Table 5', "
    "and its England Decile 1 (£155) is consistent with the UK AHC Decile 1 (£159) in Table 5 — "
    "housing_costs omitted per the 'as the table states' rule, confidence medium. 2026 only. "
    "Mean weekly household income, nation's own bottom/top decile. " + DECILE_NOTE
)
n52 = 0
Y = YEAR["2026"]
for m in pat.finditer(blk):
    nation, b1, r1, c1, b10, r10, c10 = m.groups()
    quote = m.group(0).strip()
    for dec, b, r, c in (("1", b1, r1, c1), ("10", b10, r10, c10)):
        ig = f"decile_{dec}"
        base_cond = {
            "fy": Y["fy"],
            "geography": nation,
            "income_group": ig,
            "statistic": "mean_weekly_income",
        }
        row(
            T52,
            f"Decile {dec} Baseline",
            "income_statistic",
            "gbp_per_week",
            gbp_to_num(b),
            b,
            "as printed, GBP per week ('£' and thousands separator stripped)",
            Y["period"],
            {**base_cond, "scenario": "baseline"},
            quote,
            NOTE52,
            conf="medium",
        )
        row(
            T52,
            f"Decile {dec} Reform",
            "income_statistic",
            "gbp_per_week",
            gbp_to_num(r),
            r,
            "as printed, GBP per week ('£' and thousands separator stripped)",
            Y["period"],
            {**base_cond, "scenario": "reform"},
            quote,
            NOTE52,
            conf="medium",
        )
        row(
            T52,
            f"Decile {dec} Change",
            "average_household_income_change",
            "gbp_per_week",
            gbp_to_num(c),
            c,
            "as printed, GBP per week (sign kept, '£' stripped); reform minus baseline",
            Y["period"],
            {
                "fy": Y["fy"],
                "geography": nation,
                "income_group": ig,
                "scenario": "reform_minus_baseline",
            },
            quote,
            NOTE52,
            conf="medium",
        )
        n52 += 3
assert n52 == 24, n52

# ---------------------------------------------------------------- §8 Table 6 (PDF p.30 / printed p.28)
GL_COND = {
    "housing_costs": "ahc",
    "threshold": "1_percent_of_equivalised_ahc_disposable_income",
    "note": THRESH_NOTE,
}
GL_NOTE = (
    "Shares of households (§8: 'households experiencing income changes'; Executive Summary: '1.78% of UK "
    "households'). 'Gainers >1%' = share of households whose AHC equivalised disposable income rises by "
    "more than 1% under the reform; 'Losers >1%' = falls by more than 1%. The paper also mentions a 5% "
    "threshold but prints no 5% table. " + DECILE_NOTE
)
T6 = "Table 6: Distribution of gains and losses (2026 and 2030)"
blk = table_lines(r"Table 6: Distribution of gains and losses", r"\nFigure 3:")
pat = re.compile(r"^(Decile \d+|All) (\S+%) (\S+%) (\S+%) (\S+%)\s*$", re.M)
n6 = 0
for m in pat.finditer(blk):
    label, g26, l26, g30, l30 = m.groups()
    quote = m.group(0).strip()
    ig = "all" if label == "All" else "decile_" + label.split()[1]
    for yr, g, l in (("2026", g26, l26), ("2030", g30, l30)):
        Y = YEAR[yr]
        row(
            T6,
            f"{yr} Gainers >1%",
            "share_gaining",
            "share",
            pct_to_share(g),
            g,
            "percent / 100 -> share",
            Y["period"],
            {
                "fy": Y["fy"],
                "geography": "UK",
                "scenario": "reform_minus_baseline",
                "income_group": ig,
                **GL_COND,
            },
            quote,
            GL_NOTE,
        )
        row(
            T6,
            f"{yr} Losers >1%",
            "share_losing",
            "share",
            pct_to_share(l),
            l,
            "percent / 100 -> share",
            Y["period"],
            {
                "fy": Y["fy"],
                "geography": "UK",
                "scenario": "reform_minus_baseline",
                "income_group": ig,
                **GL_COND,
            },
            quote,
            GL_NOTE,
        )
        n6 += 2
assert n6 == 44, n6

# ---------------------------------------------------------------- prose share_no_change (Exec Summary PDF p.6 / printed p.4; §8 PDF p.29 / printed p.27)
NC_NOTE = (
    "Share within +/-1% is printed only in prose (no table; Figure 3 is a chart). Executive Summary "
    "('Distribution of Impacts', printed p.4) gives 91.73% for 2026; §8 (printed p.27) gives '91.7% in 2026, "
    "90.7% in 2030'; Key Findings gives '90.7 -91.7%'. The 2026 row uses the more precise Executive Summary "
    "figure; the §8 '91.7%' is the same number rounded and is not staged separately. Equals 100 - gainers - "
    "losers from Table 6 'All' (paper's own arithmetic, printed). " + GL_NOTE
)
q1 = "The majority of households (91.73%) see minimal income change (<1% \neither way)."
assert q1 in TEXT
row(
    "Executive Summary, 'Distribution of Impacts' (prose, printed p.4; companion to Table 6)",
    "prose: households with minimal income change (<1% either way), 2026",
    "share_no_change",
    "share",
    pct_to_share("91.73%"),
    "91.73%",
    "percent / 100 -> share",
    YEAR["2026"]["period"],
    {
        "fy": "2026-27",
        "geography": "UK",
        "scenario": "reform_minus_baseline",
        "income_group": "all",
        **GL_COND,
    },
    q1.replace("\n", ""),
    NC_NOTE,
)
q2 = "Most households (91.7% in 2026, 90.7% in 2030) experience minimal \nincome change (<1% either direction)."
assert q2 in TEXT
row(
    "§8 Gainers and Losers Analysis (prose, printed p.27; companion to Table 6)",
    "prose: households with minimal income change (<1% either direction), 2030",
    "share_no_change",
    "share",
    pct_to_share("90.7%"),
    "90.7%",
    "percent / 100 -> share",
    YEAR["2030"]["period"],
    {
        "fy": "2030-31",
        "geography": "UK",
        "scenario": "reform_minus_baseline",
        "income_group": "all",
        **GL_COND,
    },
    q2.replace("\n", ""),
    NC_NOTE,
)
nnc = 2

# ---------------------------------------------------------------- Table 6.1 (PDF p.31 / printed p.29)
T61 = "Table 6.1: Household type patterns (2026 and 2030)"
blk = table_lines(
    r"Table 6\.1: Household type patterns \(2026 and 2030\)", r"\n===== PAGE 32"
)
pat = re.compile(
    r"^(With Children|Lone Parent|Three\+ Children|Elderly|No Earners|Disabled|Two\+ Earners) (\S+%) (\S+%) (\S+%) (\S+%)\s*$",
    re.M,
)
NOTE61 = (
    "By household type (not requested by decile; staged as part of 'every number in the gainers/losers "
    "section' — drop by source_table if unwanted). Household types as printed; the paper does not define "
    "them. " + GL_NOTE
)
n61 = 0
for m in pat.finditer(blk):
    ht, g26, l26, g30, l30 = m.groups()
    quote = m.group(0).strip()
    for yr, g, l in (("2026", g26, l26), ("2030", g30, l30)):
        Y = YEAR[yr]
        cond = {
            "fy": Y["fy"],
            "geography": "UK",
            "scenario": "reform_minus_baseline",
            "income_group": "all",
            "household_type": ht,
            **GL_COND,
        }
        row(
            T61,
            f"{yr} Gainers >1%",
            "share_gaining",
            "share",
            pct_to_share(g),
            g,
            "percent / 100 -> share",
            Y["period"],
            cond,
            quote,
            NOTE61,
        )
        row(
            T61,
            f"{yr} Losers >1%",
            "share_losing",
            "share",
            pct_to_share(l),
            l,
            "percent / 100 -> share",
            Y["period"],
            cond,
            quote,
            NOTE61,
        )
        n61 += 2
assert n61 == 28, n61

# ---------------------------------------------------------------- Table 6.2 (PDF p.32 / printed p.30)
T62 = "Table 6.2: Gainers and Losers by Nation (2026 and 2030)"
blk = join_nation_breaks(
    table_lines(r"Table 6\.2: Gainers and Losers by Nation", r"\n===== PAGE 33")
)
pat = re.compile(
    r"^(England|Scotland|Wales|Northern Ireland) (\S+%) (\S+%) (\S+%) (\S+%)\s*$", re.M
)
NOTE62 = "By nation, all households. " + GL_NOTE
n62 = 0
for m in pat.finditer(blk):
    nation, g26, l26, g30, l30 = m.groups()
    quote = m.group(0).strip()
    for yr, g, l in (("2026", g26, l26), ("2030", g30, l30)):
        Y = YEAR[yr]
        cond = {
            "fy": Y["fy"],
            "geography": nation,
            "scenario": "reform_minus_baseline",
            "income_group": "all",
            **GL_COND,
        }
        row(
            T62,
            f"{yr} All Gainers >1%",
            "share_gaining",
            "share",
            pct_to_share(g),
            g,
            "percent / 100 -> share",
            Y["period"],
            cond,
            quote,
            NOTE62,
        )
        row(
            T62,
            f"{yr} All Losers >1%",
            "share_losing",
            "share",
            pct_to_share(l),
            l,
            "percent / 100 -> share",
            Y["period"],
            cond,
            quote,
            NOTE62,
        )
        n62 += 2
assert n62 == 16, n62

# ---------------------------------------------------------------- Table 6.3 (PDF p.33 / printed p.31)
T63 = "Table 6.3: Household type patterns by nation (2026)"
blk = join_nation_breaks(
    table_lines(
        r"Table 6\.3: Household type patterns by nation", r"\nFigure 3\.2 shows"
    )
)
pat = re.compile(
    r"^(England|Scotland|Wales|Northern Ireland) (\S+%) (\S+%) (\S+%) (\S+%)\s*$", re.M
)
NOTE63 = (
    "By nation x household type, 2026 only. Column headers print 'Elderly Gainers' / 'Elderly Losers' / "
    "'With Children Gainers' / 'With Children Losers' without the '>1%' suffix; the 1% threshold is taken "
    "from the §8 section intro (medium confidence on the threshold, not the number). "
    + NOTE61
)
n63 = 0
Y = YEAR["2026"]
for m in pat.finditer(blk):
    nation, eg, el, cg, cl = m.groups()
    quote = m.group(0).strip()
    for ht, g, l, cg_, cl_ in (
        ("Elderly", eg, el, "Elderly Gainers", "Elderly Losers"),
        ("With Children", cg, cl, "With Children Gainers", "With Children Losers"),
    ):
        cond = {
            "fy": Y["fy"],
            "geography": nation,
            "scenario": "reform_minus_baseline",
            "income_group": "all",
            "household_type": ht,
            **GL_COND,
        }
        row(
            T63,
            cg_,
            "share_gaining",
            "share",
            pct_to_share(g),
            g,
            "percent / 100 -> share",
            Y["period"],
            cond,
            quote,
            NOTE63,
            conf="medium",
        )
        row(
            T63,
            cl_,
            "share_losing",
            "share",
            pct_to_share(l),
            l,
            "percent / 100 -> share",
            Y["period"],
            cond,
            quote,
            NOTE63,
            conf="medium",
        )
        n63 += 2
assert n63 == 16, n63

# ---------------------------------------------------------------- verbatim check + write
FIELDS = [
    "source_table",
    "source_column",
    "proposed_metric",
    "proposed_unit",
    "value",
    "value_raw",
    "normalization",
    "value_kind",
    "period",
    "conditions",
    "quote",
    "note",
    "parse_confidence",
]
text_joined = join_nation_breaks(TEXT).replace("\n", "")
not_found_raw = [r for r in rows if r["value_raw"] not in TEXT]
not_found_quote = [
    r
    for r in rows
    if r["quote"] not in join_nation_breaks(TEXT) and r["quote"] not in text_joined
]
for r in rows:
    assert list(r.keys()) == FIELDS, r.keys()
    assert isinstance(r["value"], float) or isinstance(r["value"], int)
with OUT.open("w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

from collections import Counter

print("rows per table:")
for k, v in Counter(r["source_table"] for r in rows).items():
    print(f"  {v:3d}  {k}")
print("total rows:", len(rows))
print(
    "value_raw NOT found in text:",
    len(not_found_raw),
    [r["value_raw"] for r in not_found_raw],
)
print(
    "quote NOT found in text:",
    len(not_found_quote),
    [r["quote"] for r in not_found_quote],
)
# cell-count check per table (a cell = one printed number)
print(
    "cells: T4",
    n4,
    "T4.1",
    n41,
    "T5",
    n5,
    "T5.1",
    n51,
    "T5.2",
    n52,
    "T6",
    n6,
    "prose",
    nnc,
    "T6.1",
    n61,
    "T6.2",
    n62,
    "T6.3",
    n63,
)
