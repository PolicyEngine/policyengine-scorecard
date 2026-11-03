#!/usr/bin/env python3
"""Stage CenTax's Autumn Budget 2026 claims (#230, family uk_centax).

The rows are data in this file. Running it rewrites manifest.jsonl and
claims_staged.jsonl.gz byte for byte:

    python sources/harvest-uk-ab2026-2026-10-29/uk_centax/stage.py

`--verify` also checks, where the primaries are present under
.ab2026-primaries/uk_centax/ (git-ignored, hashed not vendored), that each
primary hashes to its manifest sha256 and that every quote occurs in its
primary's text (HTML text, or `pdftotext -layout` output, whitespace
normalised).
"""

import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIMARIES = ROOT / ".ab2026-primaries" / "uk_centax"
SOURCE = "centax"
EVENT = "autumn_budget_2026"
PUBLISHER = "CenTax (Centre for the Analysis of Taxation)"
YIELD = "positive = yield to the Exchequer"
COST = "positive = cost to the Exchequer"
HMRC = "hmrc_administrative_microdata"

PUBS = {
    "RX": {
        "url": "https://centax.org.uk/autumn-budget-2026-reaction/",
        "title": "Autumn Budget 2026: Initial reaction",
        "date": "2026-10-28",
        "publisher": PUBLISHER,
        "sha256": "92c6008835547d411b67b9f23edecae77a45ba67985d5364d6bebde20f7be457",
        "bytes": 248542,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Page dated 28 October 2026 and marked 'This page is being updated live'; the copy hashed is the fetch of 2026-10-29T16:17Z (curl, browser User-Agent, HTTP 200). No published or modified time in the page metadata.",
        "file": "autumn-budget-2026-reaction.html",
    },
    "TTH": {
        "url": "https://centax.org.uk/taxes-at-the-top-understanding-what-high-earners-pay/",
        "title": "Taxes at the top: Understanding what high earners pay and options for reform (landing page)",
        "date": "2026-09-23",
        "publisher": PUBLISHER,
        "sha256": "c954e08f2aa6de7aaedb5e12f8df16ea93a44033e72c1bb08d25c5159e6aac33",
        "bytes": 267599,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Linked from the reaction page's related-publications panel ('reforms available at the 2026 Budget'); 0 rows, the landing page prints no figures; links the PDF. Fetched 2026-10-29T16:30Z.",
        "file": "taxes-at-the-top.html",
    },
    "TT": {
        "url": "https://centax.org.uk/wp-content/uploads/2026/09/AdvaniHughsonSummers2026_Taxes-at-the-top.pdf",
        "title": "Taxes at the top: Understanding what high earners pay and options for reform (Advani, Hughson and Summers, September 2026)",
        "date": "2026-09-23",
        "publisher": PUBLISHER,
        "sha256": "af4cab614220c28640c0d875ab24aea263c54ec75957cfe263f6dbac171857f3",
        "bytes": 963857,
        "doc_type": "pdf",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "35 pp.; PDF CreationDate 2026-09-23. Text read with pdftotext -layout; locators are printed page numbers (Key findings = p. 1). Fetched 2026-10-29T16:31Z.",
        "file": "taxes-at-the-top.pdf",
    },
    "URH": {
        "url": "https://centax.org.uk/capital-gains-tax-should-the-uk-have-a-unicorn-relief/",
        "title": "Capital Gains Tax on Entrepreneurs: Should the UK have a ‘Unicorn Relief’? (landing page)",
        "date": "2026-10-08",
        "publisher": PUBLISHER,
        "sha256": "91a6c8dc749273b1c6b6e330a2acaef4010a379d5e82e1bab22c4a820c5cb65a",
        "bytes": 267896,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Linked from the reaction page's related-publications panel; 0 rows, the landing page prints no figures; links the PDF. Fetched 2026-10-29T16:30Z.",
        "file": "unicorn-relief.html",
    },
    "UR": {
        "url": "https://centax.org.uk/wp-content/uploads/2026/10/AdvaniFlewGazmuri-BarkerSummers2026_CGT-on-Entrepreneurs-Unicorn-Relief.pdf",
        "title": "Capital Gains Tax on Entrepreneurs: Should the UK have a ‘Unicorn Relief’? (Advani, Flew, Gazmuri-Barker and Summers, October 2026)",
        "date": "2026-10-08",
        "publisher": PUBLISHER,
        "sha256": "9fd8ce97f3343f7aee1cab11dede3f374ba473b8db4056268a0becc154e7a71b",
        "bytes": 568966,
        "doc_type": "pdf",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "74 pp.; PDF CreationDate 2026-10-08. Text read with pdftotext -layout; locators are printed page numbers. Fetched 2026-10-29T16:31Z.",
        "file": "unicorn-relief.pdf",
    },
}

CGT = "ab2026_option__cgt_reform_package"
PNIC = "ab2026_option__nics_on_partnership_income"
INIC = "ab2026_option__nics_on_investment_income"
CC_REMOVE = "ab2026_option__childcare_100k_threshold_removed"
CC_15H = "ab2026_option__childcare_100k_threshold_removed_first_15_hours_under_3s"
CC_RAISE = "ab2026_option__childcare_100k_threshold_raised"
CC_TAPER = "ab2026_option__childcare_100k_entitlement_taper"
TAXGAP = "ab2026__hmrc_tax_gap_package"
PTA = "ab2026__pension_tax_allowance"

