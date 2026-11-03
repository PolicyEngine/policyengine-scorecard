#!/usr/bin/env python3
"""Stage Tax Policy Associates' Autumn Budget 2026 claims (#230, family uk_tpa).

The rows are data in this file. Running it rewrites manifest.jsonl and
claims_staged.jsonl.gz byte for byte:

    python sources/harvest-uk-ab2026-2026-10-29/uk_tpa/stage.py

`--verify` also checks, where the primaries are present under
.ab2026-primaries/uk_tpa/ (git-ignored, hashed not vendored):

- that each primary hashes to its manifest sha256;
- that every quote occurs in its primary (HTML text, or the compact JSON of a
  chart data file) and carries its value_raw;
- that every chart row's value is the value at its JSON path;
- that each TPA group's Table 6.1 lines, read from uk_hmt_tables, reproduce
  TPA's printed group values (exactly for the by-year and by-tax charts; for
  the real-terms by-measure chart, through deflators fitted to its
  single-measure bars).
"""

import gzip
import hashlib
import io
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIMARIES = ROOT / ".ab2026-primaries" / "uk_tpa"
HMT_TABLES = HERE.parent / "uk_hmt_tables" / "claims_staged.jsonl.gz"
SOURCE = "tax_policy_associates"
EVENT = "autumn_budget_2026"
TPA = "Tax Policy Associates"
YIELD = "positive = yield to the Exchequer"

# --- primaries (manifest.jsonl, in reading order) ---------------------------

PUBS = {
    "ART": {
        "url": "https://taxpolicy.org.uk/2026/10/28/budget-2026-what-it-means/",
        "title": "Budget 2026 – what it means",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "9d8031655aa08411da8350d9dc8680dea53b80aea1e04f2c3a0b5ff009fc350d",
        "bytes": 201933,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "article:published_time 2026-10-28T15:51:19+00:00, article:modified_time 2026-10-29T09:59:59+00:00; fetched 2026-10-29T16:17Z (curl, browser User-Agent, HTTP 200). The seven charts are ECharts embeds whose data files are the next seven primaries. Reader comments under the article are not TPA's and are not staged.",
        "file": "budget-2026-what-it-means.html",
    },
    "EVENT": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/charts/budget_tax_rises_by_event.json",
        "title": "Who's responsible for each year's tax rises? (chart data, budget_tax_rises_by_event.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "62d64a909445ce6122171f676ef8739bd830a3e64e1fdabe6b43028434a686a3",
        "bytes": 9965,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON named in the article's data-json attribute (first chart, 'The big picture'); £bn in 2026 money; fetched 2026-10-29T16:19Z. doc_type flourish_json is the nearest enum for a chart-data file, as in the AB2025 uk_tpa family.",
        "file": "budget_tax_rises_by_event.json",
    },
    "GOV": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/charts/tax_take_by_government.json",
        "title": "Tax as a % of GDP - who added to the tax take? (chart data, tax_take_by_government.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "b13087894131a927a0833abd54494212a4eb48f0fdf1a1a3e2b772e74bac79eb",
        "bytes": 4916,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON (second chart, method in the article's footnote 3); % of GDP; fetched 2026-10-29T16:19Z.",
        "file": "tax_take_by_government.json",
    },
    "GDP": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/charts/budget_2026_tax_gdp_impact.json",
        "title": "Impact of the 2026 Budget on tax as a % of GDP (chart data, budget_2026_tax_gdp_impact.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "a96c8f8f29b1e0e7343483e22929631231556c65e8cdfa05b4e0449e639fac36",
        "bytes": 2738,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON (third chart, method in footnote 4: Table 6.1 'Total tax policy decisions' over OBR nominal GDP, EFO Table A.3); fetched 2026-10-29T16:19Z.",
        "file": "budget_2026_tax_gdp_impact.json",
    },
    "BYTAX": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/charts/budget_2026_chart_by_tax_2027_28.json?v=20261028-2",
        "title": "Budget 2026 tax measures by tax, 2027/28 (chart data, budget_2026_chart_by_tax_2027_28.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "dcf10b6e82b0848a146578bb68328c4bfdcbdf461ae7e334d3c0db0fc233197b",
        "bytes": 4472,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON (fourth chart, footnote 5); URL as named in the article, cache-buster ?v=20261028-2; fetched 2026-10-29T16:19Z.",
        "file": "budget_2026_chart_by_tax_2027_28.json",
    },
    "BYYEAR": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/charts/budget_2026_chart_by_year_v2.json?v=20261028-2",
        "title": "Budget tax changes (grouped by year) (chart data, budget_2026_chart_by_year_v2.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "db22d5e01bb59ba7f1b5df304813c485a5f66d9731de1827f56475bdc0abfe1f",
        "bytes": 5647,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON (fifth chart, footnote 6); cache-buster ?v=20261028-2; fetched 2026-10-29T16:19Z.",
        "file": "budget_2026_chart_by_year_v2.json",
    },
    "BYMEAS": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/charts/budget_2026_chart_by_measure_total_real.json",
        "title": "Budget 2026 measures: total over 2026/27 to 2031/32 (chart data, budget_2026_chart_by_measure_total_real.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "7355f24b6b8a620ccc624200468dd1da43389d760ebc2bf89d1c486a011cf1cb",
        "bytes": 6793,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON (sixth chart, footnote 7); £bn at 2026/27 prices; fetched 2026-10-29T16:19Z.",
        "file": "budget_2026_chart_by_measure_total_real.json",
    },
    "BANK": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/bank_tax/bank-tax-compare-uk-budget-2026.json?v=20261028-3",
        "title": "Investment bank: tax as % of profit (chart data, bank-tax-compare-uk-budget-2026.json)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "7a8454d612b6e46ba5abd53d6b4d40146dd57e0741452f627183c71941ad2a20",
        "bytes": 6595,
        "doc_type": "flourish_json",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "ECharts option JSON (seventh chart, 'Bank tax'); cache-buster ?v=20261028-3; fetched 2026-10-29T16:19Z.",
        "file": "bank-tax-compare-uk-budget-2026.json",
    },
    "CB": {
        "url": "https://taxpolicy.org.uk/wp-content/assets/child_benefit_budget_2026.png",
        "title": "TPA tax calculator screenshot: marginal rate at £70,000 with child benefit, current rules 2026/27 v Budget 2027/28 (child_benefit_budget_2026.png)",
        "date": "2026-10-28",
        "publisher": TPA,
        "sha256": "e69c25ad27fbd19b398ab9bd86c5798d3e723969243442a614801b895ab994a1",
        "bytes": 172693,
        "doc_type": "png",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Image linked from the article's footnote 1; the values are printed text in the calculator's tooltip panel, read from the image; fetched 2026-10-29T16:19Z.",
        "file": "child_benefit_budget_2026.png",
    },
    "CALC": {
        "url": "https://taxpolicy.org.uk/uk-tax-calculator/",
        "title": "The UK tax calculator that shows you what you’re really paying",
        "date": "2026-10-25",
        "publisher": TPA,
        "sha256": "69a72c68640f3b2ff74d585aeea28ecda0897308dbc640c8ed34d596c8c09f62",
        "bytes": 249216,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Descriptor only, no rows (scope in NOTES.md). article:published_time 2026-10-25T08:00:00+00:00, article:modified_time 2026-10-28T15:26:49+00:00 ('Updated for the 28 October 2026 Budget'); fetched 2026-10-29T16:19Z.",
        "file": "uk-tax-calculator.html",
    },
}

# Table 6.1 lines and their registry keys, for the measures TPA names singly.
KEY = {
    2: "ab2026__electricity_vat_zero_rate_to_july_2027",
    3: "ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred",
    5: "ab2026__mileage_allowance_payments_55p",
    15: "ab2026__trading_allowance_3000",
    26: "ab2026__founders_relief_cgt",
    44: "ab2026__uk_export_finance_defence_capacity",
    45: "ab2026__hmrc_tax_gap_package",
    46: "ab2026__online_marketplace_liability_uk_businesses",
    49: "ab2026__distributions_framework_modernised",
    52: "ab2026__pension_tax_allowance",
    54: "ab2026__foreign_sovereign_investments_taxation",
    55: "ab2026__bank_surcharge_6pc_temporary",
    56: "ab2026__machine_games_duty_higher_stake_25pc",
    58: "ab2026__writing_down_allowance_12pc_and_fya_50pc",
    59: "ab2026__private_hire_operators_vat_full_fare",
    60: "ab2026__badr_lifetime_limit_500000",
    61: "ab2026__property_income_rates_plus_2pp",
    62: "ab2026__savings_income_rates_plus_2pp",
    68: "ab2026__foreign_permanent_establishment_exemption_mandatory",
    86: "ab2026__company_car_tax_rates_2030_31",
    96: "ab2026__ets_energy_from_waste_delay",
}
TOTAL_TAX = "ab2026__package_total_tax_policy_decisions"
SP = "ab2026__package_property_and_savings_income_rates"  # lines 61, 62