H_CGT = "CenTax's CGT package: equalise CGT rates with Income Tax rates, an investment allowance for the risk-free rate, remove uplift at death, rebasing on arrival with deemed disposal on departure (the first four costed; more generous loss relief not costed)"
H_PNIC = "an equivalent of Employer NICs on partnership profits (top-up rate), with a £10,500 Partnership allowance and a £5,000 exempt amount per partner"
H_INIC = "an equivalent of Class 1 NICs on rental income, savings income outside ISAs and other non-dividend investment income"
H_CC = "remove the £100,000 income threshold for free childcare entitlement in England"
H_PTA = "Pension Tax Allowance: an additional tax-free amount covering the difference between the Personal Allowance and the state pension, withdrawn at £1 for every £3 of income above the state pension"

ROWS = []
CHECKS = []


def bn(x):
    return round(x * 1e9)


def mn(x):
    return round(x * 1e6)


def add(
    pub, value, value_raw, quote, locator, *,
    metric=None, pmetric=None, unit=None, punit=None, normalization="as printed",
    fy=None, period=None, time_basis=None, key=None, pkey=None,
    attribution="own", bclass="different_model", model=HMRC, kind="point",
    cond=None, hint=None, table=None, column=None, note="", conf="high", geography="UK",
):
    p = PUBS[pub]
    c = {"fiscal_event": EVENT, "geography": geography}
    if fy:
        c["fy"] = fy
        period = int(fy[:4]) + 1
        time_basis = "fiscal_year"
    c.update(cond or {})
    if pkey:
        assert key is None
        c["proposed_measure_key"] = pkey
    r = {
        "source": SOURCE, "source_model": model, "value": value, "value_raw": value_raw,
        "normalization": normalization, "value_kind": kind, "period": period, "time_basis": time_basis,
        "conditions": c, "reform_hint": hint, "measure_key": key, "attribution": attribution,
        "benchmark_class": bclass, "baseline_policy": None,
        "publication": {"title": p["title"], "url": p["url"], "date": p["date"], "publisher": p["publisher"],
                        "primary_sha256": p["sha256"], "locator": locator, "access": p["access"]},
        "source_table": table, "source_column": column, "quote": quote, "note": note,
        "parse_confidence": conf, "status": "ok",
    }
    for k, v in (("metric", metric), ("proposed_metric", pmetric), ("unit_concept", unit), ("proposed_unit", punit)):
        if v:
            r[k] = v
    assert value_raw in quote, (value_raw, quote)
    assert len(quote.split()) < 15, quote
    CHECKS.append((len(ROWS), pub))
    ROWS.append(r)


YEARS = "CenTax gives tax years as the later year ('2022 is tax year 2021-22', Taxes at the top fn 2)"
NOYEAR = "no year in the sentence; staged with the 2030 costing it describes; " + YEARS

# === 1. Autumn Budget 2026: Initial reaction (28 October 2026) ==============

add("RX", 53, "53%", "the new allowance adds additional complexity and a new marginal rate of 53%",
    "'Pension Tax Allowance' section, seventh paragraph",
    pmetric="marginal_tax_rate", unit="percent", fy="2027-28", key=PTA, model="arithmetic",
    cond={"subgroup": "pensioners with income in the allowance's withdrawal band",
          "withdrawal_rate": "£1 of allowance for every £3 of income above the state pension ('a marginal tax rate of 33.3%', as printed)"},
    hint=H_PTA, note="CenTax's arithmetic: the basic rate plus the allowance's withdrawal. The withdrawal rate itself (33.3%) is the allowance's design and is kept in conditions (README rule 8).")
add("RX", mn(640), "£640 million",
    "removing the threshold for the free childcare entitlement would be around £640 million",
    "'Carer’s Allowance' section, fourth paragraph",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2029-30", pkey=CC_REMOVE,
    geography="England",
    cond={"basis": "post_behavioural", "sign_convention": COST, "scenario": "central",
          "year_note": "'in 2030'; " + YEARS},
    hint=H_CC,
    note="CenTax repeats its own September 2026 estimate (Removing the £100,000 childcare cliff-edge, Table 4.2 central net fiscal cost, already in data/externals/centax-childcare-100k.json, #207). An option the Budget did not take.")
add("RX", bn(1.6), "£1.6 billion", "This reform is forecast to raise around £1.6 billion a year",
    "'Timely payments for Self Assessment' section, fifth paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2030-31", key=TAXGAP,
    model="arithmetic",
    cond={"basis": "forecast", "sign_convention": YIELD, "statistic": "mean",
          "row_type": "measure_component",
          "component": "More timely payment for Self Assessment (HM Treasury Budget 2026 Table 6.3 line 3)",
          "horizon": "a year averaged over 2029-30 to 2031-32 (staged at the middle year)",
          "derived_from": "HM Treasury Budget 2026 Table 6.3 line 3 (£1,355m, £1,605m, £1,815m), part of Table 6.1 line 45"},
    hint="More timely payment: Income Tax Self Assessment taxpayers who make payments on account pay more in-year from April 2029",
    note="CenTax's average of HM Treasury's yearly costing (mean £1,592m); arithmetic, not an independent estimate. A sub-measure of Table 6.1 line 45, so it carries line 45's key with row_type measure_component (README rule 9).")

# === 2. Taxes at the top (23 September 2026) ================================

KF = "p. 1, Key findings"
TOP = {"top_10pct": "top 10%", "top_1pct": "top 1%", "top_0.1pct": "top 0.1%", "top_0.01pct": "top 0.01%"}
DESC = dict(model=HMRC, bclass="administrative_fact")
REM = "total remuneration (taxable income plus realised capital gains)"
INC = "total taxable income"


def desc(value, raw, quote, loc, *, metric=None, pmetric=None, unit, fy="2021-22", cond=None, kind="point", note="", conf="high", normalization="as printed"):
    add("TT", value, raw, quote, loc, metric=metric, pmetric=pmetric, unit=unit, fy=fy, kind=kind,
        cond={"basis": "outturn", "year_note": YEARS, **(cond or {})}, note=note or "Descriptive statistic from HMRC administrative data; context, no measure key.",
        conf=conf, normalization=normalization, **DESC)


desc(0.405, "40.5%", "The top 10% received 40.5% of total taxable income", KF + ", item 1",
     metric="income_share", unit="share", normalization="40.5% -> 0.405",
     cond={"income_group": "top_10pct", "income_concept": INC})
desc(0.60, "60%", "income and paid 60% of Income Tax and National Insurance", KF + ", item 1",
     metric="revenue_share", unit="share", normalization="60% -> 0.60",
     cond={"income_group": "top_10pct", "income_concept": INC,
           "measure_type": "share of total Income Tax and NICs paid"})
desc(0.439, "43.9%", "raises their share of remuneration to 43.9%", KF + ", item 1",
     metric="income_share", unit="share", normalization="43.9% -> 0.439",
     cond={"income_group": "top_10pct", "income_concept": REM})
desc(0.615, "61.5%", "their share of tax paid only increases to 61.5%", KF + ", item 1",
     metric="revenue_share", unit="share", normalization="61.5% -> 0.615",
     cond={"income_group": "top_10pct", "income_concept": REM,
           "measure_type": "share of Income Tax, NICs and CGT paid"})
for v, raw, grp, q in [(37, "37%", "top_1pct", "37% for the top 1%, 34% for the top 0.1%"),
                       (34, "34%", "top_0.1pct", "37% for the top 1%, 34% for the top 0.1%"),
                       (30, "30%", "top_0.01pct", "and down to 30% for the top 0.01%")]:
    desc(v, raw, q, KF + ", item 2", metric="average_tax_rate", unit="percent",
         cond={"income_group": grp, "income_concept": REM, "statistic": "mean effective average tax rate (EATR)"})
for v, raw, fy, grp, q in [
    (17, "17%", "2007-08", "median", "average effective tax rates paid by the median taxpayer fell from 17% to 12%"),
    (12, "12%", "2021-22", "median", "average effective tax rates paid by the median taxpayer fell from 17% to 12%"),
    (33, "33%", "2007-08", "p99", "whilst rates for those at the top 1% rose from 33% to 36%"),
    (36, "36%", "2021-22", "p99", "whilst rates for those at the top 1% rose from 33% to 36%"),
    (37, "37%", "2007-08", "p99.99", "(equivalent to remuneration of around £5 million in 2022) fell from 37% to 33%"),
    (33, "33%", "2021-22", "p99.99", "(equivalent to remuneration of around £5 million in 2022) fell from 37% to 33%"),
]:
    desc(v, raw, q, KF + ", item 3", metric="average_tax_rate", unit="percent", fy=fy,
         cond={"income_group": grp, "income_concept": REM,
               "statistic": "mean EATR of taxpayers within 1% of the percentile (pp. 12-14)"})
desc(0.1, "one in ten", "one in ten pays close to the headline rate of 47%",
     KF + ", item 4", pmetric="taxpayer_share", unit="share", normalization="one in ten -> 0.1",
     cond={"income_group": "top_0.01pct", "income_concept": REM, "eatr_band": "close to the 47% headline rate"})
desc(0.25, "a quarter", "whilst a quarter pay 20% or less", KF + ", item 4",
     pmetric="taxpayer_share", unit="share", normalization="a quarter -> 0.25",
     cond={"income_group": "top_0.01pct", "income_concept": REM, "eatr_band": "20% or less"})
add("TT", 23, "23%", "this lower threshold is likely to have risen to 23%", KF + ", item 4",
    pmetric="effective_tax_rate", unit="percent", fy="2026-27", conf="medium",
    cond={"income_group": "top_0.01pct", "income_concept": REM, "statistic": "25th percentile EATR",
          "scenario": "after the CGT rate and relief changes since 2022",
          "year_note": "no year stated; staged at 2026-27, the tax year of the report"},
    note="CenTax's judgement of where the 2022 25th percentile (20%) has moved; context, no measure key.")
add("TT", 62, "62%", "equalising rates with Income Tax would increase revenue by 62%",
    KF + ", item 5", metric="revenue_change", unit="percent", fy="2029-30", pkey=CGT,
    cond={"basis": "post_behavioural", "scenario": "central", "sign_convention": YIELD,
          "denominator": "baseline CGT revenue", "year_note": YEARS},
    hint=H_CGT, note="The body (p. 17) repeats it; staged once.")
add("TT", 88, "88%", "This is down from the 88% increase we estimated in 2024", KF + ", item 5",
    metric="revenue_change", unit="percent", fy="2025-26", pkey=CGT,
    cond={"basis": "post_behavioural", "sign_convention": YIELD, "denominator": "baseline CGT revenue",
          "scenario": "Advani, Lonsdale and Summers (2024) estimate, before the Autumn Budget 2024 CGT changes",
          "year_note": "the 2024 estimate was for 2026 (p. 17); " + YEARS},
    hint=H_CGT, note="CenTax's earlier estimate, reported for comparison.")