# TPA's multi-line groups: proposed key -> Table 6.1 lines (NOTES.md).
GROUPS = {
    "ab2026__package_tpa_savings_property_income_and_cash_isa": (11, 61, 62),
    "ab2026__package_tpa_temporary_vat_and_fuel_cuts": (2, 3, 18, 65, 66),
    "ab2026__package_tpa_fuel_duty_red_diesel_and_hgv_ved": (3, 18, 65),
    "ab2026__package_tpa_business_rates": (12, 13, 14, 57, 76, 80),
    "ab2026__package_tpa_energy_and_environment": (17, 69, 71, 90, 96),
    "ab2026__package_tpa_other_income_tax": (5, 15, 28, 52, 53, 86, 94),
    "ab2026__package_tpa_other_vat": (36, 46, 51, 59, 88, 89),
    "ab2026__package_tpa_other_corporate_tax": (49, 50, 54, 68, 97),
    "ab2026__package_tpa_other_by_year": (10, 16, 19, 26, 44, 56, 60, 77, 78, 79, 93, 95, 98),
    "ab2026__package_tpa_tariffs": (10, 16, 77, 78, 95),
    "ab2026__package_tpa_cgt_founders_relief_and_badr": (26, 60),
    "ab2026__package_tpa_other_by_tax_2027_28": (17, 19, 44, 56, 69, 71, 79, 90, 93, 96, 98),
    "ab2026__package_tpa_other_by_measure": (
        11, 17, 18, 19, 28, 36, 50, 51, 53, 65, 66, 69, 71, 79, 88, 89, 90, 93, 94, 97, 98,
    ),
    SP: (61, 62),
}

FYS6 = ["2026-27", "2027-28", "2028-29", "2029-30", "2030-31", "2031-32"]
FYS7 = ["2024-25", "2025-26"] + FYS6[:5]
FYS_GOV = ["2025-26"] + FYS6[:5]

ROWS = []
CHECKS = []  # (row index, pub, json path or None) for --verify


def bn(x):
    return round(x * 1e9)


def mn(x):
    return round(x * 1e6)


def add(
    pub, value, value_raw, quote, locator, *,
    metric=None, pmetric=None, unit=None, punit=None, normalization="as printed",
    fy=None, period=None, time_basis=None, key=None, pkey=None,
    attribution="own", bclass="different_model", model="arithmetic", kind="point",
    cond=None, hint=None, table=None, column=None, note="", conf="high", path=None,
    geography="UK",
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
        "source": SOURCE,
        "source_model": model,
        "value": value,
        "value_raw": value_raw,
        "normalization": normalization,
        "value_kind": kind,
        "period": period,
        "time_basis": time_basis,
        "conditions": c,
        "reform_hint": hint,
        "measure_key": key,
        "attribution": attribution,
        "benchmark_class": bclass,
        "baseline_policy": None,
        "publication": {
            "title": p["title"],
            "url": p["url"],
            "date": p["date"],
            "publisher": p["publisher"],
            "primary_sha256": p["sha256"],
            "locator": locator,
            "access": p["access"],
        },
        "source_table": table,
        "source_column": column,
        "quote": quote,
        "note": note,
        "parse_confidence": conf,
        "status": "ok",
    }
    if metric:
        r["metric"] = metric
    if pmetric:
        r["proposed_metric"] = pmetric
    if unit:
        r["unit_concept"] = unit
    if punit:
        r["proposed_unit"] = punit
    assert value_raw in quote, (value_raw, quote)
    CHECKS.append((len(ROWS), pub, path))
    ROWS.append(r)


def hmt_restated(**c):
    return {"basis": "forecast", "scoring_method": "final", "sign_convention": YIELD, **c}


# === 1. The article =========================================================

A = "ART"
add(A, bn(123), "£123bn",
    "by 2030/31 we will be paying £123bn more tax (in today’s money)",
    "'The big picture', paragraph after the % of GDP chart",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2030-31",
    cond={"basis": "forecast", "sign_convention": YIELD, "price_basis": "today's money (2026)",
          "measure_type": "extra tax in 2030-31 from tax changes since 2021, against no tax changes since 2021",
          "derived_from": "OBR costings of each tax measure announced since 2020, summed by TPA (footnote 3 method)"},
    hint="all tax changes since 2021 (Conservative Budgets, Starmer/Reeves Budgets and this Budget)",
    note="Context figure spanning many fiscal events, so no AB2026 key. The text says 'since 2021'; footnote 3 says measures 'announced since March 2020'. The chart data (budget_tax_rises_by_event.json, 'Net tax rise') prints £122.9bn for 2030-31.")
add(A, 0.4, "About two-fifths",
    "About two-fifths of that comes from Conservative Budgets",
    "'The big picture', paragraph after the % of GDP chart",
    metric="revenue_share", unit="share", normalization="two-fifths -> 0.4", fy="2030-31",
    cond={"basis": "forecast", "subgroup": "Conservative Budgets",
          "measure_type": "share of the £123bn extra tax in 2030-31",
          "derived_from": "OBR costings of each tax measure announced since 2020, grouped by government (footnote 3)"},
    hint="tax changes in Conservative Budgets since 2021", kind="central")