add("TT", bn(19.7), "£19.7 billion", "It equates to £19.7 billion of additional revenue by 2030", KF + ", item 5",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2029-30", pkey=CGT,
    cond={"basis": "post_behavioural", "scenario": "central", "sign_convention": YIELD,
          "baseline_forecast": "OBR baseline forecast of £32 billion for CGT (p. 17)", "year_note": YEARS},
    hint=H_CGT, note="Key findings say 'by 2030'; p. 17 says 'in 2030'. Staged once.")
add("TT", bn(2.1), "£2.1 billion", "Employer NICs to partnership profits would raise £2.1 billion in 2030",
    KF + ", item 6", metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2029-30", pkey=PNIC,
    cond={"basis": "post_behavioural", "scenario": "central", "sign_convention": YIELD, "year_note": YEARS},
    hint=H_PNIC, note="p. 20: 'Our updated central revenue estimate, after accounting for behavioural responses'.")
add("TT", 0.98, "98%", "98% of this revenue would come from the top decile", KF + ", item 6",
    metric="revenue_share", unit="share", normalization="98% -> 0.98", fy="2029-30", pkey=PNIC,
    cond={"income_group": "decile_10", "income_concept": INC, "year_note": YEARS}, hint=H_PNIC)
add("TT", bn(4), "£4 billion", "Class 1 NICs to investment income could raise up to £4 billion", KF + ", item 7",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2029-30", pkey=INIC, kind="range_high",
    cond={"basis": "static", "sign_convention": YIELD, "income_type": "all three (total)", "year_note": YEARS},
    hint=H_INIC, note="'This is a static estimate, so before behavioural responses'; p. 22 splits it £3bn / £0.6bn / £0.4bn.")
add("TT", mn(640), "£640 million", "Removing the £100,000 childcare cliff-edge would cost £640 million", KF + ", item 8",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2029-30", pkey=CC_REMOVE, geography="England",
    cond={"basis": "post_behavioural", "scenario": "central", "sign_convention": COST, "year_note": YEARS},
    hint=H_CC, note="Repeats the September 2026 childcare report (Table 4.2, in data/externals/centax-childcare-100k.json, #207). pp. 25 and 27 repeat it; staged once.")
CCQ = "set to rise eleven-fold, from 1,100 in 2022 to 11,980 by 2030"
add("TT", 1100, "1,100", CCQ, KF + ", item 8", metric="affected_count", unit="persons", fy="2021-22",
    geography="England", bclass="administrative_fact",
    cond={"basis": "outturn", "subgroup": "parents holding their incomes below £100,000 (bunching)", "year_note": YEARS},
    note="Observed in 2022 HMRC data; current-policy context, no measure key. p. 23 repeats it.")
add("TT", 11980, "11,980", CCQ, KF + ", item 8", metric="affected_count", unit="persons", fy="2029-30",
    geography="England",
    cond={"basis": "forecast", "scenario": "if the cliff-edge remains in place",
          "subgroup": "parents holding their incomes below £100,000 (bunching)", "year_note": YEARS},
    note="Current-policy projection; context, no measure key.")
add("TT", 0.03, "3%", "3% of lower paid partners of individuals earning just over £100,000 leaving the workforce",
    KF + ", item 8", pmetric="workforce_exit_share", unit="share", normalization="3% -> 0.03", fy="2021-22",
    geography="England", bclass="administrative_fact",
    cond={"basis": "outturn", "subgroup": "lower-paid partners of individuals earning just over £100,000", "year_note": YEARS},
    note="Current-policy effect in 2022 data; context, no measure key. p. 24 gives the underlying 6% and 9%.")
add("TT", 0.9, "90%", "with 90% of those partners being women", KF + ", item 8",
    pmetric="female_share", unit="share", normalization="90% -> 0.9", fy="2021-22",
    geography="England", bclass="administrative_fact",
    cond={"basis": "outturn", "subgroup": "partners leaving the workforce at the cliff-edge", "year_note": YEARS},
    note="Context, no measure key. p. 24 repeats it ('mothers leaving work'); staged once.")

P5 = "p. 5, section 2.1"
for v, raw, grp, q in [
    (51000, "£51,000", "p90 (top 10%)", "an individual would have needed £51,000 in 2022"),
    (173000, "£173,000", "p99 (top 1%)", "they would have needed £173,000, £862,000 or £4,999,000 respectively"),
    (862000, "£862,000", "p99.9 (top 0.1%)", "they would have needed £173,000, £862,000 or £4,999,000 respectively"),
    (4999000, "£4,999,000", "p99.99 (top 0.01%)", "they would have needed £173,000, £862,000 or £4,999,000 respectively"),
]:
    desc(v, raw, q, P5, metric="income_statistic", unit="gbp",
         cond={"income_concept": REM, "statistic": f"entry threshold, {grp}"})
for v, raw, grp, q in [
    (50800, "£50,800", "p90 (top 10%)", "an individual would have needed £50,800 in 2022"),
    (160000, "£160,000", "p99 (top 1%)", "they would have needed £160,000 or £653,000 or £2,832,000 respectively"),
    (653000, "£653,000", "p99.9 (top 0.1%)", "they would have needed £160,000 or £653,000 or £2,832,000 respectively"),
    (2832000, "£2,832,000", "p99.99 (top 0.01%)", "they would have needed £160,000 or £653,000 or £2,832,000 respectively"),
]:
    desc(v, raw, q, P5, metric="income_statistic", unit="gbp",
         cond={"income_concept": INC, "statistic": f"entry threshold, {grp}"})
GAP ={"measure_type": "gap between the headline Income Tax and NICs rate and the mean EATR"}
desc(2.8, "2.8 percentage points", "by around 2.8 percentage points on average", "p. 8, section 2.3",
     pmetric="effective_tax_rate_gap", unit="percentage_points",
     cond={**GAP, "income_concept": INC, "income_group": "top groups, on average"})
desc(2.9, "2.9 percentage points", "is similar (2.9 percentage points) for the top 10%", "p. 9",
     pmetric="effective_tax_rate_gap", unit="percentage_points",
     cond={**GAP, "income_concept": REM, "income_group": "top_10pct"})
for v, raw, concept in [(5.8, "5.8 percentage points", REM), (2.6, "2.6 percentage points", INC)]:
    desc(v, raw, "an average of 5.8 percentage points (versus 2.6 percentage points on income)", "p. 9",
         pmetric="effective_tax_rate_gap", unit="percentage_points",
         cond={**GAP, "income_concept": concept, "income_group": "top_1pct"})
for v, grp in [(12, "top_0.1pct"), (16, "top_0.01pct")]:
    desc(v, str(v), "to 12 and 16 percentage points, respectively for the top 0.1% and 0.01%", "p. 9",
         pmetric="effective_tax_rate_gap", unit="percentage_points",
         cond={**GAP, "income_concept": REM, "income_group": grp})
for v, raw, kind in [(19, "19%", "range_low"), (35, "35%", "range_high")]:
    desc(v, raw, "continue increasing from 19% to 35% within the top decile", "p. 9", metric="average_tax_rate",
         unit="percent", kind=kind,
         cond={"income_concept": REM, "income_group": "decile_10", "statistic": "mean EATR, range across the top decile"})
P11 = "p. 11, section 2.4"
for v, raw, grp, band, q in [
    (0.5, "half", "top_10pct", "around the headline rates", "half of the individuals have EATRs around the headline rates"),
    (0.25, "one in four", "top_10pct", "at least 2.2 percentage points below the headline rate", "one in four with EATRs at least 2.2 percentage points below the headline rate"),
    (0.5, "Half", "top_1pct", "close to the headline rates", "Half of the individuals amongst the top 1% also have EATRs"),
    (0.25, "a quarter", "top_1pct", "below 36% (headline rates around 40-45%)", "a quarter of this group has EATRs below 36%"),
    (0.25, "a quarter", "top_0.1pct", "close to the headline rates of 45-47%", "only a quarter of individuals have EATRs close to the headline rates"),
    (0.25, "another quarter", "top_0.1pct", "below 28%", "whilst another quarter has EATRs below 28%"),
    (0.5, "half", "top_0.01pct", "30% or less", "half have EATRs of 30% or less"),
]:
    desc(v, raw, q, P11, pmetric="taxpayer_share", unit="share", normalization=f"{raw} -> {v}",
         cond={"income_concept": REM, "income_group": grp, "eatr_band": band})
desc(18700, "£18,700", "around £18,700 (median)", "p. 12, section 2.5", metric="income_statistic", unit="gbp",
     cond={"income_concept": REM, "statistic": "median"})
for v, raw, fy in [(35, "35%", "2014-15"), (27, "27%", "2019-20")]:
    desc(v, raw, "fell significantly from 35% in 2015 to 27% in 2020", "p. 13", metric="average_tax_rate",
         unit="percent", fy=fy,
         cond={"income_concept": REM, "income_group": "p99.99",
               "statistic": "mean EATR of taxpayers within 1% of the 99.99th percentile"})

P17 = "p. 17, section 3.1"
add("TT", bn(32), "£32 billion", "the current Office for Budget Responsibility (OBR) baseline forecast of £32 billion for CGT",
    P17, metric="tax_collections", unit="gbp", normalization="£ billion × 1e9", fy="2029-30",
    attribution="restated", model="obr_efo_forecast",
    cond={"basis": "forecast", "originator": "OBR, Economic and fiscal outlook: March 2026 (fn 10)", "tax": "CGT",
          "year_note": "the CGT forecast for 2030; " + YEARS},
    note="OBR baseline restated; context.")
add("TT", bn(16), "£16 billion", "This forecast is double the £16 billion that OBR forecast for 2026", P17,
    metric="tax_collections", unit="gbp", normalization="£ billion × 1e9", fy="2025-26",
    attribution="restated", model="obr_efo_forecast",
    cond={"basis": "forecast", "originator": "OBR forecast used in Advani, Lonsdale and Summers (2024)", "tax": "CGT",
          "year_note": YEARS},
    note="An earlier OBR forecast restated; context.")
add("TT", bn(14), "£14 billion", "(£19.7 billion now, vs £14 billion then)", P17,
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2025-26", pkey=CGT,
    cond={"basis": "post_behavioural", "sign_convention": YIELD,
          "scenario": "Advani, Lonsdale and Summers (2024) estimate", "year_note": "the 2024 estimate was for 2026; " + YEARS},
    hint=H_CGT, note="CenTax's earlier estimate, reported for comparison.")
P18 = "p. 18, section 3.1"
add("TT", 0.19, "19%", "On a static basis, 19% of the additional revenue from our proposed reform", P18,
    metric="revenue_share", unit="share", normalization="19% -> 0.19", fy="2029-30", pkey=CGT,
    cond={"basis": "static", "income_group": "top_0.1pct",
          "income_concept": "total income before capital gains", "year_note": NOYEAR}, hint=H_CGT)