add(A, bn(6), "about £6bn",
    "Only about £6bn comes from today’s Budget",
    "'The big picture', paragraph after the % of GDP chart",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2030-31", key=TOTAL_TAX,
    cond={"basis": "forecast", "sign_convention": YIELD, "price_basis": "today's money (2026)",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 total tax policy decisions, in 2026 money"},
    hint="the tax measures of today's Budget",
    note="TPA's real-terms re-expression of Table 6.1 (£6,495m cash in 2030-31); the chart data budget_tax_rises_by_event.json prints £5.9bn for 'Healey Oct 2026 Budget' in 2030-31. Arithmetic on HM Treasury's costings, not an independent estimate.")
add(A, bn(0.7), "about £0.7bn",
    "In 2027/28, the tax measures almost cancel out, adding only about £0.7bn",
    "'The Budget changes', first paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2027-28", key=TOTAL_TAX,
    attribution="restated", model="hmt_costing_obr_certified",
    cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1"),
    hint="the tax measures of today's Budget",
    note="Rounds HM Treasury's total tax policy decisions for 2027-28 (£695m); footnote 5 says TPA's groups sum to £700m.")
add(A, bn(19), "£19bn",
    "£19bn in real terms over six years",
    "'The Budget changes', second paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2031-32", key=TOTAL_TAX,
    kind="cumulative",
    cond={"basis": "forecast", "sign_convention": YIELD, "horizon": "2026-27 to 2031-32 (cumulative)",
          "price_basis": "2026-27 prices (footnote 7)",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 tax lines, deflated by the OBR's October 2026 CPI forecast"},
    hint="the tax measures of today's Budget, phased in",
    note="Footnote 7 gives the unrounded total, £19.1bn. Arithmetic on HM Treasury's costings, not an independent estimate.")
add(A, mn(160), "£160m",
    "The savings and property rise brings in just £160m next year",
    "'The Budget changes', third paragraph",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2027-28", pkey=SP,
    cond={"basis": "forecast", "sign_convention": YIELD, "table_61_lines": "61, 62",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 lines 61 and 62"},
    hint="the further 2ppt rise in property and savings income tax rates",
    note="'Next year' is 2027-28 (article of 28 October 2026). Equals Table 6.1 lines 61 + 62 for 2027-28 (£35m + £125m).")
add(A, bn(1.1), "£1.1bn",
    "brings in just £160m next year but £1.1bn in 2028/29",
    "'The Budget changes', third paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2028-29", pkey=SP,
    cond={"basis": "forecast", "sign_convention": YIELD, "table_61_lines": "61, 62",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 lines 61 and 62"},
    hint="the further 2ppt rise in property and savings income tax rates",
    note="Table 6.1 lines 61 + 62 sum to £1,130m in 2028-29.")
add(A, bn(1.5), "about £1.5bn",
    "That raises about £1.5bn over fifteen months",
    "'The headline tax increases' > 'Bank tax'",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2028-29", key=KEY[55],
    kind="cumulative", conf="medium",
    cond={"basis": "forecast", "sign_convention": YIELD,
          "horizon": "fifteen months from 1 January 2027 (Table 6.1 line 55 yields in 2026-27 to 2028-29)",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 line 55, summed over its three years",
          "year_note": "TPA states no year; staged at 2028-29, the last year of yield in Table 6.1 line 55"},
    hint="temporary rise in the bank surcharge from 3% to 6% for fifteen months",
    note="Table 6.1 line 55 sums to £1,475m (£305m + £950m + £220m). Arithmetic on HM Treasury's costing.")
add(A, bn(1), "about £1bn",
    "This also raises about £1bn",
    "'The headline tax increases' > 'Savers and landlords', first paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2028-29", pkey=SP, conf="medium",
    cond={"basis": "forecast", "sign_convention": YIELD, "table_61_lines": "61, 62",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 lines 61 and 62",
          "year_note": "no year stated ('it will be permanent'); staged at 2028-29, the first full year of the rise"},
    hint="a further two points on savings and property income tax rates from April 2027",
    note="An annual round number; Table 6.1 lines 61 + 62 give £955m to £1,130m a year from 2028-29.")
add(A, 0.84, "84%",
    "The government says “84% of income tax payers will be unaffected”",
    "'The headline tax increases' > 'Savers and landlords', second paragraph",
    pmetric="unaffected_share", unit="share", normalization="84% -> 0.84", fy="2027-28", pkey=SP,
    attribution="restated", model="not_stated",
    cond={"originator": "HM Treasury, Budget 2026", "denominator": "income tax payers",
          "table_61_lines": "61, 62"},
    hint="the further 2ppt rise in property and savings income tax rates",
    note="HM Treasury's statement, quoted by TPA (Budget 2026 para 2.50 in the uk_hmt_redbook family). The share is of taxpayers unaffected, not affected.")

PV5 = {"discount_rate": "5% a year (footnote 12)"}
NEW = "new investment that gets the first-year allowance"
OLD = "second-hand assets, cars and existing pool balances (writing-down allowances only)"
R_AFTER = "50% first-year allowance and 12% writing-down allowance (this Budget)"
R_BEFORE = "40% first-year allowance and 14% writing-down allowance (before this Budget)"
R_PRE = "18% writing-down allowance alone (before Labour's changes)"
for v, raw, quote, regime, key in [
    (0.85, "85%", "the tax relief is worth 85% of the cost, up from 84%", R_AFTER, KEY[58]),
    (0.84, "84%", "the tax relief is worth 85% of the cost, up from 84%", R_BEFORE, None),
    (0.82, "82%", "and more than the 82% it was worth before Labour’s changes", R_PRE, None),
]:
    add(A, v, raw, quote, "'Writing-down allowance', paragraph after the Red Book excerpt",
        pmetric="capital_allowance_present_value", unit="share",
        normalization=f"{raw} -> {v}", period=2027, time_basis="point_in_time", key=key,
        cond={**PV5, "subgroup": NEW, "regime": regime,
              "measure_type": "present value of capital allowances as a share of the cost"},
        hint=regime if key else None,
        note="TPA's 'rough numbers'; footnote 12 gives the unrounded values (85.3%, 84.2%, 82.2%)."
        + ("" if key else " The regime before this Budget, so no measure key."))
for v, raw, regime, key in [
    (0.77, "77%", "14% writing-down allowance (before this Budget)", None),
    (0.74, "74%", "12% writing-down allowance (this Budget)", KEY[58]),
]:
    add(A, v, raw, "For those, the relief falls from 77% to 74% of the cost",
        "'Writing-down allowance', paragraph after the subscription box",
        pmetric="capital_allowance_present_value", unit="share",
        normalization=f"{raw} -> {v}", period=2027, time_basis="point_in_time", key=key,
        cond={**PV5, "subgroup": OLD, "regime": regime,
              "measure_type": "present value of capital allowances as a share of the cost"},
        hint=regime if key else None,
        note="Footnote 12 gives 77.4% and 74.1%." + ("" if key else " The regime before this Budget, so no measure key."))
add(A, bn(1), "about £1bn a year",
    "All of this raises, net, about £1bn a year in the medium term",
    "'Writing-down allowance', last paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2029-30", key=KEY[58],
    attribution="restated", model="hmt_costing_obr_certified", conf="medium",
    cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 line 58",
                      year_note="'in the medium term'; no year stated; staged at 2029-30"),
    hint="writing-down allowance cut to 12% and first-year allowance raised to 50%",
    note="Rounds Table 6.1 line 58 (£1,040m to £1,120m a year from 2028-29).")

PTA_HINT = "Pension Tax Allowance: no income tax for pensioners with total income up to the full new State Pension, withdrawn at £1 for every £3 above it, 2027-28 to 2029-30"
add(A, 93, "£93",
    "prevent pensioners being chased by HMRC for £93",
    "'Pension tax', third paragraph",
    metric="tax_liability", unit="gbp", fy="2027-28", key=KEY[52], conf="medium",
    cond={"scenario": "without the Pension Tax Allowance",
          "subgroup": "pensioner whose income just exceeds the Personal Allowance through the State Pension",
          "measure_type": "small income tax bill the allowance removes",
          "allowance_maximum": "up to £94 a year (as printed in the previous paragraph)"},
    hint=PTA_HINT,
    note="Single-person worked example (mode 3). The paragraph before gives the allowance as 'up to £94 a year', a design parameter kept in conditions (README rule 8).")
add(A, 53, "53%",
    "meaning a 53% marginal rate for pensioners on about £13,000",
    "'Pension tax', third paragraph",
    pmetric="marginal_tax_rate", unit="percent", fy="2027-28", key=KEY[52],
    cond={"subgroup": "pensioners on about £13,000, in the allowance's withdrawal band",
          "rate_components": "20p of tax plus 33p of lost allowance per £1",
          "withdrawal_band": "£282 (as printed)", "allowance_maximum": "up to £94 a year (as printed)",
          "threshold": "the full new State Pension, £13,036.40 in 2027/28"},
    hint=PTA_HINT, note="TPA's arithmetic from the basic rate and the taper. The £282 band and the £94 maximum are the allowance's design (README rule 8) and are kept in conditions, not staged as rows.")
add(A, bn(0.5), "about £0.5bn a year",
    "That raises about £0.5bn a year",
    "'Other changes' > 'Foreign branches', second paragraph",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2027-28", key=KEY[68],
    attribution="restated", model="hmt_costing_obr_certified", conf="medium",
    cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 line 68",
                      year_note="no year stated; staged at 2027-28, the first year footnote 15 cites"),
    hint="foreign branch exemption made mandatory from January 2027",
    note="Rounds Table 6.1 line 68; footnote 15 prints £480m in 2027/28, then £450m to £495m a year.")

# --- footnotes ---
F2 = "footnote 2"
add(A, 33, "33%", "The UK’s tax burden was around 33% of GDP in 2019/20", F2,
    pmetric="tax_to_gdp_ratio", punit="percent_of_gdp", fy="2019-20",
    attribution="restated", model="administrative_data", bclass="administrative_fact",
    cond={"basis": "outturn", "originator": "not named in the footnote (OBR/ONS outturn)"},
    note="Context level; restated.")
add(A, 38.5, "38.5%", "is forecast to reach 38.5% by 2030/31", F2,
    pmetric="tax_to_gdp_ratio", punit="percent_of_gdp", fy="2030-31",
    attribution="restated", model="obr_efo_forecast",
    cond={"basis": "forecast", "originator": "OBR forecast (not named in the footnote)"},
    note="Context level; restated. Matches the chart data's 2030-31 'Tax take' (38.5%).")
add(A, 14, "14 percentage points",
    "The pandemic increased government debt by around 14 percentage points of GDP", F2,
    pmetric="public_sector_net_debt_change", unit="percentage_points", fy="2020-21",
    attribution="restated", model="administrative_data", bclass="administrative_fact",
    cond={"basis": "outturn", "horizon": "2018-19 to 2020-21", "denominator": "GDP",
          "originator": "not named in the footnote"},
    note="Context; 'government debt' as printed (no debt measure named).")
add(A, bn(300), "over £300bn", "the direct pandemic support measures costing over £300bn", F2,
    pmetric="programme_cost", unit="gbp", normalization="£ billion × 1e9", fy="2020-21", kind="range_low",
    attribution="restated", model="administrative_data", bclass="administrative_fact", conf="medium",
    cond={"basis": "outturn", "program": "direct pandemic support measures",
          "year_note": "no year stated; the support ran mainly in 2020-21; staged there",
          "originator": "not named in the footnote"},
    note="Context; restated.")
add(A, bn(110), "£110 billion", "By 2025/26, debt interest spending was £110 billion", F2,
    pmetric="debt_interest_cost", unit="gbp", normalization="£ billion × 1e9", fy="2025-26",
    attribution="restated", model="administrative_data", bclass="administrative_fact",
    cond={"basis": "outturn", "originator": "not named in the footnote"}, note="Context; restated.")
add(A, 2100000, "2.1 million",
    "Working-age disability benefit caseloads increased from 2.1 million in November 2019", F2,
    metric="caseload", unit="persons", normalization="million × 1e6", period=2019, time_basis="point_in_time",
    attribution="restated", model="administrative_data", bclass="administrative_fact",
    cond={"subgroup": "working-age disability benefit claimants", "date": "November 2019",
          "originator": "DWP statistics (the footnote links OBR's paragraph 5.30)"},
    note="Context; restated.")
add(A, 3200000, "3.2 million", "to 3.2 million in November 2024", F2,
    metric="caseload", unit="persons", normalization="million × 1e6", period=2024, time_basis="point_in_time",
    attribution="restated", model="administrative_data", bclass="administrative_fact",
    cond={"subgroup": "working-age disability benefit claimants", "date": "November 2024",
          "originator": "DWP statistics (the footnote links OBR's paragraph 5.30)"},
    note="Context; restated.")
F5Q = "The groups sum to £700m against the Red Book’s total of £695m"
add(A, mn(700), "£700m", F5Q, "footnote 5",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2027-28", key=TOTAL_TAX,
    cond={"basis": "forecast", "sign_convention": YIELD,
          "measure_type": "sum of TPA's groups of the Table 6.1 tax rows",
          "derived_from": "HM Treasury Budget 2026 Table 6.1, tax rows (53 lines)"},
    hint="the tax measures of today's Budget",
    note="Arithmetic on HM Treasury's costings; the 53 tax lines of Table 6.1 sum to £700m in 2027-28.")
add(A, mn(695), "£695m", F5Q, "footnote 5",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2027-28", key=TOTAL_TAX,
    attribution="restated", model="hmt_costing_obr_certified",
    cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 total tax policy decisions"),
    hint="the tax measures of today's Budget")
F7Q = "The bars add up to the real-terms total of £19.1bn (£21.0bn in cash)"
F7C = {"basis": "forecast", "sign_convention": YIELD, "horizon": "2026-27 to 2031-32 (cumulative)"}
add(A, bn(19.1), "£19.1bn", F7Q, "footnote 7",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2031-32", key=TOTAL_TAX,
    kind="cumulative",
    cond={**F7C, "price_basis": "2026-27 prices",
          "deflator": "OBR CPI forecast (EFO Table A.1), 2.0% assumed for 2032",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 tax rows, deflated"},
    hint="the tax measures of today's Budget", note="Arithmetic on HM Treasury's costings.")
add(A, bn(21.0), "£21.0bn", F7Q, "footnote 7",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2031-32", key=TOTAL_TAX,
    kind="cumulative",
    cond={**F7C, "price_basis": "cash", "derived_from": "HM Treasury Budget 2026 Table 6.1 tax rows"},
    hint="the tax measures of today's Budget",
    note="The 53 Table 6.1 tax lines sum to £20,955m over the six years; the printed total tax policy decisions sum to £20,930m.")
add(A, bn(0.6), "£0.6 billion",
    "the savings rise to yield “£0.6 billion a year on average from 2028-29”", "footnote 8",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2028-29", key=KEY[62],
    attribution="restated", model="obr_efo_forecast",
    cond={"basis": "post_behavioural", "sign_convention": YIELD, "statistic": "mean",
          "horizon": "a year on average from 2028-29", "originator": "OBR, EFO October 2026 para 3.17"},
    hint="further 2ppt rise in savings income tax rates", note="OBR's figure, quoted by TPA.")
add(A, bn(0.4), "£0.4 billion", "and the property rise “£0.4 billion”", "footnote 8",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2028-29", key=KEY[61],
    attribution="restated", model="obr_efo_forecast",
    cond={"basis": "post_behavioural", "sign_convention": YIELD, "statistic": "mean",
          "horizon": "a year on average from 2028-29", "originator": "OBR, EFO October 2026 para 3.17"},
    hint="further 2ppt rise in property income tax rates",
    note="OBR's figure, quoted by TPA. Table 6.1 line 61 averages £478m over 2028-29 to 2031-32.")

F12 = "footnote 12"
PVC = {"measure_type": "present value of capital allowances as a share of the cost"}
Q_NEW5 = "New assets getting the first-year allowance: 84.2% under 40%/14%, 85.3% under 50%/12%"
Q_OLD18 = "and 82.2% under the old 18% writing-down allowance alone"
Q_OTH5 = "82.2% at 18%, 77.4% at 14% and 74.1% at 12%"
Q_NEW10 = "70.7%, 75.0% and 77.3% for new assets"
Q_OTH10 = "70.7%, 64.2% and 60.0% for the others"
R14 = "14% writing-down allowance (before this Budget)"
R12 = "12% writing-down allowance (this Budget)"
R18 = "18% writing-down allowance (before Labour's changes)"
for v, raw, quote, sub, regime, rate, key, conf, extra in [
    (0.842, "84.2%", Q_NEW5, NEW, R_BEFORE, "5%", None, "high", ""),
    (0.853, "85.3%", Q_NEW5, NEW, R_AFTER, "5%", KEY[58], "high", ""),
    (0.822, "82.2%", Q_OLD18, NEW, R_PRE, "5%", None, "high", ""),
    (0.822, "82.2%", Q_OTH5, OLD, R18, "5%", None, "high", ""),
    (0.774, "77.4%", Q_OTH5, OLD, R14, "5%", None, "high", ""),
    (0.741, "74.1%", Q_OTH5, OLD, R12, "5%", KEY[58], "high", ""),
    (0.707, "70.7%", Q_NEW10, NEW, R_PRE, "10%", None, "medium", " The footnote lists the three new-asset values at 10% without naming their regimes; the order (old 18% WDA, 40%/14%, 50%/12%) follows the 'others' list and was checked by recomputing the present values at a 10% discount rate."),
    (0.750, "75.0%", Q_NEW10, NEW, R_BEFORE, "10%", None, "medium", " Regime order inferred as for the 70.7% row."),
    (0.773, "77.3%", Q_NEW10, NEW, R_AFTER, "10%", KEY[58], "medium", " Regime order inferred as for the 70.7% row."),
    (0.707, "70.7%", Q_OTH10, OLD, R18, "10%", None, "high", ""),
    (0.642, "64.2%", Q_OTH10, OLD, R14, "10%", None, "high", ""),
    (0.600, "60.0%", Q_OTH10, OLD, R12, "10%", KEY[58], "high", ""),
]:
    add(A, v, raw, quote, F12,
        pmetric="capital_allowance_present_value", unit="share", normalization=f"{raw} -> {v}",
        period=2027, time_basis="point_in_time", key=key, conf=conf,
        cond={**PVC, "subgroup": sub, "regime": regime, "discount_rate": f"{rate} a year"},
        hint=regime if key else None,
        note="TPA's calculation: first-year allowance taken immediately, writing-down allowances on the rest from the following year." + extra
        + ("" if key else " A regime before this Budget, so no measure key."))
Q14 = "Yield: £690m in 2029/30, £675m in 2030/31 and £655m in 2031/32"
for fy, v in [("2029-30", 690), ("2030-31", 675), ("2031-32", 655)]:
    add(A, mn(v), f"£{v}m", Q14, "footnote 14",
        metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy=fy, key=KEY[54],
        attribution="restated", model="hmt_costing_obr_certified",
        cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 line 54"),
        hint="statutory regime for the direct taxation of foreign sovereigns from 1 January 2029")
Q15 = "Yield: £480m in 2027/28, then £450m to £495m a year"
add(A, mn(480), "£480m", Q15, "footnote 15",
    metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy="2027-28", key=KEY[68],
    attribution="restated", model="hmt_costing_obr_certified",
    cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 line 68"),
    hint="foreign branch exemption made mandatory from January 2027")
for v, kind, fy in [(450, "range_low", "2029-30"), (495, "range_high", "2028-29")]:
    add(A, mn(v), f"£{v}m", Q15, "footnote 15",
        metric="revenue_change", unit="gbp", normalization="£ million × 1e6", fy=fy, key=KEY[68],
        kind=kind, attribution="restated", model="hmt_costing_obr_certified",
        cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 line 68",
                          horizon="a year, 2028-29 to 2031-32 (range across years, not an uncertainty range)",
                          year_note="TPA prints a range across 2028-29 to 2031-32; staged at the year Table 6.1 line 68 shows this value"),
        hint="foreign branch exemption made mandatory from January 2027")

# === 2. Chart data files ====================================================


def chart_hint(label):
    return f"TPA chart group '{label}'"


# --- 2a. Who's responsible for each year's tax rises? (£bn, 2026 money) ---
EVENT_SERIES = [
    ("Hunt 2023-24 tax cuts", [-42.1, -37.0, -32.4, -29.2, -29.6, -31.0, -31.3]),
    ("Sunak/Hunt threshold freezes", [33.5, 37.4, 45.2, 50.2, 51.1, 51.7, 52.7]),
    ("Sunak 2021-22, other", [15.7, 17.6, 18.2, 18.2, 18.5, 18.7, 19.0]),
    ("Hunt Nov 2022, other", [10.9, 10.4, 12.0, 12.2, 6.8, 6.8, 7.0]),
    ("Reeves Oct 2024 Budget", [1.4, 27.4, 37.4, 40.6, 40.6, 41.2, 40.8]),
    ("Reeves Nov 2025 Budget", [0.0, 1.3, 0.7, 5.9, 13.3, 24.3, 27.2]),
    ("Reeves spring statements", [0.1, 0.9, 0.8, 1.0, 1.2, 1.6, 1.6]),
    ("Healey Oct 2026 Budget", [0.0, 0.0, -1.6, 0.7, 2.7, 5.2, 5.9]),
    ("Net tax rise", [19.3, 57.9, 80.2, 99.6, 104.6, 118.6, 122.9]),
]
for s, (name, vals) in enumerate(EVENT_SERIES):
    healey = name == "Healey Oct 2026 Budget"
    for i, v in enumerate(vals):
        fy = FYS7[i]
        lab = f"{'-' if v < 0 else ''}£{abs(v):.1f}bn"
        raw = repr(v)
        note = ""
        if healey:
            note = "TPA's real-terms re-expression of Table 6.1 total tax policy decisions; arithmetic on HM Treasury's costings."
            if fy in ("2024-25", "2025-26"):
                note += " Table 6.1 starts in 2026-27; TPA's chart prints 0.0 for this year, so the row carries no measure key."
        add("EVENT", bn(v), raw, f'"value": {raw}, "name": "{fy}: {lab}"',
            f"series[{s}] '{name}', data[{i}] ({fy})",
            metric="revenue_change", unit="gbp", normalization="£ billion (2026 money) × 1e9", fy=fy,
            key=TOTAL_TAX if healey and fy not in ("2024-25", "2025-26") else None,
            cond={"basis": "forecast", "sign_convention": YIELD, "price_basis": "2026 money",
                  "policy_event": name,
                  "derived_from": "OBR costings of tax measures announced since 2020, grouped by TPA by fiscal event"},
            hint="the tax measures of the October 2026 Budget" if healey else None,
            table="Who's responsible for each year's tax rises?", column=name, note=note,
            path=("series", s, "data", i, "value"))

# --- 2b. Tax as a % of GDP - who added to the tax take? ---
GOV_SERIES = [
    ("Before measures announced since March 2020", [33.82, 34.33, 34.43, 34.53, 34.46, 34.49]),
    ("Conservative measures, 2020 to 2024", [1.25, 1.7, 1.96, 1.79, 1.75, 1.76]),
    ("Starmer/Reeves measures, 2024 to 2026", [0.93, 1.22, 1.49, 1.7, 2.03, 2.08]),
    ("2026 Budget", [0.0, -0.05, 0.02, 0.08, 0.16, 0.18]),
]
GOVT = "Tax as a % of GDP - who added to the tax take?"
for s, (name, vals) in enumerate(GOV_SERIES):
    arr = "[" + ", ".join(repr(v) for v in vals) + "]"
    for i, v in enumerate(vals):
        fy = FYS_GOV[i]
        budget = name == "2026 Budget"
        residual = s == 0
        note = "TPA: 'The grey area is what's left – so by definition the earlier measures' (footnote 3)." if residual else ""
        if budget:
            note = "Table 6.1 total tax policy decisions over nominal GDP; arithmetic on HM Treasury's costings."
            if fy == "2025-26":
                note += " Table 6.1 starts in 2026-27; TPA's chart prints 0.0 for this year, so the row carries no measure key."
        add("GOV", v, repr(v), f'"data": {arr}',
            f"series[{s}] '{name}', data[{i}] ({fy})",
            metric=None if residual else "revenue_change",
            pmetric="tax_to_gdp_ratio" if residual else None,
            punit="percent_of_gdp", fy=fy, key=TOTAL_TAX if budget and fy != "2025-26" else None,
            cond={"basis": "forecast", "denominator": "nominal GDP", "policy_event": name,
                  **({} if residual else {"sign_convention": YIELD}),
                  "derived_from": "OBR costings of each tax measure announced since March 2020 over that year's nominal GDP, grouped by the government that announced it (footnote 3)"},
            hint="the tax measures of the October 2026 Budget" if budget else None,
            table=GOVT, column=name, note=note, path=("series", s, "data", i))
for i, v in enumerate([36.0, 37.2, 37.9, 38.1, 38.4, 38.5]):
    fy = FYS_GOV[i]
    add("GOV", v, repr(v), f'"value": {v!r}, "label": {{"formatter": "{v:.1f}%"',
        f"series[4] 'Tax take', data[{i}] ({fy})",
        pmetric="tax_to_gdp_ratio", punit="percent_of_gdp", fy=fy,
        attribution="restated", model="obr_efo_forecast",
        cond={"basis": "forecast", "denominator": "nominal GDP",
              "originator": "OBR (TPA's chart; the tax-take line's source is not footnoted)"},
        table=GOVT, column="Tax take", note="Context level; restated.",
        path=("series", 4, "data", i, "value"))
add("GOV", 32.9, "32.9%", '"label": {"formatter": "2019-20 (pre-pandemic): 32.9%"',
    "series[4] 'Tax take', markLine",
    pmetric="tax_to_gdp_ratio", punit="percent_of_gdp", fy="2019-20",
    attribution="restated", model="administrative_data", bclass="administrative_fact",
    cond={"basis": "outturn", "denominator": "nominal GDP", "originator": "not named on the chart"},
    table=GOVT, column="Tax take (markLine)",
    note="Context level; restated. Footnote 2 says 'around 33%'.",
    path=("series", 4, "markLine", "data", 0, "yAxis"))

# --- 2c. Impact of the 2026 Budget on tax as a % of GDP ---
GDP_BARS = [
    ("2026-27", -0.052, "-0.05%", "-£1.6bn"),
    ("2027-28", 0.021, "0.02%", "£0.7bn"),
    ("2028-29", 0.084, "0.08%", "£2.9bn"),
    ("2029-30", 0.157, "0.16%", "£5.5bn"),
    ("2030-31", 0.177, "0.18%", "£6.5bn"),
    ("2031-32", 0.183, "0.18%", "£7.0bn"),
]
GDPT = "Impact of the 2026 Budget on tax as a % of GDP"
for i, (fy, v, pct, gbp) in enumerate(GDP_BARS):
    q = f'"value": {v!r}, "name": "{fy}: {pct} of GDP ({gbp})"'
    add("GDP", v, repr(v), q, f"series[0] '2026 Budget', data[{i}] ({fy})",
        metric="revenue_change", punit="percent_of_gdp", fy=fy, key=TOTAL_TAX,
        cond={"basis": "forecast", "sign_convention": YIELD, "denominator": "nominal GDP (OBR EFO Table A.3)",
              "chart_label": pct,
              "derived_from": "HM Treasury Budget 2026 Table 6.1 'Total tax policy decisions' over OBR nominal GDP (footnote 4)"},
        hint="the tax measures of the 2026 Budget", table=GDPT, column="2026 Budget",
        note="Arithmetic on HM Treasury's costings.", path=("series", 0, "data", i, "value"))
    add("GDP", bn(float(gbp.replace("£", "").replace("bn", ""))), gbp, q,
        f"series[0] '2026 Budget', data[{i}] ({fy}), name",
        metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy=fy, key=TOTAL_TAX,
        attribution="restated", model="hmt_costing_obr_certified",
        cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 total tax policy decisions"),
        hint="the tax measures of the 2026 Budget", table=GDPT, column="2026 Budget (tooltip name)",
        note="Rounds HM Treasury's total tax policy decisions.", path=None)

# --- 2d. Budget 2026 tax measures by tax, 2027/28 (£bn) ---
BYTAX = [
    ("Bank surcharge (temporary)", 0.95, "£1.0bn", (55,)),
    ("Capital allowances", 0.765, "£0.8bn", (58,)),
    ("Other corporate tax", 0.63, "£0.6bn", "ab2026__package_tpa_other_corporate_tax"),
    ("Other VAT", 0.38, "£0.4bn", "ab2026__package_tpa_other_vat"),
    ("Other", 0.33, "£0.3bn", "ab2026__package_tpa_other_by_tax_2027_28"),
    ("Savings and property income tax", 0.155, "£0.2bn", "ab2026__package_tpa_savings_property_income_and_cash_isa"),
    ("HMRC compliance and debt", 0.1, "£0.1bn", (45,)),
    ("CGT (Founders' Relief, BADR)", -0.2, "-£0.2bn", "ab2026__package_tpa_cgt_founders_relief_and_badr"),
    ("Income tax: mileage rates, Pension Tax Allowance and other", -0.29, "-£0.3bn", "ab2026__package_tpa_other_income_tax"),
    ("VAT cut on domestic electricity (temporary)", -0.305, "-£0.3bn", (2,)),
    ("Tariffs (incl. UK-India)", -0.465, "-£0.5bn", "ab2026__package_tpa_tariffs"),
    ("Business rates", -0.49, "-£0.5bn", "ab2026__package_tpa_business_rates"),
    ("Fuel duty cut, red diesel and HGV VED (temporary)", -0.86, "-£0.9bn", "ab2026__package_tpa_fuel_duty_red_diesel_and_hgv_ved"),
]
BYTAXT = "Budget 2026 tax measures by tax, 2027/28"


def group_row(pub, path, label, v, raw, quote, locator, scope, fy, table, *, real=False, kind="point", label_txt=None):
    single = isinstance(scope, tuple)
    lines = scope if single else GROUPS[scope]
    restated = single and not real
    c = {"basis": "forecast", "sign_convention": YIELD, "table_61_lines": ", ".join(map(str, lines))}
    if label_txt:
        c["chart_label"] = label_txt
    if real:
        c.update({"price_basis": "2026-27 prices", "horizon": "2026-27 to 2031-32 (cumulative)",
                  "deflator": "OBR CPI forecast (EFO Table A.1), 2.0% assumed for 2032 (footnote 7)"})
    if restated:
        c.update({"scoring_method": "final", "originator": f"HM Treasury, Budget 2026 Table 6.1 line {lines[0]}"})
    else:
        c["derived_from"] = "HM Treasury Budget 2026 Table 6.1 lines " + ", ".join(map(str, lines)) + (" (deflated)" if real else "")
    note = (
        "Equals HM Treasury's Table 6.1 line; restated." if restated
        else "TPA's " + ("real-terms sum" if real else "grouping") + " of HM Treasury's Table 6.1 costings; arithmetic, not an independent estimate."
        + ("" if single else " The group's lines are inferred by matching TPA's values to Table 6.1 (NOTES.md); TPA says its mapping is 'available on request'.")
    )
    add(pub, bn(v), raw, quote, locator,
        metric="revenue_change", unit="gbp",
        normalization="£ billion" + (" (2026-27 prices)" if real else "") + " as in the chart data × 1e9",
        fy=fy, key=KEY[lines[0]] if single else None, pkey=None if single else scope,
        kind=kind, attribution="restated" if restated else "own",
        model="hmt_costing_obr_certified" if restated else "arithmetic",
        cond=c, hint=chart_hint(label), table=table, column=label, note=note, path=path)


for i, (label, v, lab, scope) in enumerate(BYTAX):
    group_row("BYTAX", ("series", 0, "data", i, "value"), label, v, repr(v),
              f'"value": {v!r}, "label": {{"formatter": "{lab}"}}',
              f"series[0] '2027/28', data[{i}] (yAxis '{label}')", scope, "2027-28", BYTAXT, label_txt=lab)
add("BYTAX", bn(0.7), "£0.7bn", "Net £0.7bn.", "aria.label.description, last sentence",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2027-28", key=TOTAL_TAX,
    cond={"basis": "forecast", "sign_convention": YIELD,
          "derived_from": "HM Treasury Budget 2026 Table 6.1 tax rows, summed by TPA's groups"},
    hint="the tax measures of the 2026 Budget", table=BYTAXT, column="Net",
    note="The groups sum to £700m (footnote 5); arithmetic on HM Treasury's costings.")

# --- 2e. Budget tax changes (grouped by year) (£bn) ---
BYYEAR = [
    ("Other", [-0.205, -0.36, 0.055, 0.005, -0.03, -0.245], "ab2026__package_tpa_other_by_year"),
    ("Business rates", [0.01, -0.49, -0.685, -0.03, -0.04, -0.045], "ab2026__package_tpa_business_rates"),
    ("Bank surcharge", [0.305, 0.95, 0.22, 0.0, 0.0, 0.0], (55,)),
    ("Energy and environment", [0.06, 0.025, -0.33, -0.575, -0.505, -0.49], "ab2026__package_tpa_energy_and_environment"),
    ("Other income tax", [-0.065, -0.29, -0.585, -0.6, -0.215, -0.255], "ab2026__package_tpa_other_income_tax"),
    ("Temporary VAT and fuel cuts", [-1.835, -1.165, 0.0, 0.0, 0.0, 0.0], "ab2026__package_tpa_temporary_vat_and_fuel_cuts"),
    ("Other VAT", [-0.015, 0.38, 0.84, 0.8, 0.795, 0.83], "ab2026__package_tpa_other_vat"),
    ("Savings and property income", [0.015, 0.155, 1.11, 0.92, 0.95, 0.975], "ab2026__package_tpa_savings_property_income_and_cash_isa"),
    ("Capital allowances", [0.125, 0.765, 1.04, 1.075, 1.1, 1.12], (58,)),
    ("Other corporate tax", [-0.04, 0.63, 1.085, 1.98, 1.955, 1.925], "ab2026__package_tpa_other_corporate_tax"),
    ("Tax gap (HMRC)", [0.01, 0.1, 0.115, 1.98, 2.485, 3.16], (45,)),
]
BYYEART = "Budget tax changes (grouped by year)"
for s, (label, vals, scope) in enumerate(BYYEAR):
    arr = "[" + ", ".join(repr(v) for v in vals) + "]"
    for i, v in enumerate(vals):
        group_row("BYYEAR", ("series", s, "data", i), label, v, repr(v), f'"data": {arr}',
                  f"series[{s}] '{label}', data[{i}] ({FYS6[i]})", scope, FYS6[i], BYYEART)
NETQ = ("Net total: 2026-27 £-1.65bn, 2027-28 £0.70bn, 2028-29 £2.87bn, 2029-30 £5.55bn, "
        "2030-31 £6.50bn, 2031-32 £6.97bn.")
for fy, raw in zip(FYS6, ["£-1.65bn", "£0.70bn", "£2.87bn", "£5.55bn", "£6.50bn", "£6.97bn"]):
    add("BYYEAR", bn(float(raw.replace("£", "").replace("bn", ""))), raw, NETQ,
        "aria.label.description, 'Net total'",
        metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy=fy, key=TOTAL_TAX,
        attribution="restated", model="hmt_costing_obr_certified",
        cond=hmt_restated(originator="HM Treasury, Budget 2026 Table 6.1 total tax policy decisions"),
        hint="the tax measures of the 2026 Budget", table=BYYEART, column="Net total",
        note="Matches HM Treasury's printed totals to two decimals (TPA's groups sum to -1.635 in 2026-27).")

# --- 2f. Budget 2026 measures: total over 2026/27 to 2031/32 (£bn, 2026/27 prices) ---
BYMEAS = [
    ("Tax gap package (HMRC compliance and debt)", 7.155, "£7.2bn", (45,)),
    ("Writing-down allowance cut to 12%", 4.863, "£4.9bn", (58,)),
    ("Savings and property income tax rates +2ppts", 3.981, "£4.0bn", SP),
    ("Foreign sovereign investments", 2.422, "£2.4bn", (54,)),
    ("Foreign branch exemption made mandatory", 2.315, "£2.3bn", (68,)),
    ("Distributions framework", 2.207, "£2.2bn", (49,)),
    ("Private hire VAT", 1.58, "£1.6bn", (59,)),
    ("Bank surcharge to 6% (temporary)", 1.436, "£1.4bn", (55,)),
    ("Online marketplace VAT liability", 1.181, "£1.2bn", (46,)),
    ("BADR lifetime limit cut to £500,000", 1.0, "£1.0bn", (60,)),
    ("UK Export Finance", 0.753, "£0.8bn", (44,)),
    ("Machine games duty", 0.671, "£0.7bn", (56,)),
    ("Company car tax 2030-31 rates", 0.592, "£0.6bn", (86,)),
    ("Pension Tax Allowance", -0.237, "-£0.2bn", (52,)),
    ("Trading allowance to £3,000", -0.688, "-£0.7bn", (15,)),
    ("VAT cut on domestic electricity (temporary)", -1.051, "-£1.1bn", (2,)),
    ("Mileage rates", -1.076, "-£1.1bn", (5,)),
    ("Founders' Relief", -1.194, "-£1.2bn", (26,)),
    ("Business rates", -1.221, "-£1.2bn", "ab2026__package_tpa_business_rates"),
    ("Other", -1.275, "-£1.3bn", "ab2026__package_tpa_other_by_measure"),
    ("Fuel duty cut (temporary)", -1.332, "-£1.3bn", (3,)),
    ("Emissions Trading Scheme delay", -1.379, "-£1.4bn", (96,)),
    ("Tariffs (incl. UK-India)", -1.594, "-£1.6bn", "ab2026__package_tpa_tariffs"),
]
BYMEAST = "Budget 2026 measures: total over 2026/27 to 2031/32"
for i, (label, v, lab, scope) in enumerate(BYMEAS):
    group_row("BYMEAS", ("series", 0, "data", i, "value"), label, v, repr(v),
              f'"value": {v!r}, "label": {{"formatter": "{lab}"}}',
              f"series[0] 'Total, 2026/27 to 2031/32', data[{i}] (yAxis '{label}')", scope, "2031-32",
              BYMEAST, real=True, kind="cumulative", label_txt=lab)
add("BYMEAS", bn(19.1), "£19.1bn", "Net total £19.1bn.", "aria.label.description, last sentence",
    metric="revenue_change", unit="gbp", normalization="£ billion × 1e9", fy="2031-32", key=TOTAL_TAX,
    kind="cumulative",
    cond={"basis": "forecast", "sign_convention": YIELD, "price_basis": "2026-27 prices",
          "horizon": "2026-27 to 2031-32 (cumulative)",
          "derived_from": "HM Treasury Budget 2026 Table 6.1 tax rows, deflated"},
    hint="the tax measures of the 2026 Budget", table=BYMEAST, column="Net total",
    note="Arithmetic on HM Treasury's costings; the same total as footnote 7.")

# --- 2g. Investment bank: tax as % of profit (2027 rules) ---
COUNTRIES = ["Netherlands", "Italy", "France", "UK after Budget", "Germany", "Spain", "UK", "US", "Ireland", "Singapore"]
TOTALS = [
    ("43.8%", "The Netherlands is highest at 43.8%"), ("42.0%", "then Italy 42.0%"),
    ("36.0%", "France 36.0%"), ("33.7%", "UK after Budget 33.7%"), ("32.8%", "Germany 32.8%"),
    ("31.4%", "Spain 31.4%"), ("30.8%", "the UK 30.8%"), ("23.4%", "the US 23.4%"),
    ("16.1%", "Ireland 16.1%"), ("14.9%", "Singapore 14.9%"),
]
COMPONENTS = [
    ("Corporate income taxes", [30.9, 40.4, 32.4, 30.5, 31.6, 30.1, 27.6, 23.1, 14.6, 14.9]),
    ("Bank levies and deposit insurance", [11.5, None, 0.3, 2.3, None, None, 2.3, None, None, None]),
    ("Irrecoverable VAT and sales tax", [1.3, 1.6, 1.3, 0.9, 1.2, 1.4, 0.9, 0.3, 1.5, None]),
    ("Other business taxes", [None, None, 1.9, None, None, None, None, None, None, None]),
]
BANKT = "Investment bank: tax as % of profit"
BANK_HINT = "bank surcharge 6% (now 3%) temporarily, from 1 January 2027 to 31 March 2028"


def bank_cond(country, comp=None):
    c = {"entity": "notional investment bank", "rules": "2027 rules", "country": country,
         "denominator": "profit"}
    if comp:
        c["tax_component"] = comp
    if country == "UK after Budget":
        c["scenario"] = "UK after the Budget (bank surcharge 6%)"
    elif country == "UK":
        c["scenario"] = "UK before the Budget (bank surcharge 3%)"
    return c


for i, (raw, quote) in enumerate(TOTALS):
    country = COUNTRIES[i]
    ukb = country == "UK after Budget"
    add("BANK", float(raw.rstrip("%")), raw, quote, f"aria.label.description; yAxis[1].data[{i}] ('{country}')",
        pmetric="effective_tax_rate", unit="percent", period=2027, time_basis="annual",
        key=KEY[55] if ukb else None, cond=bank_cond(country),
        hint=BANK_HINT if ukb else None, table=BANKT, column=f"{country}: total",
        geography="UK" if country.startswith("UK") else country,
        note="TPA's model of a notional investment bank's taxes." + ("" if ukb else " Comparison or pre-Budget level, so no measure key."),
        path=("yAxis", 1, "data", i, "value"))
for s, (comp, vals) in enumerate(COMPONENTS):
    arr = "[" + ", ".join("null" if v is None else repr(v) for v in vals) + "]"
    for i, v in enumerate(vals):
        if v is None:
            continue
        country = COUNTRIES[i]
        ukb = country == "UK after Budget" and comp == "Corporate income taxes"
        add("BANK", v, repr(v), f'"data": {arr}', f"series[{s}] '{comp}', data[{i}] ('{country}')",
            pmetric="effective_tax_rate", unit="percent", period=2027, time_basis="annual",
            key=KEY[55] if ukb else None, cond=bank_cond(country, comp),
            hint=BANK_HINT if ukb else None, table=BANKT, column=f"{country}: {comp}",
            geography="UK" if country.startswith("UK") else country,
            note="Component of TPA's notional investment bank's tax as % of profit."
            + ("" if ukb else " The surcharge does not change this component, so no measure key." if country == "UK after Budget" else " No measure key."),
            path=("series", s, "data", i))

# === 3. Calculator screenshot (footnote 1) ==================================

CBSUB = "employee in the rest of the UK (outside Scotland) on a £70,000 salary, receiving child benefit (number of children not shown)"
CBN = "Single-household worked example (mode 3), read from the screenshot's tooltip. The Budget's change here comes from child benefit uprating (footnote 1), not a Table 6.1 measure, so no measure key."
CBGEO = "UK excluding Scotland"
add("CB", 58.3, "58.3%", "Current rules, rest of UK (2026/27) 58.3%", "tooltip panel, first series",
    pmetric="marginal_tax_rate", unit="percent", fy="2026-27", model="open_source_model", conf="medium",
    cond={"subgroup": CBSUB, "scenario": "Current rules, rest of UK (2026/27)"}, geography=CBGEO,
    table="Marginal rate", column="Current rules, rest of UK (2026/27)", note=CBN)
add("CB", 58.9, "58.9%", "Budget - 2027/28 58.9%", "tooltip panel, second series",
    pmetric="marginal_tax_rate", unit="percent", fy="2027-28", model="open_source_model", conf="medium",
    cond={"subgroup": CBSUB, "scenario": "Budget - 2027/28"}, geography=CBGEO,
    hint="TPA calculator, Budget 2027/28 rules", table="Marginal rate", column="Budget - 2027/28", note=CBN)
CBB = " The breakdown sums to £583 of each £1,000 (58.3%), the current-rules rate, so it is staged under current rules. At this income the child benefit charge on £1,000 is 5% of a year's child benefit, so £163 implies about £3,260 of child benefit."
add("CB", 417, "£417", "Of the next £1,000, you keep £417", "tooltip panel, breakdown",
    pmetric="marginal_take_home_pay", unit="gbp", fy="2026-27", model="open_source_model", conf="medium",
    cond={"subgroup": CBSUB, "scenario": "Current rules, rest of UK (2026/27)",
          "measure_type": "kept from the next £1,000 of salary"}, geography=CBGEO,
    table="Marginal rate", column="Of the next £1,000, you keep", note=CBN + CBB)
for raw, v, tax, quote in [("£400", 400, "income tax", "Income tax £400"), ("£20", 20, "National Insurance", "NI £20"),
                           ("£163", 163, "High Income Child Benefit Charge", "Child benefit charge £163")]:
    add("CB", v, raw, quote, "tooltip panel, breakdown",
        pmetric="marginal_tax_amount", unit="gbp", fy="2026-27", model="open_source_model", conf="medium",
        cond={"subgroup": CBSUB, "scenario": "Current rules, rest of UK (2026/27)", "tax": tax,
              "measure_type": "tax on the next £1,000 of salary"},
        geography=CBGEO, table="Marginal rate", column=quote.rsplit(" ", 1)[0], note=CBN + CBB)


# === review fixes, 3 November 2026 ========================================
# verify-thinktanks-a.md, uk_tpa (PR #231). Explicit edits on top of the rows
# above; no primary was re-opened (the session's network policy refused
# taxpolicy.org.uk), and no printed value changes.

def _row(i, value_raw):
    """Row i (0-based, the reviewed order), checked by its printed value."""
    r = ROWS[i]
    assert r["value_raw"] == value_raw, (i, r["value_raw"], value_raw)
    return r

# Finding 5 (optional, applied): "about two-fifths" is the share of the
# £123bn coming from a group of Budgets, not models.py's revenue_share (a
# group's share of one measure's yield).
_r = _row(1, "About two-fifths")
_r.pop("metric")
_r["proposed_metric"] = "revenue_share_by_fiscal_event"

# Finding 1 (the coordinator's call): £93 is the most tax the Pension Tax
# Allowance removes, 20% x (£13,036.40 - £12,570), the same quantity as the
# "up to £94" maximum: design under rule 8. It moves to row 17's conditions.
_row(17, "53%")["conditions"]["tax_removed"] = "£93 (as printed)"
_row(16, "£93")
del ROWS[16]


# === output =================================================================

def manifest_lines():
    keys = ["url", "title", "date", "publisher", "sha256", "bytes", "doc_type", "access", "retrieved", "note"]
    return "".join(json.dumps({k: p[k] for k in keys}, ensure_ascii=False) + "\n" for p in PUBS.values())


def claims_bytes():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in ROWS:
            gz.write((json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    return buf.getvalue()


# === --verify ===============================================================

class _Text(HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "br", "td", "th", "section", "article", "figcaption", "blockquote"}

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


def _texts():
    out = {}
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
            out[k] = ("text", _norm("".join(t.out)))
        elif p["doc_type"] == "flourish_json":
            obj = json.loads(b)
            out[k] = ("json", obj, json.dumps(obj, ensure_ascii=False))
    return out


def _at(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def _hmt_lines():
    t = {}
    with gzip.open(HMT_TABLES, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            c = r["conditions"]
            if c["table"] == "6.1" and "table_line" in c:
                t.setdefault(int(c["table_line"]), [0] * 6)[FYS6.index(c["fy"])] = r["value"] / 1e9
    return t


def _solve(a, b):
    """Least squares by normal equations and Gauss-Jordan (6 unknowns)."""
    n = len(a[0])
    m = [[sum(r[i] * r[j] for r in a) for j in range(n)] + [sum(r[i] * y for r, y in zip(a, b))] for i in range(n)]
    for i in range(n):
        piv = max(range(i, n), key=lambda k: abs(m[k][i]))
        m[i], m[piv] = m[piv], m[i]
        for k in range(n):
            if k != i:
                f = m[k][i] / m[i][i]
                m[k] = [x - f * y for x, y in zip(m[k], m[i])]
    return [m[i][n] / m[i][i] for i in range(n)]


def verify():
    texts = _texts()
    bad = 0
    for idx, pub, path in CHECKS:
        r = ROWS[idx]
        if pub not in texts:
            continue
        kind = texts[pub][0]
        hay = texts[pub][1] if kind == "text" else texts[pub][2]
        if _norm(r["quote"]) not in hay:
            print(f"row {idx}: quote not in {pub}: {r['quote']!r}")
            bad += 1
        if path is not None:
            got = _at(texts[pub][1], path)
            want = r["value"]
            if isinstance(got, str):
                got = float(got.rstrip("%"))
            if r.get("unit_concept") == "gbp" and r["normalization"].startswith("£ billion"):
                got = round(got * 1e9)
            if got != want:
                print(f"row {idx}: value {want} != {got} at {pub} {path}")
                bad += 1
    t = _hmt_lines()
    tax_lines = sorted(t)

    def cash(lines):
        return [sum(t[k][i] for k in lines) for i in range(6)]

    for label, vals, scope in BYYEAR:
        lines = scope if isinstance(scope, tuple) else GROUPS[scope]
        if any(abs(a - b) > 1e-9 for a, b in zip(cash(lines), vals)):
            print(f"by-year group {label!r}: lines {lines} give {cash(lines)}, TPA {vals}")
            bad += 1
    for label, v, _, scope in BYTAX:
        lines = scope if isinstance(scope, tuple) else GROUPS[scope]
        if abs(cash(lines)[1] - v) > 1e-9:
            print(f"by-tax group {label!r}: lines {lines} give {cash(lines)[1]}, TPA {v}")
            bad += 1
    singles = [(cash(s), v) for _, v, _, s in BYMEAS if isinstance(s, tuple)]
    f = _solve([c for c, _ in singles], [v for _, v in singles])
    for label, v, _, scope in BYMEAS:
        lines = scope if isinstance(scope, tuple) else GROUPS[scope]
        real = sum(a * b for a, b in zip(cash(lines), f))
        if abs(real - v) > 0.002:
            print(f"by-measure bar {label!r}: lines {lines} give {real:.4f}, TPA {v}")
            bad += 1
    print(f"deflators fitted to the single-measure bars: {[round(x, 4) for x in f]}")
    named = set()
    for _, _, _, scope in BYMEAS:
        named |= set(scope if isinstance(scope, tuple) else GROUPS[scope])
    tax_heads = {k for k in tax_lines if k in named}
    print(f"by-measure bars cover {len(tax_heads)} Table 6.1 lines")
    print(f"verify: {len(ROWS)} rows, {len(texts)} primaries read, {bad} problems")
    return bad


if __name__ == "__main__":
    (HERE / "manifest.jsonl").write_text(manifest_lines(), encoding="utf-8")
    data = claims_bytes()
    (HERE / "claims_staged.jsonl.gz").write_bytes(data)
    print(f"{len(ROWS)} rows, sha256 {hashlib.sha256(data).hexdigest()}")
    if "--verify" in sys.argv[1:]:
        sys.exit(1 if verify() else 0)