add("TT", 0.70, "70%", "70% comes from those who are in the top 0.1%", P18,
    metric="revenue_share", unit="share", normalization="70% -> 0.70", fy="2029-30", pkey=CGT,
    cond={"basis": "static", "income_group": "top_0.1pct",
          "income_concept": "average total remuneration over the past five years", "year_note": NOYEAR}, hint=H_CGT)
P19 = "p. 19, section 3.2"
add("TT", 0.46, "46%", "nearly half (46%) accruing to the top 0.1% of the income distribution",
    P19, metric="income_share", unit="share", normalization="46% -> 0.46", fy="2019-20",
    bclass="administrative_fact",
    cond={"basis": "outturn", "income_group": "top_0.1pct", "income_concept": "partnership profits", "year_note": YEARS},
    note="Descriptive statistic from HMRC administrative data; context, no measure key.")
P20 = "p. 20, section 3.2"
add("TT", 0.58, "58%", "with 58% from the top 0.1% alone", P20, metric="revenue_share", unit="share",
    normalization="58% -> 0.58", fy="2029-30", pkey=PNIC,
    cond={"income_group": "top_0.1pct", "income_concept": INC, "year_note": NOYEAR}, hint=H_PNIC)
add("TT", 0.70, "over 70%", "would account for over 70% of all taxpayers affected by the reform", P20,
    metric="affected_share", unit="share", normalization="over 70% -> 0.70", fy="2029-30", pkey=PNIC, kind="range_low",
    cond={"income_group": "decile_10", "income_concept": INC, "denominator": "taxpayers affected by the reform", "year_note": NOYEAR},
    hint=H_PNIC)
add("TT", 0.09, "9%", "make up just 9% of the affected population", P20, metric="affected_share", unit="share",
    normalization="9% -> 0.09", fy="2029-30", pkey=PNIC,
    cond={"income_group": "bottom_50pct", "income_concept": INC, "denominator": "taxpayers affected by the reform", "year_note": NOYEAR},
    hint=H_PNIC)
add("TT", 0.005, "less than 0.5%", "would contribute less than 0.5% of total revenue", P20, metric="revenue_share",
    unit="share", normalization="less than 0.5% -> 0.005", fy="2029-30", pkey=PNIC, kind="range_high",
    cond={"income_group": "bottom_50pct", "income_concept": INC, "year_note": NOYEAR}, hint=H_PNIC)
T1 = "Table 1: Share of revenue raised from NICs on partnerships, by income distribution"
for grp, label, rev, aff in [
    ("bottom_50pct", "Bottom 50%", "0.40%", "8.75%"), ("p50_p60", "50% - 60%", "0.16%", "2.51%"),
    ("p60_p70", "60% - 70%", "0.19%", "2.50%"), ("p70_p80", "70% - 80%", "0.36%", "4.15%"),
    ("p80_p90", "80% - 90%", "1.00%", "11.77%"), ("p90_p99", "90% - 99%", "11.53%", "40.30%"),
    ("p99_p99.5", "99% - 99.5%", "9.39%", "11.58%"), ("p99.5_p99.9", "99.5% - 99.9%", "19.44%", "12.09%"),
    ("top_0.1pct", "Top 0.1%", "57.52%", "6.36%"),
]:
    q = f"{label} {rev} {aff}"
    for raw, metric, col in [(rev, "revenue_share", "Share of revenue raised"), (aff, "affected_share", "Share of affected population")]:
        v = round(float(raw.rstrip("%")) / 100, 6)
        add("TT", v, raw, q, f"p. 21, Table 1, row '{label}'", metric=metric, unit="share",
            normalization=f"{raw} -> {v}", fy="2029-30", pkey=PNIC,
            cond={"income_group": grp, "income_concept": INC, "year_note": "no year printed with the table; staged with the 2030 costing"},
            hint=H_PNIC, table=T1, column=col)
P22 = "p. 22, section 3.3"
IQ = "this would raise up to £3 billion, £0.6 billion and £0.4 billion"
for v, raw, comp in [(3, "£3 billion", "rental income"), (0.6, "£0.6 billion", "savings income outside ISAs"),
                     (0.4, "£0.4 billion", "other non-dividend investment income")]:
    add("TT", bn(v), raw, IQ, P22, metric="revenue_change", unit="gbp", normalization="£ billion × 1e9",
        fy="2029-30", pkey=INIC, kind="range_high",
        cond={"basis": "static", "sign_convention": YIELD, "income_type": comp, "year_note": YEARS},
        hint=H_INIC, note="Static: 'naturally at the upper bound of the actual expected revenue' (fn 13).")
for v, raw, comp, grp, q in [
    (0.45, "45%", "rental income", "decile_10", "45% of additional revenue would come from the top 10% whilst 6%"),
    (0.06, "6%", "rental income", "bottom_50pct", "45% of additional revenue would come from the top 10% whilst 6%"),
    (0.69, "69%", "savings income outside ISAs", "decile_10", "These figures are 69%/4% for savings income and 74%/4% for other"),
    (0.04, "4%", "savings income outside ISAs", "bottom_50pct", "These figures are 69%/4% for savings income and 74%/4% for other"),
    (0.74, "74%", "other non-dividend investment income", "decile_10", "These figures are 69%/4% for savings income and 74%/4% for other"),
    (0.04, "4%", "other non-dividend investment income", "bottom_50pct", "These figures are 69%/4% for savings income and 74%/4% for other"),
]:
    add("TT", v, raw, q, P22, metric="revenue_share", unit="share", normalization=f"{raw} -> {v}", fy="2029-30",
        pkey=INIC, cond={"basis": "static", "income_type": comp, "income_group": grp, "year_note": NOYEAR}, hint=H_INIC)

CCC = dict(geography="England")
add("TT", 0.1, "fewer than one in ten", "fewer than one in ten employees with eligible children responded to the cliff-edge",
    "p. 23, section 3.4", pmetric="behavioural_response_share", unit="share", normalization="one in ten -> 0.1",
    fy="2021-22", kind="range_high", bclass="administrative_fact",
    cond={"basis": "outturn", "subgroup": "employees with eligible children", "year_note": YEARS},
    note="Current-policy behaviour in 2022 data; context, no measure key.", **CCC)
add("TT", 0.3, "about three in ten", "rising to about three in ten amongst the self-employed and owner-managers",
    "p. 23, section 3.4", pmetric="behavioural_response_share", unit="share", normalization="three in ten -> 0.3",
    fy="2021-22", bclass="administrative_fact",
    cond={"basis": "outturn", "subgroup": "self-employed and owner-managers with eligible children", "year_note": YEARS},
    note="Current-policy behaviour in 2022 data; context, no measure key.", **CCC)
add("TT", 0.1, "one in ten", "Only one in ten were more than £4,000 worse off",
    "p. 24, section 3.4", metric="affected_share", unit="share", normalization="one in ten -> 0.1", fy="2021-22",
    bclass="administrative_fact",
    cond={"basis": "outturn", "measure_type": "parents more than £4,000 worse off from just crossing £100,000", "year_note": YEARS},
    note="Current-policy context, no measure key.", **CCC)
add("TT", 0.8, "eight in ten", "that proportion will rise to eight in ten parents",
    "p. 24, section 3.4", metric="affected_share", unit="share", normalization="eight in ten -> 0.8", fy="2029-30",
    cond={"basis": "forecast", "scenario": "if the cliff-edge remains in place",
          "measure_type": "parents more than £4,000 worse off from just crossing £100,000",
          "year_note": "'by the end of this parliament'; staged at 2029-30, the report's 2030"},
    conf="medium", note="Current-policy projection; context, no measure key.", **CCC)
for v, raw, scen, q in [
    (0.06, "about 6%", "income below £100,000", "the share of parents whose partner is not in work is about 6%"),
    (0.09, "about 9%", "income just over £100,000", "but once income crosses the threshold it rises to about 9%"),
]:
    add("TT", v, raw, q, "p. 24, section 3.4", pmetric="partner_not_in_work_share", unit="share",
        normalization=f"{raw} -> {v}", fy="2021-22", bclass="administrative_fact",
        cond={"basis": "outturn", "subgroup": f"parents with {scen}", "year_note": YEARS},
        note="Current-policy context, no measure key.", **CCC)
add("TT", mn(520), "£520 million", "is likely to be around £520 million in 2028", "p. 25, section 3.4",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2027-28", pkey=CC_REMOVE,
    cond={"basis": "post_behavioural", "scenario": "central", "sign_convention": COST, "year_note": YEARS},
    hint=H_CC, note="Repeats the September 2026 childcare report (Table 4.2, in data/externals/centax-childcare-100k.json, #207).", **CCC)
add("TT", 0.33, "one third (33%)", "one third (33%) of parents whose incomes were between £100,000 and £120,000",
    "p. 26, section 3.4", metric="participation_rate", unit="share", normalization="33% -> 0.33", fy="2021-22",
    bclass="administrative_fact",
    cond={"basis": "outturn", "subgroup": "parents with year-end incomes between £100,000 and £120,000",
          "program": "free childcare entitlement (claimed and received some)", "year_note": YEARS},
    note="Current-policy context, no measure key.", **CCC)
OPT = {"basis": "post_behavioural", "scenario": "central", "sign_convention": COST, "costing_basis": "actual ANI", "year_note": YEARS}
add("TT", mn(210), "£210 million", "This would cost around £210 million in 2030", "p. 26, section 3.4, first bullet",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2029-30", pkey=CC_15H, cond=OPT,
    hint="remove the £100,000 threshold for the first 15 hours of childcare for under-3s", **CCC)
for v, thr in [(100, "£125,000"), (250, "£150,000")]:
    add("TT", mn(v), f"£{v} million", "£125,000 or £150,000 would cost around £100 million or £250 million",
        "p. 26, section 3.4, second bullet", metric="revenue_change", unit="gbp", normalization="£ million × 1e6",
        fy="2029-30", pkey=CC_RAISE, cond={**OPT, "threshold": thr},
        hint=f"raise the free childcare entitlement threshold to {thr}", **CCC)
for v, raw, rate, q, norm in [
    (mn(320), "£320 million", "8p", "would cost around £320 million by 2030", "£ million × 1e6"),
    (-mn(20), "£20 million", "28p", "estimated to actually raise £20 million by replacing the current policy",
     "'raise £20 million' -> -2e7 under positive = cost"),
    (mn(80), "£80 million", "18p", "deducting 18 pence is estimated to cost £80 million", "£ million × 1e6"),
]:
    add("TT", v, raw, q, "p. 26, section 3.4, third bullet", metric="revenue_change", unit="gbp",
        normalization=norm, fy="2029-30", pkey=CC_TAPER, cond={**OPT, "taper_rate": f"{rate} per £1 earned over £100,000"},
        hint=f"taper the withdrawal of free childcare above £100,000 at {rate} per pound", **CCC)

# === 3. Capital Gains Tax on Entrepreneurs: Unicorn Relief (8 October 2026) =

UR9 = "p. 10, footnote 9"
add("UR", bn(19.7), "£19.7 billion", "estimate it would raise £19.7 billion in 2030", UR9,
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2029-30", pkey=CGT,
    cond={"basis": "post_behavioural", "scenario": "central", "sign_convention": YIELD, "year_note": YEARS},
    hint=H_CGT, note="Repeats Taxes at the top (Advani, Hughson and Summers 2026).")
add("UR", bn(14), "£14 billion", "previously estimated it would raise £14 billion in 2026", UR9,
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2025-26", pkey=CGT,
    cond={"basis": "post_behavioural", "sign_convention": YIELD,
          "scenario": "Advani, Lonsdale and Summers (2024) estimate", "year_note": YEARS},
    hint=H_CGT, note="CenTax's earlier estimate.")
add("UR", bn(10), "just under £10 billion",
    "would reduce the ALS2024 estimate to just under £10 billion on a like-for-like basis", UR9,
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2025-26", pkey=CGT, kind="range_high",
    cond={"basis": "post_behavioural", "sign_convention": YIELD,
          "scenario": "the 2024 estimate adjusted for CGT rate changes since, on the 2024 baseline",
          "year_note": "like-for-like with the 2024 estimate for 2026; " + YEARS},
    hint=H_CGT, conf="medium", note="CenTax's adjustment of its 2024 estimate.")


# === review fixes, 3 November 2026 ========================================
# verify-thinktanks-a.md, uk_centax (PR #231). Explicit edits on top of the
# rows above; no primary was re-opened (the session's network policy refused
# centax.org.uk), and no printed value changes.

def _row(i, value_raw):
    """Row i (0-based, the reviewed order), checked by its printed value."""
    r = ROWS[i]
    assert r["value_raw"] == value_raw, (i, r["value_raw"], value_raw)
    return r

# Finding 1: p. 22's £3bn, £0.6bn and £0.4bn are the parts of key finding
# 7's "up to £4 billion" (row 24); tag them so an ingest never adds them to
# it (rule 9, by analogy for an option key).
for _i, _raw in ((84, "£3 billion"), (85, "£0.6 billion"), (86, "£0.4 billion")):
    _c = _row(_i, _raw)["conditions"]
    _c["row_type"] = "measure_component"
    _c["component"] = _c["income_type"]

# Finding 2: row 2's derivation (Table 6.3 row 3: 1,355, 1,605 and 1,815)
# was confirmed against uk_hmt_redbook's staged Table 6.3 cells; no edit.

# Finding 3: record the #207 file's differences in row 27's note.
_r = _row(27, "11,980")
_r["note"] += (" The #207 file (data/externals/centax-childcare-100k.json) holds 16,280 for 2030's"
               " central 'Number Bunching, Before Removal'; this may be a different concept, or"
               " CenTax may differ between its two publications. Neither is corrected.")

# Finding 4 (optional, applied): values are not re-signed (AB2025 README);
# "raise £20 million" is a yield of £20 million.
_r = _row(105, "£20 million")
_r["value"] = 20000000
_r["conditions"]["sign_convention"] = YIELD
_r["normalization"] = "£ million × 1e6"

# Finding 5 (optional, applied): a 25th-percentile EATR is an average tax
# rate, as rows 7-15 stage it.
_r = _row(18, "23%")
_r["metric"] = "average_tax_rate"
_r.pop("proposed_metric")


# === output and --verify ====================================================

def manifest_lines():
    keys = ["url", "title", "date", "publisher", "sha256", "bytes", "doc_type", "access", "retrieved", "note"]
    return "".join(json.dumps({k: p[k] for k in keys}, ensure_ascii=False) + "\n" for p in PUBS.values())


def claims_bytes():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in ROWS:
            gz.write((json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    return buf.getvalue()


class _Text(HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "br", "td", "th", "section", "article"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def _norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def verify():
    texts, bad = {}, 0
    for k, p in PUBS.items():
        f = PRIMARIES / p["file"]
        if not f.exists():
            continue
        b = f.read_bytes()
        assert hashlib.sha256(b).hexdigest() == p["sha256"], f"{k}: sha256 mismatch"
        assert len(b) == p["bytes"], f"{k}: byte count"
        if p["doc_type"] == "html":
            t = _Text()
            t.feed(b.decode("utf-8"))
            texts[k] = _norm("".join(t.out))
        else:
            texts[k] = _norm(subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True, check=True).stdout)
    for idx, pub in CHECKS:
        if pub in texts and _norm(ROWS[idx]["quote"]) not in texts[pub]:
            print(f"row {idx}: quote not in {pub}: {ROWS[idx]['quote']!r}")
            bad += 1
    print(f"verify: {len(ROWS)} rows, {len(texts)} primaries read, {bad} problems")
    return bad


if __name__ == "__main__":
    (HERE / "manifest.jsonl").write_text(manifest_lines(), encoding="utf-8")
    data = claims_bytes()
    (HERE / "claims_staged.jsonl.gz").write_bytes(data)
    print(f"{len(ROWS)} rows, sha256 {hashlib.sha256(data).hexdigest()}")
    if "--verify" in sys.argv[1:]:
        sys.exit(1 if verify() else 0)
