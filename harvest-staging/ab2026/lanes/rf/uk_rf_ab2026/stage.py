#!/usr/bin/env python3
"""Stage the Resolution Foundation's Autumn Budget 2026 claims (family uk_rf_ab2026, #230).

Every row is data in this file, so running it rewrites claims_staged.jsonl.gz
byte for byte:

    python3 stage.py

The primaries are hashed, not vendored. With the fetched copies on disk, this
also checks each document's sha256 against manifest.jsonl, that every text
quote occurs in its document, and that every workbook cell embedded below
matches the workbook's stored value:

    python3 stage.py --check-primaries ../../../.ab2026-primaries/uk_rf_ab2026

The check needs pdftotext (poppler) for the two PDFs.
"""

import argparse
import gzip
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import zipfile
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
OUT = HERE / "claims_staged.jsonl.gz"
SOURCE = "resolution_foundation"
EVENT = "autumn_budget_2026"
PUBLISHER = "Resolution Foundation"

# ---------------------------------------------------------------------------
# Primaries (manifest.jsonl carries the same sha256s; --check-primaries
# compares them).
# ---------------------------------------------------------------------------
DOCS = {
    "PR28": dict(
        title="Press release: Budget balancing act leaves families braced for tough winter and four-year living standards downturn",
        url="https://www.resolutionfoundation.org/press-releases/budget-balancing-act-leaves-families-braced-for-tough-winter-and-four-year-living-standards-downturn/",
        date="2026-10-28",
        sha="ac5369e6f73bbfddc53dfd9977a34a89e032be513e1a21f192a02d124ef98878",
        file="pr_2026-10-28.html",
    ),
    "PR29": dict(
        title="Press release: Britain braced for painful second half of the Parliament",
        url="https://www.resolutionfoundation.org/press-releases/britain-braced-for-painful-second-half-of-the-parliament/",
        date="2026-10-29",
        sha="40b102686bbee5dbaff30ea96bfa6bef3f73fe777142a826c811e7fa88c7c22d",
        file="pr_2026-10-29.html",
    ),
    "LAND": dict(
        title="Spread thin: Analysing the Autumn 2026 Budget (publication page)",
        url="https://www.resolutionfoundation.org/publications/spread-thin/",
        date="2026-10-29",
        sha="66a999dc35476a54c003bb9fda0ebbb3648cb52403d7b78c5b9fe9f5f569d792",
        file="spread-thin.html",
    ),
    "V1": dict(
        title="Spread thin: Analysing the Autumn 2026 Budget (briefing PDF, first version, Spread-thin-1.pdf)",
        url="https://www.resolutionfoundation.org/app/uploads/2026/10/Spread-thin-1.pdf",
        date="2026-10-29",
        sha="a669f39d30d5648697ce0234692bd9695fadafd85669ee809c02af0c90595603",
        file="Spread-thin-1.pdf",
    ),
    "V2": dict(
        title="Spread thin: Analysing the Autumn 2026 Budget (briefing PDF, replaced version, Spread-thin.pdf)",
        url="https://www.resolutionfoundation.org/app/uploads/2026/10/Spread-thin.pdf",
        date="2026-10-29",
        sha="9536b6cd8478dea91f88a103c9004cc7b4cdde269a521f62048e3c523a15d9ff",
        file="Spread-thin.pdf",
    ),
    "XL": dict(
        title="Spread thin: chart data workbook (Final-clean-charts-all-sections-for-comms.xlsx)",
        url="https://www.resolutionfoundation.org/app/uploads/2026/10/Final-clean-charts-all-sections-for-comms.xlsx",
        date="2026-10-29",
        sha="a4e1c072bf8f95f364a470be46ad1d1fad2c4f86fa83d371b45b577df1d6e0d1",
        file="Final-clean-charts-all-sections-for-comms.xlsx",
    ),
    "CMT": dict(
        title="It's good to be flexible (Nye Cominetti, comment)",
        url="https://www.resolutionfoundation.org/comment/its-good-to-be-flexible/",
        date="2026-10-29",
        sha="3510a245ad89667dee8e6dbb42d175970c05667a244c4034197c43000962fcfc",
        file="comment_flexible.html",
    ),
}

# Registered enums used here (scorecard_db.models). Anything else becomes
# proposed_metric / proposed_unit; pipeline/ab2026_harvest_contract.py checks
# both lists against the live enums.
METRICS = {
    "affected_count", "affected_share", "average_annual_gain",
    "average_household_income_change", "decisions_effect_on_borrowing",
    "eligibility_rate", "eligible_count", "energy_bill_change",
    "fiscal_headroom", "gainer_count", "participant_count",
    "pct_change_after_tax_income", "poverty_rate", "poverty_rate_change",
    "real_income_growth", "revenue_change", "share_gaining", "share_losing",
    "spending_share", "tax_liability",
}
UNITS = {
    "families", "gbp", "gbp_per_week", "households", "percent",
    "percentage_points", "persons", "properties", "share",
}

# ---------------------------------------------------------------------------
# Shared condition values
# ---------------------------------------------------------------------------
SC_COST = "positive = cost to the Exchequer"
SC_YIELD = "positive = yield to the Exchequer"
SC_BORROW = "positive = increase in borrowing"
SC_GAIN = "positive = gain to households"
SC_F10 = ("positive = raises revenue (reduces borrowing), as RF plots Figure 10 "
          "(the OBR's borrowing sign flipped: workbook F10 I15 'Signs flipped from source')")
VIG_AXIS = "net equivalised household income vigintile, after housing costs"
DEC_AXIS = "net equivalised household income decile, after housing costs"
HALF_AXIS = "household income distribution, split at the median (RF: poorer / richer half)"
F8_GEO = "Council Tax and VAT cuts modelled for Great Britain only; Fuel Duty for the UK (Figure 8 notes)"
TWO_YEARS = "2026-27 and 2027-28 (Figure 8: temporary policies; p.19: 'this year and next')"
NEXT5 = "annual average over the next five years, 2026-27 to 2030-31"
COLA_PKG = "the cost of living package: Household Energy Payment, electricity VAT cut (original six months and three-month extension) and Fuel Duty delay"

# Table titles
FIG = {
    7: "Figure 7: The typical household will pay almost as much for energy this year as in 2022-23",
    8: "Figure 8: In cash terms, richer families benefit almost as much as poorer families from the cost of living package",
    9: "Figure 9: The Budget will help a handful of renters to buy via Your First Home, while support for tenants on the lowest income remains frozen",
    10: "Figure 10: Measures announced raise revenues, but there will be a hit if Fuel Duty remains at current levels",
    20: "Figure 20: The combined impact of this Parliament’s tax and benefit changes has been progressive",
    21: "Figure 21: Living standards for non-pensioner families are set to fall for the rest of this Parliament",
    22: "Figure 22: This Parliament’s income growth is expected to be progressive, with lower-income families benefiting most",
    23: "Figure 23: Child poverty is set to fall this Parliament",
}

# Registered keys (data/uk/ab2026_measures.json)
HEP = "ab2026__household_energy_payment_100_bands_a_to_d"
VAT = "ab2026__electricity_vat_zero_rate_to_july_2027"
FD = "ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred"
PKG = "ab2026__package_household_energy_vat_and_fuel_duty"
TOTAL = "ab2026__package_total_policy_decisions"
CA = "ab2026__carers_allowance_earnings_taper"
PTA = "ab2026__pension_tax_allowance"
MGD = "ab2026__machine_games_duty_higher_stake_25pc"
YFH = "ab2026__your_first_home_equity_loan"
BANK = "ab2026__bank_surcharge_6pc_temporary"
WDA = "ab2026__writing_down_allowance_12pc_and_fya_50pc"
FOUNDERS = "ab2026__founders_relief_cgt"
BRR = "ab2026__business_rates_retention_mayoral_authorities"
DIP = "ab2026__defence_investment_plan_further_savings"

# Proposed keys (scopes in NOTES.md)
P_HEP_VAT = "ab2026__package_household_energy_payment_and_electricity_vat"
P_ENERGY_SUPPORT = "ab2026__package_rf_energy_bill_support_announced_at_budget"
P_SAV_PROP = "ab2026__package_savings_and_property_income_rates_plus_2pp"
P_AB26_PERM = "ab2026__package_rf_ab26_permanent_personal_measures"
P_PARLIAMENT = "ab2026__package_rf_parliament_permanent_tax_and_benefit_measures"
P_OBR_TAX = "ab2026__package_obr_direct_effect_of_tax_measures"
P_OBR_ADMIN = "ab2026__package_obr_tax_administration_compliance_and_debt_collection"
P_RF_OTHER_TAX = "ab2026__package_rf_other_tax_measures"
P_OBR_DECISIONS = "ab2026__package_obr_total_effect_of_government_decisions"
P_ABSOLUTE = "ab2026__package_rf_absolute_policy_changes"
P_RDEL = "ab2026__package_rdel_decisions_excluding_household_energy_payment"
P_GAS_SC = "ab2026__gas_standing_charge_moved_to_unit_rates"
P_GSL = "ab2026__gas_supplier_levy_funded_from_general_taxation"
P_MIN_WAGE = "ab2026__minimum_wage_rates_april_2027"
O_FD_FREEZE = "ab2026_option__fuel_duty_continued_freeze"
O_TAX_FREEZE = "ab2026_option__obr_tax_measures_with_continued_fuel_duty_freeze"
O_FD_RPI = "ab2026_option__fuel_duty_rpi_uprating_since_2011"
O_LHA = "ab2026_option__lha_unfreeze_2027_28"

ROWS = []


def dec(raw, scale=1):
    """A number from its printed or stored string, scaled exactly."""
    return float(Decimal(raw) * Decimal(scale))


def add(doc, loc, raw, value, quote, metric, unit, *, fy=None, period=None,
        tb=None, c=None, mk=None, pk=None, att="own", model="landman_ttm",
        bench="different_model", kind="point", norm="as printed", note="",
        hint=None, base=None, pbase=None, table=None, col=None, conf="high",
        geo="UK"):
    d = DOCS[doc]
    if fy:
        period, tb = int(fy[:4]) + 1, "fiscal_year"
    assert period and tb, (doc, loc, raw)
    assert raw in quote, (doc, loc, raw, quote)
    assert len(quote.split()) < 15, (doc, loc, quote)
    cond = {"fiscal_event": EVENT, "geography": geo}
    if fy:
        cond["fy"] = fy
    for k, v in (c or {}).items():
        assert isinstance(v, str), (doc, loc, k)
        cond[k] = v
    if pk:
        assert mk is None
        cond["proposed_measure_key"] = pk
    row = {
        "source": SOURCE,
        "source_model": model,
        "value": value,
        "value_raw": raw,
        "normalization": norm,
        "value_kind": kind,
        "period": period,
        "time_basis": tb,
        "conditions": cond,
        "reform_hint": hint,
        "measure_key": mk,
        "attribution": att,
        "benchmark_class": bench,
        "baseline_policy": base,
        "publication": {
            "title": d["title"],
            "url": d["url"],
            "date": d["date"],
            "publisher": PUBLISHER,
            "primary_sha256": d["sha"],
            "locator": loc,
            "access": "direct",
        },
        "source_table": table,
        "source_column": col,
        "quote": quote,
        "note": note,
        "parse_confidence": conf,
        "status": "ok",
    }
    if metric in METRICS:
        row["metric"] = metric
    else:
        row["proposed_metric"] = metric
    if unit in UNITS:
        row["unit_concept"] = unit
    else:
        row["proposed_unit"] = unit
    if pbase:
        row["proposed_baseline"] = pbase
    ROWS.append(row)


BN = "£ billion × 1e9 → £"
M = "£ million × 1e6 → £"
PCT_SHARE = "per cent / 100 → share"
LOSS = "printed as a fall ('lower' / 'fall' / 'drop'); carried negative under 'positive = gain to households'"
RESTATED_HMT = "Restates HM Treasury, Budget 2026 Table 6.1"
RESTATED_OBR = "Restates the OBR, Economic and fiscal outlook, October 2026"

# ===========================================================================
# PR28: press release, 28 October 2026. Locators count the body paragraphs
# after the dateline.
# ===========================================================================
add("PR28", "paragraph 2", "£11 billion", dec("11", 1e9),
    "Borrowing is up by £11 billion a year on average",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"basis": "pre-measures", "comparison": "October 2026 vs March 2026 OBR forecast",
       "horizon": NEXT5 + " (Spread thin p.8)", "statistic": "annual average",
       "sign_convention": SC_BORROW},
    att="restated", model="obr_efo_forecast", norm=BN,
    note=RESTATED_OBR + " (Spread thin p.3: 'which the OBR projected over the forecast period'). The release prints no horizon; Spread thin p.8 gives 'over the next five years'.")
add("PR28", "paragraph 4", "£7 billion", dec("7", 1e9),
    "Fresh policy changes are worth £7 billion in absolute terms",
    "absolute_policy_change", "gbp", fy="2031-32", pk=P_ABSOLUTE,
    c={"statistic": "sum of the absolute values of giveaways and clawbacks (RF's fiscal-event size measure)",
       "horizon": "by the end of the forecast"},
    model="arithmetic", norm=BN, conf="medium",
    hint="Fresh policy changes (giveaways and clawbacks)",
    note="'By the end of the forecast' read as 2031-32, the October 2026 forecast's final year.")
add("PR28", "paragraph 5", "£2.6 billion", dec("2.6", 1e9),
    "the £2.6 billion Household Energy Payment",
    "revenue_change", "gbp", fy="2026-27", mk=HEP,
    c={"sign_convention": SC_COST}, att="restated", model="hmt_costing_obr_certified",
    norm=BN, hint="the £2.6 billion Household Energy Payment",
    note=RESTATED_HMT + " line 1 (-£2,625m in 2026-27, its only non-zero year). The release prints no year; Spread thin p.27 has 'worth £2.6 billion in 2026-27'.")
add("PR28", "paragraph 6", "around four-in-five", 0.8,
    "around four-in-five properties in England eligible for support",
    "eligibility_rate", "share", fy="2026-27", mk=HEP, geo="England",
    c={"unit_population": "properties (dwellings in Council Tax bands A-D)"},
    model="administrative_data", bench="administrative_fact",
    norm="'four-in-five' → 0.8", hint="a £100 rebate for those living in Council Tax bands A-D")
add("PR28", "paragraph 6", "around one-in-eight", 0.125,
    "around one-in-eight households in the bottom half of the income distribution",
    "affected_share", "share", fy="2026-27", mk=HEP, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS,
       "denominator": "households in the bottom half of the income distribution",
       "subgroup": "live in higher-band properties (Council Tax bands E and above) and miss out on the Household Energy Payment"},
    model="survey_microdata", norm="'one-in-eight' → 0.125",
    hint="a £100 rebate for those living in Council Tax bands A-D")
add("PR28", "paragraph 7", "20 per cent", 0.2,
    "One-in-five (20 per cent) households in London and the South East",
    "affected_share", "share", fy="2026-27", mk=HEP, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "region": "London and the South East",
       "denominator": "households in the bottom half of the income distribution in the region",
       "subgroup": "live in Council Tax bands E and above and will not receive the Household Energy Payment"},
    model="survey_microdata", norm=PCT_SHARE)
add("PR28", "paragraph 7", "5 per cent", 0.05,
    "compared to one-in-twenty (5 per cent) in the North East",
    "affected_share", "share", fy="2026-27", mk=HEP, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS,
       "region": "North East, North West, and Yorkshire and The Humber",
       "denominator": "households in the bottom half of the income distribution in the regions",
       "subgroup": "live in Council Tax bands E and above and will not receive the Household Energy Payment"},
    model="survey_microdata", norm=PCT_SHARE)
add("PR28", "paragraph 8", "£2,210", 2210,
    "bills are set to average £2,210 across 2027",
    "typical_energy_bill", "gbp", period=2027, tb="annual", geo="GB",
    c={"household_type": "typical dual-fuel household",
       "basis": "EDF Energy Price Cap forecasts of 26 October 2026 (Notes to Editors)"},
    model="arithmetic",
    note="Spread thin p.16 puts the Q1 2027 cap at £2,192 (annualised); the release's £2,210 is the 2027 average.")
add("PR28", "paragraph 8", "£600", 600,
    "an increase of £600 (or 38 per cent) on the 2026 average",
    "average_energy_bill_change", "gbp", period=2027, tb="annual", geo="GB",
    c={"household_type": "typical dual-fuel household", "comparison": "2027 average vs 2026 average",
       "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("PR28", "paragraph 8", "38 per cent", 38,
    "an increase of £600 (or 38 per cent) on the 2026 average",
    "average_energy_bill_change", "percent", period=2027, tb="annual", geo="GB",
    c={"household_type": "typical dual-fuel household", "comparison": "2027 average vs 2026 average",
       "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("PR28", "paragraph 8", "up to £116", 116,
    "Support of up to £116 announced today",
    "energy_bill_change", "gbp", period=2027, tb="annual", geo="GB", pk=P_ENERGY_SUPPORT,
    c={"household_type": "typical household receiving the support",
       "sign_convention": "positive = support (a reduction in the household's bills)"},
    kind="range_high", model="arithmetic", conf="medium",
    hint="Support of up to £116 announced today",
    note="RF does not itemise the £116 (the £100 Household Energy Payment plus smaller bill measures announced on Budget day). Period read from the sentence's 2027 bill rise.")
add("PR28", "paragraph 8", "less than a fifth", 0.2,
    "will alleviate less than a fifth of this coming rise in bills",
    "bill_rise_offset_share", "share", period=2027, tb="annual", geo="GB", pk=P_ENERGY_SUPPORT,
    c={"denominator": "the £600 rise in the typical bill in 2027"},
    kind="range_high", model="arithmetic", norm="'a fifth' → 0.2", conf="medium")
add("PR28", "paragraph 9", "around £20 billion", dec("20", 1e9),
    "they could have raised around £20 billion a year",
    "revenue_change", "gbp", fy="2026-27", pk=O_FD_RPI,
    c={"sign_convention": SC_YIELD,
       "counterfactual": "planned Fuel Duty rises delivered over the past 15 years"},
    model="arithmetic", norm=BN, conf="medium",
    hint="Had Chancellors actually delivered planned rises over the past 15 years",
    note="The release prints no year; Spread thin p.24 says 'around £20 billion higher this year'.")
add("PR28", "paragraph 11", "£2 billion", dec("2", 1e9),
    "by an average of £2 billion a year",
    "decisions_effect_on_borrowing", "gbp", period=2031, tb="fiscal_year", pk=P_OBR_DECISIONS,
    c={"horizon": NEXT5, "statistic": "annual average", "sign_convention": SC_BORROW},
    model="arithmetic", norm=BN, hint="the Chancellor's decisions",
    note="The sentence: the decisions 'have raised total borrowing over the next five years – by an average of £2 billion a year' (while reducing it in 2029-30).")
add("PR28", "paragraph 11", "£13bn", dec("13", 1e9),
    "higher in every year than forecast in March, by an average of £13bn",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"basis": "post-measures", "comparison": "October 2026 post-measures vs March 2026 forecast",
       "horizon": NEXT5, "statistic": "annual average", "sign_convention": SC_BORROW},
    model="arithmetic", norm=BN)
add("PR28", "paragraph 11", "£14.5bn", dec("14.5", 1e9),
    "the £14.5bn headroom left in 2029-30",
    "fiscal_headroom", "gbp", fy="2029-30",
    c={"rule": "current balance", "forecast_vintage": "October 2026, post-measures"},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("PR28", "paragraph 12", "£26 billion", dec("26", 1e9),
    "the current budget could turn out to be £26 billion in deficit in 2029-30",
    "current_budget_balance", "gbp", fy="2029-30",
    c={"sign_convention": "positive = current budget deficit",
       "scenario": "outturn misses the forecast by the typical gap between plans and outcomes outside major shocks"},
    model="arithmetic", norm=BN)
add("PR28", "paragraph 12", "about £2 billion", dec("2", 1e9),
    "about £2 billion of extra debt interest costs",
    "debt_interest_change", "gbp", period=2030, tb="fiscal_year",
    c={"scenario": "gilt yields at the peak of recent weeks, beyond the OBR's revisions",
       "horizon": "year not printed; the paragraph discusses 2029-30",
       "sign_convention": "positive = higher debt interest spending"},
    model="arithmetic", norm=BN, conf="medium")
add("PR28", "paragraph 14", "6.7 per cent", 6.7,
    "challenging real cuts worth 6.7 per cent – or £12bn in total",
    "real_spending_change", "percent", period=2032, tb="fiscal_year",
    c={"subgroup": "unprotected departments (e.g. Justice, Transport, Work and Pensions)",
       "horizon": "between now and the end of the forecast (2031-32)",
       "sign_convention": "positive = size of the real-terms cut"},
    model="arithmetic")
add("PR28", "paragraph 14", "£12bn", dec("12", 1e9),
    "challenging real cuts worth 6.7 per cent – or £12bn in total",
    "real_spending_change", "gbp", period=2032, tb="fiscal_year",
    c={"subgroup": "unprotected departments (e.g. Justice, Transport, Work and Pensions)",
       "horizon": "between now and the end of the forecast (2031-32)",
       "sign_convention": "positive = size of the real-terms cut"},
    model="arithmetic", norm=BN)
add("PR28", "paragraph 15", "£420", -420,
    "Real household disposable income (RHDI) per person is currently £420 lower",
    "real_income_change", "gbp", period=2026, tb="point_in_time",
    c={"statistic": "real household disposable income (RHDI) per person",
       "comparison": "now vs two years ago", "sign_convention": SC_GAIN},
    model="arithmetic", norm=LOSS)
add("PR28", "paragraph 16", "0.6 per cent", 0.6,
    "rise by an average of just 0.6 per cent a year",
    "real_income_growth", "percent", period=2029, tb="annual",
    c={"statistic": "RHDI per person, average annual growth", "horizon": "this Parliament (2024 to 2029)"},
    model="arithmetic")
add("PR28", "paragraph 16", "£776", 776,
    "(or £776 in total) over this Parliament",
    "real_income_change", "gbp", period=2029, tb="annual",
    c={"statistic": "RHDI per person", "horizon": "this Parliament (2024 to 2029)"},
    kind="cumulative", model="arithmetic")
add("PR28", "paragraph 16", "-0.4 per cent", -0.4,
    "when incomes fell by -0.4 per cent",
    "real_income_growth", "percent", period=2024, tb="annual",
    c={"statistic": "RHDI per person", "horizon": "the last Parliament (2019 to 2024)"},
    kind="cumulative", model="arithmetic", bench="administrative_fact")

# ===========================================================================
# PR29: press release, 29 October 2026 (Spread thin launch).
# ===========================================================================
add("PR29", "measures bullet 1", "£1,750", 1750,
    "Typical energy bills net of support are forecast to be £1,750 this year (2026-27)",
    "typical_energy_bill", "gbp", fy="2026-27", geo="GB",
    c={"household_type": "typical dual-fuel household",
       "scenario": "net of support, including the Household Energy Payment",
       "price_basis": "2026-27 prices (Spread thin Figure 7)"},
    model="arithmetic",
    note="Spread thin Figure 7: 'After rebate: £1,748' for 2026-27.")
add("PR29", "measures bullet 1", "£1,685", 1685,
    "the last energy price shock (2022-23) when net bills were £1,685",
    "typical_energy_bill", "gbp", fy="2022-23", geo="GB",
    c={"household_type": "typical dual-fuel household",
       "scenario": "net of support, after the 2022 £150 Council Tax rebate",
       "price_basis": "2026-27 prices (Spread thin Figure 7)"},
    model="arithmetic",
    note="Spread thin Figure 7 labels the same bill 'After rebate: £1,686' (workbook F7 M7 1686.1999).")
add("PR29", "measures bullet 2", "52 per cent", 0.52,
    "52 per cent of the whole cost of living package",
    "spending_share", "share", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "modelling_geography": F8_GEO},
    norm=PCT_SHARE, hint=COLA_PKG)
add("PR29", "measures bullet 2", "48 per cent", 0.48,
    "the other 48 per cent going to the top half",
    "spending_share", "share", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "modelling_geography": F8_GEO},
    norm=PCT_SHARE, hint=COLA_PKG)
add("PR29", "measures bullet 2", "under £145", 145,
    "under £145 on average for poorer households",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO},
    kind="range_high", hint=COLA_PKG)
add("PR29", "measures bullet 2", "over £130", 130,
    "compared to over £130 for richer households",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO},
    kind="range_low", hint=COLA_PKG)
add("PR29", "measures bullet 2", "less than £15", 15,
    "a gap of less than £15",
    "income_change_gap", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"comparison": "average gain of the poorer half minus that of the richer half",
       "horizon": TWO_YEARS, "unit_population": "households"},
    kind="range_high", hint=COLA_PKG)
add("PR29", "takeaways bullet 1", "£76 billion", dec("76", 1e9),
    "The £76 billion improvement in the UK’s primary balance",
    "primary_balance_change", "gbp", fy="2028-29",
    c={"horizon": "2023-24 to 2028-29", "sign_convention": "positive = improvement (towards surplus)"},
    model="arithmetic", norm=BN)
add("PR29", "takeaways bullet 1", "£107 billion", dec("107", 1e9),
    "more than fully accounted for by £107 billion of higher tax revenues",
    "tax_revenue_change", "gbp", fy="2028-29",
    c={"horizon": "2023-24 to 2028-29", "sign_convention": "positive = higher receipts"},
    model="arithmetic", norm=BN,
    note="Spread thin fn 53 computes it from receipts/GDP between 2023-24 and 2029-30 times 2029-30 GDP.")
add("PR29", "takeaways bullet 2", "£9 billion", dec("9", 1e9),
    "a £9 billion top up to departmental budgets over the current spending review period",
    "rdel_change", "gbp", period=2029, tb="fiscal_year", pk=P_RDEL,
    c={"horizon": "current Spending Review period (2026-27 to 2028-29)",
       "sign_convention": "positive = higher departmental spending"},
    kind="cumulative", model="arithmetic", norm=BN,
    hint="a £9 billion top up to departmental budgets")
add("PR29", "takeaways bullet 2", "£4.4 billion", dec("4.4", 1e9),
    "twice as much as the £4.4 billion cost of living support package",
    "revenue_change", "gbp", period=2027, tb="fiscal_year", mk=PKG,
    c={"sign_convention": SC_COST,
       "costing_basis": "Fuel Duty counted at the share accruing directly to households (Spread thin fn 19)",
       "horizon": "years not printed in the release (Spread thin p.19 prints '2025-26 and 2026-27')"},
    model="arithmetic", norm=BN, conf="medium", hint=COLA_PKG,
    note="Table 6.1 lines 1-3 sum to £5,040m over 2026-27 and 2027-28; RF counts about half the £1.4bn Fuel Duty cost (Spread thin p.5, fn 19).")
add("PR29", "takeaways bullet 3", "4.7 per cent", 4.7,
    "will fall to just 4.7 per cent of GDP by 2031-32",
    "rdel_share_of_gdp", "percent", fy="2031-32",
    c={"subgroup": "13 ‘unprotected’ departments",
       "scenario": "3 per cent defence target met and real health spending growing 2.6 per cent a year"},
    model="arithmetic")
add("PR29", "takeaways bullet 4", "2.9 per cent", 2.9,
    "raise public sector net investment to 2.9 per cent of GDP in 2027-28",
    "psni_share_of_gdp", "percent", fy="2027-28", att="restated", model="obr_efo_forecast",
    note=RESTATED_OBR + " (the level set by Rachel Reeves's first Budget).")
add("PR29", "takeaways bullet 4", "2.3 per cent", 2.3,
    "falling to 2.3 per cent in 2031-32",
    "psni_share_of_gdp", "percent", fy="2031-32", att="restated", model="obr_efo_forecast",
    note=RESTATED_OBR + ".")
add("PR29", "takeaways bullet 4", "2.5 per cent", 2.5,
    "(2.5 per cent in 2023-24)",
    "psni_share_of_gdp", "percent", fy="2023-24", att="restated", model="administrative_data",
    bench="administrative_fact", note="Outturn inherited from Jeremy Hunt.")
add("PR29", "takeaways bullet 5", "£600", 600,
    "set to grow by a paltry £600 over the course of the Parliament",
    "real_income_change", "gbp", fy="2028-29",
    c={"statistic": "median real annual disposable income", "unit_population": "working-age (non-pensioner) households",
       "housing_costs": "ahc", "horizon": "2023-24 to 2028-29", "price_basis": "2026-27 prices"},
    kind="cumulative")
add("PR29", "takeaways bullet 5", "£1,050", -1050,
    "typical incomes are forecast to fall in total by £1,050 (3 per cent)",
    "real_income_change", "gbp", fy="2028-29",
    c={"statistic": "median real annual disposable income", "unit_population": "working-age (non-pensioner) households",
       "housing_costs": "ahc", "horizon": "2026-27 to 2028-29", "price_basis": "2026-27 prices",
       "sign_convention": SC_GAIN},
    kind="cumulative", norm=LOSS)
add("PR29", "takeaways bullet 5", "3 per cent", -3,
    "typical incomes are forecast to fall in total by £1,050 (3 per cent)",
    "real_income_growth", "percent", fy="2028-29",
    c={"statistic": "median real annual disposable income", "unit_population": "working-age (non-pensioner) households",
       "housing_costs": "ahc", "horizon": "2026-27 to 2028-29", "sign_convention": SC_GAIN},
    kind="cumulative", norm=LOSS)
add("PR29", "Ruth Curtice quote, paragraph 3", "£1,000", -1000,
    "a projected £1,000 fall in disposable incomes",
    "real_income_change", "gbp", fy="2028-29",
    c={"statistic": "typical disposable income", "horizon": "second half of the Parliament (2026-27 to 2028-29)",
       "sign_convention": SC_GAIN},
    kind="cumulative", norm=LOSS, conf="medium",
    note="A rounded restatement of the £1,050 fall in bullet 5.")

# ===========================================================================
# LAND: Spread thin publication page (summary and key findings).
# ===========================================================================
add("LAND", "summary paragraph 2", "£147 billion", dec("147", 1e9),
    "pushed the forecast debt interest bill up to £147 billion in 2029-30",
    "debt_interest_spending", "gbp", fy="2029-30", att="restated", model="obr_efo_forecast",
    norm=BN, note=RESTATED_OBR + ".")
add("LAND", "summary paragraph 2", "£13 billion", dec("13", 1e9),
    "£13 billion more than in March",
    "debt_interest_change", "gbp", fy="2029-30",
    c={"comparison": "October 2026 vs March 2026 OBR forecast",
       "sign_convention": "positive = higher debt interest spending"},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("LAND", "summary paragraph 2", "£14.5 billion", dec("14.5", 1e9),
    "leaves the Government with just £14.5 billion of headroom",
    "fiscal_headroom", "gbp", fy="2029-30",
    c={"rule": "current balance", "forecast_vintage": "October 2026, post-measures"},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("LAND", "summary paragraph 2", "about three-fifths", 0.6,
    "about three-fifths of its March level",
    "headroom_share_of_previous", "share", fy="2029-30",
    c={"denominator": "headroom after the March 2026 Spring Forecast (£23.6bn)"},
    model="arithmetic", norm="'three-fifths' → 0.6")
add("LAND", "summary paragraph 2", "£3.7 billion", dec("3.7", 1e9),
    "A £3.7 billion package of new household support",
    "revenue_change", "gbp", period=2028, tb="fiscal_year", pk=P_HEP_VAT,
    c={"sign_convention": SC_COST, "horizon": "2026-27 and 2027-28 (Spread thin p.17: £3.4bn and £0.3bn)"},
    kind="cumulative", model="arithmetic", norm=BN,
    hint="the Household Energy Payment and the electricity VAT cut",
    note="Table 6.1 lines 1 and 2 sum to £3,685m over 2026-27 and 2027-28.")
add("LAND", "summary paragraph 2", "just over half", 0.5,
    "only just over half of measures announced by Burnham and Healey",
    "spending_share", "share", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS},
    kind="range_low", norm="'half' → 0.5 (lower bound)", conf="medium", hint=COLA_PKG,
    note="The sentence is about cost of living support; Spread thin p.19 puts the poorer half's share at 52 per cent.")
add("LAND", "summary paragraph 3", "3.0 per cent", -3.0,
    "Typical non-pensioner incomes are now set to fall by 3.0 per cent (£1,050)",
    "real_income_growth", "percent", fy="2028-29",
    c={"statistic": "median", "unit_population": "non-pensioners", "housing_costs": "ahc",
       "horizon": "2026-27 to 2028-29", "sign_convention": SC_GAIN},
    kind="cumulative", norm=LOSS)
add("LAND", "summary paragraph 3", "£1,050", -1050,
    "Typical non-pensioner incomes are now set to fall by 3.0 per cent (£1,050)",
    "real_income_change", "gbp", fy="2028-29",
    c={"statistic": "median", "unit_population": "non-pensioners", "housing_costs": "ahc",
       "horizon": "2026-27 to 2028-29", "price_basis": "2026-27 prices", "sign_convention": SC_GAIN},
    kind="cumulative", norm=LOSS)
add("LAND", "Key findings bullet 1", "£12 billion", dec("12", 1e9),
    "have pushed up borrowing by an average of £12 billion a year",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"component": "higher debt interest payments", "basis": "pre-measures",
       "horizon": "2026-27 to 2030-31", "statistic": "annual average", "sign_convention": SC_BORROW},
    model="arithmetic", norm=BN)
add("LAND", "Key findings bullet 1", "4.1 per cent", 4.1,
    "debt interest spending reaching £147 billion (4.1 per cent of GDP) in 2029-30",
    "debt_interest_share_of_gdp", "percent", fy="2029-30", att="restated", model="obr_efo_forecast",
    note=RESTATED_OBR + ".")
add("LAND", "Key findings bullet 2", "62 per cent", 0.62,
    "only around three-fifths (62 per cent) of its March level",
    "headroom_share_of_previous", "share", fy="2029-30",
    c={"denominator": "headroom after the March 2026 Spring Forecast (£23.6bn)"},
    model="arithmetic", norm=PCT_SHARE)
add("LAND", "Key findings bullet 3", "£4.4 billion", dec("4.4", 1e9),
    "The £4.4 billion cost of living package is poorly targeted",
    "revenue_change", "gbp", period=2027, tb="fiscal_year", mk=PKG,
    c={"sign_convention": SC_COST,
       "costing_basis": "Fuel Duty counted at the share accruing directly to households (Spread thin fn 19)",
       "horizon": "years not printed on the page (Spread thin p.19 prints '2025-26 and 2026-27')"},
    model="arithmetic", norm=BN, conf="medium", hint=COLA_PKG)
add("LAND", "Key findings bullet 3", "up to 20 million", dec("20", 1e6),
    "the Household Energy Payment goes to up to 20 million households in England",
    "eligible_count", "households", fy="2026-27", mk=HEP, geo="England",
    kind="range_high", model="administrative_data", bench="administrative_fact",
    norm="million × 1e6")
add("LAND", "Key findings bullet 3", "£158", 158,
    "the poorer half of the income distribution gains £158 on average",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO,
       "document_version": "page text at fetch time; matches Spread thin v1, not v2"},
    hint=COLA_PKG,
    note="The PDF this page links (Spread-thin.pdf, v2) prints £145 for the poorer half and £130 for the richer half; the page still printed v1's £158 / £144 when fetched.")
add("LAND", "Key findings bullet 3", "£144", 144,
    "against £144 for the richer half",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO,
       "document_version": "page text at fetch time; matches Spread thin v1, not v2"},
    hint=COLA_PKG,
    note="Spread thin v2 prints £130 for the richer half.")
add("LAND", "Key findings bullet 4", "over a million", dec("1", 1e6),
    "over a million private renting families lose out",
    "gainer_count", "families", fy="2027-28", pk=O_LHA, geo="England",
    c={"unit_population": "private renting families (benefit units)",
       "framing": "RF: lose out from prolonging the LHA freeze into 2027-28; they would gain if LHA were unfrozen"},
    kind="range_low", norm="'a million' → 1,000,000 (lower bound)",
    hint="Prolonging the Local Housing Allowance freeze into 2027-28",
    note="Geography and year from Spread thin Figure 9 (England, 2027-28); workbook F9 M22 counts 1,572,152.")
add("LAND", "Key findings bullet 4", "91 per cent", 0.91,
    "91 per cent of whom are in the bottom half of the income distribution",
    "affected_share", "share", fy="2027-28", pk=O_LHA, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS,
       "denominator": "private renting families who lose out from the prolonged LHA freeze"},
    norm=PCT_SHARE, hint="Prolonging the Local Housing Allowance freeze into 2027-28")
add("LAND", "Key findings bullet 5", "2.6 percentage points", -2.6,
    "child poverty is still set to fall by 2.6 percentage points across this Parliament",
    "poverty_rate_change", "percentage_points", fy="2028-29",
    c={"unit_population": "children", "housing_costs": "ahc", "poverty_line": "relative_60_median",
       "horizon": "2023-24 to 2028-29", "sign_convention": "positive = rise in the poverty rate"},
    kind="cumulative", norm="printed as a fall; carried negative")

# ===========================================================================
# V1: the first Spread thin PDF (Spread-thin-1.pdf). Only the passages the
# replacement changed are staged from it; every other figure is staged from V2.
# ===========================================================================
V1_NOTE = ("Superseded: Spread thin v2 (Spread-thin.pdf) replaced these figures with £145 / £15 / £130 "
           "the same morning. Staged so the first published version is on record.")
add("V1", "p.5, paragraph 4", "£158", 158,
    "the poorest half gain on average £158 from the cost of living measures",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO,
       "document_version": "v1 (superseded)"},
    hint=COLA_PKG, note=V1_NOTE)
add("V1", "p.5, paragraph 4", "£14", 14,
    "a paltry £14 more than the £144 in giveaways enjoyed by the top half",
    "income_change_gap", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"comparison": "average gain of the poorer half minus that of the richer half",
       "horizon": TWO_YEARS, "unit_population": "households", "document_version": "v1 (superseded)"},
    hint=COLA_PKG, note=V1_NOTE)
add("V1", "p.5, paragraph 4", "£144", 144,
    "a paltry £14 more than the £144 in giveaways enjoyed by the top half",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO,
       "document_version": "v1 (superseded)"},
    hint=COLA_PKG, note=V1_NOTE)

# ===========================================================================
# V2: the replaced Spread thin PDF (Spread-thin.pdf), the version the landing
# page links. Page numbers are the PDF's (they match the printed folios).
# A number printed twice with the same meaning is staged once, at the
# occurrence that states its period or scope most completely.
# ===========================================================================
add("V2", "p.3, Summary paragraph 2", "£7 billion", dec("7", 1e9),
    "the absolute value of giveaways and clawbacks totted up to just £7 billion",
    "absolute_policy_change", "gbp", fy="2031-32", pk=P_ABSOLUTE,
    c={"statistic": "sum of the absolute values of giveaways and clawbacks (RF's fiscal-event size measure)",
       "horizon": "year not printed; the 28 October release says 'by the end of the forecast'"},
    model="arithmetic", norm=BN, conf="medium",
    hint="giveaways and clawbacks", note="Year read as 2031-32, the forecast's final year.")
add("V2", "p.3, Summary paragraph 5", "around £2 billion", dec("2", 1e9),
    "it would have added around £2 billion in extra debt interest costs",
    "debt_interest_change", "gbp", period=2030, tb="fiscal_year",
    c={"scenario": "fiscal forecasts read at the recent peak of gilt rates",
       "horizon": "year not printed", "sign_convention": "positive = higher debt interest spending"},
    model="arithmetic", norm=BN, conf="medium")
add("V2", "p.4, paragraph 3", "about £5 billion", dec("5", 1e9),
    "he has brought in an average of about £5 billion annually from next year",
    "revenue_change", "gbp", period=2032, tb="fiscal_year", pk=P_OBR_TAX,
    c={"sign_convention": SC_YIELD, "statistic": "annual average",
       "horizon": "2027-28 to 2031-32 (from next year)"},
    model="arithmetic", norm=BN, hint="On the tax side",
    note="Workbook F10 C57-C58: the average of the OBR's direct effect of tax measures over 2027-28 to 2031-32 is 4.65, 'rounded' to 5.")
add("V2", "p.4, paragraph 3", "over £3 billion", dec("3", 1e9),
    "bringing over £3 billion annually by 2030-31",
    "revenue_change", "gbp", fy="2030-31", pk=P_OBR_ADMIN,
    c={"sign_convention": SC_YIELD},
    kind="range_low", model="arithmetic", norm=BN, conf="medium",
    hint="a range of technical measures to close the ‘tax gap’",
    note="Workbook F10 row 52 (OBR 'Tax administration, compliance and debt collection') has 2.89 in 2030-31 and 3.64 in 2031-32, so 'over £3 billion' holds from 2031-32.")
add("V2", "p.4, paragraph 4", "around £100", 100,
    "around £100 higher than anticipated when the Treasury initially did the Spending Review",
    "real_rdel_per_person_change", "gbp", period=2029, tb="fiscal_year",
    c={"comparison": "October 2026 forecast vs Spending Review 2025 plans",
       "statistic": "real-terms RDEL per person", "horizon": "year not printed (the current Spending Review period)"},
    model="arithmetic", conf="medium")
add("V2", "p.5, paragraph 1", "5.4 per cent", 5.4,
    "will dwindle from 5.4 per cent of GDP this year to 4.7 per cent",
    "rdel_share_of_gdp", "percent", fy="2026-27",
    c={"subgroup": "unprotected areas (including justice, local government and jobcentres)"},
    model="arithmetic")
add("V2", "p.5, paragraph 1", "4.7 per cent", 4.7,
    "to 4.7 per cent of GDP in 2031-32",
    "rdel_share_of_gdp", "percent", fy="2031-32",
    c={"subgroup": "unprotected areas (including justice, local government and jobcentres)",
       "scenario": "the Chancellor sticks to his overall plans"},
    model="arithmetic")
add("V2", "p.5, paragraph 2", "£80 million", dec("80", 1e6),
    "This comes with a modest £80 million cost by 2031-32",
    "revenue_change", "gbp", fy="2031-32", mk=CA, c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=M,
    hint="eliminate the benefit ‘cliff edge’ for unpaid carers in receipt of Carer’s Allowance",
    note=RESTATED_HMT + " line 7 (-£80m in 2031-32).")
add("V2", "p.5, paragraph 4", "20 million", dec("20", 1e6),
    "the vast majority (20 million) of English households",
    "eligible_count", "households", fy="2026-27", mk=HEP, geo="England",
    model="administrative_data", bench="administrative_fact", norm="million × 1e6",
    hint="a £100 money-back scheme for homes in Council Tax bands A to D")
add("V2", "p.5, paragraph 4", "around half", 0.5,
    "where only around half the £1.4 billion cost directly goes to households",
    "incidence_share", "share", period=2028, tb="fiscal_year", mk=FD,
    c={"subgroup": "households (direct effect)", "horizon": "2026-27 and 2027-28"},
    model="arithmetic", norm="'half' → 0.5", hint="yet another costly freezing of Fuel Duty")
add("V2", "p.5, paragraph 4", "£145", 145,
    "the poorest half gain on average £145 from the cost of living measures",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO,
       "price_basis": "cash terms (Figure 8)"},
    hint=COLA_PKG,
    note="v1 printed £158 here; p.19 prints 'under £145'.")
add("V2", "p.5, paragraph 4", "£15", 15,
    "a paltry £15 more than the £130 in giveaways enjoyed by the top half",
    "income_change_gap", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"comparison": "average gain of the poorer half minus that of the richer half",
       "horizon": TWO_YEARS, "unit_population": "households"},
    hint=COLA_PKG, note="v1 printed £14 here.")
add("V2", "p.5, paragraph 4", "£130", 130,
    "a paltry £15 more than the £130 in giveaways enjoyed by the top half",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "unit_population": "households", "sign_convention": SC_GAIN, "modelling_geography": F8_GEO,
       "price_basis": "cash terms (Figure 8)"},
    hint=COLA_PKG, note="v1 printed £144 here.")
add("V2", "p.6, paragraph 2", "76 per cent", 0.76,
    "We estimate that three-quarters (76 per cent) of the private renter households",
    "affected_share", "share", fy="2027-28", mk=YFH, geo="England",
    c={"income_group": "top_half", "income_axis": HALF_AXIS,
       "denominator": "private renter households with the resources to access Your First Home"},
    norm=PCT_SHARE, hint="The Chancellor’s ‘Your First Home’ deposit scheme",
    note="Year and geography from Figure 9 (England, 2027-28); workbook F9 N20 0.762.")
add("V2", "p.8, paragraph 1", "£11 billion", dec("11", 1e9),
    "raised the OBR’s ‘pre-measures’ borrowing forecast by £11 billion a year on average",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"basis": "pre-measures", "comparison": "October 2026 vs March 2026 OBR forecast",
       "horizon": NEXT5, "statistic": "annual average", "sign_convention": SC_BORROW},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("V2", "p.8, paragraph 1", "97 per cent", 97,
    "public sector net debt to peak at 97 per cent of GDP in 2028-29",
    "psnd_share_of_gdp", "percent", fy="2028-29", c={"basis": "pre-measures"},
    att="restated", model="obr_efo_forecast", note=RESTATED_OBR + ", before measures.")
add("V2", "p.8, paragraph 2", "£4 billion", dec("-4", 1e9),
    "reduced average borrowing by £4 billion",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"component": "higher prices (receipts rise more than uprated spending)", "basis": "pre-measures",
       "horizon": "average over the forecast", "statistic": "annual average", "sign_convention": SC_BORROW},
    att="restated", model="obr_efo_forecast", norm=BN + "; 'reduced' → negative",
    note=RESTATED_OBR + " ('In the OBR’s reckoning').")
add("V2", "p.8, paragraph 2", "£2.5 billion", dec("2.5", 1e9),
    "which pushed up borrowing by an average of £2.5 billion",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"component": "weaker growth", "basis": "pre-measures",
       "horizon": "average over the forecast", "statistic": "annual average", "sign_convention": SC_BORROW},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("V2", "p.9, paragraph 1", "£12 billion", dec("12", 1e9),
    "pushed up borrowing by an average of £12 billion between 2026-27 and 2030-31",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"component": "higher debt interest payments", "basis": "pre-measures",
       "horizon": "2026-27 to 2030-31", "statistic": "annual average", "sign_convention": SC_BORROW},
    model="arithmetic", norm=BN, note="RF's decomposition (Figure 2).")
add("V2", "p.9, paragraph 3", "£110 billion", dec("110", 1e9),
    "£110 billion in 2025-26",
    "debt_interest_spending", "gbp", fy="2025-26", att="restated", model="obr_efo_forecast",
    norm=BN, note=RESTATED_OBR + ".")
add("V2", "p.10, paragraph 1", "£147 billion", dec("147", 1e9),
    "debt interest spending is now forecast to reach £147 billion in 2029-30",
    "debt_interest_spending", "gbp", fy="2029-30", att="restated", model="obr_efo_forecast",
    norm=BN, note=RESTATED_OBR + " (central government debt interest, net of the APF; fn 2).")
add("V2", "p.10, paragraph 1", "£13 billion", dec("13", 1e9),
    "£13 billion more than in March",
    "debt_interest_change", "gbp", fy="2029-30",
    c={"comparison": "October 2026 vs March 2026 OBR forecast",
       "sign_convention": "positive = higher debt interest spending"},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("V2", "p.10, paragraph 1", "4.1 per cent", 4.1,
    "This leaves debt interest spending at 4.1 per cent of GDP in 2029-30",
    "debt_interest_share_of_gdp", "percent", fy="2029-30", att="restated", model="obr_efo_forecast",
    note=RESTATED_OBR + ".")
add("V2", "p.10, paragraph 1", "4.14 per cent", 4.14,
    "peaking marginally higher at 4.14 per cent in 2031-32",
    "debt_interest_share_of_gdp", "percent", fy="2031-32", att="restated", model="obr_efo_forecast",
    note=RESTATED_OBR + "; RF adds 'the highest on record since 1956-57'.")
add("V2", "p.12, paragraph 1", "£1,040", 1040,
    "will be worth £1,040 a year for someone working 40 hours a week",
    "annual_earnings_change", "gbp", fy="2027-28", pk=P_MIN_WAGE,
    c={"household_type": "adult minimum wage worker, 40 hours a week"}, model="arithmetic",
    hint="minimum wage rates from April 2027: the adult rate up 50p (3.9 per cent) to £13.21, youth rates up 3.9 per cent")
add("V2", "p.13, paragraph 1", "1.4 per cent", 1.4,
    "projected to rise by just 1.4 per cent in total over the decade",
    "real_income_growth", "percent", period=2030, tb="annual",
    c={"statistic": "real household disposable income (RHDI) per person", "horizon": "the 2020s"},
    kind="cumulative", model="arithmetic", note="ONS outturn and the OBR's October 2026 forecast (Figure 5).")
add("V2", "p.13, paragraph 1", "£400", 400,
    "(equivalent to £400 in 2026-27 prices)",
    "real_income_change", "gbp", period=2030, tb="annual",
    c={"statistic": "real household disposable income (RHDI) per person", "horizon": "the 2020s",
       "price_basis": "2026-27 prices"},
    kind="cumulative", model="arithmetic")
add("V2", "p.16, Box 2", "£6.7 billion", dec("-6.7", 1e9),
    "a receipts shortfall of around £6.7 billion in 2029-30",
    "forecast_revenue_change", "gbp", fy="2029-30",
    c={"component": "lower net migration", "sign_convention": "positive = higher receipts"},
    model="arithmetic", norm=BN + "; 'shortfall' → negative",
    note="RF applies the OBR's March 2024 Box 4.5 migrant fiscal contribution; p.15 rounds it to '£7 billion in 2029-30'.")
add("V2", "p.16, Box 2", "60 per cent", 0.6,
    "or around 60 per cent of the pre-measures fall in headroom",
    "share_of_headroom_change", "share", fy="2029-30",
    c={"component": "lower net migration"}, model="arithmetic", norm=PCT_SHARE)
add("V2", "p.16, section heading", "£3.7 billion", dec("3.7", 1e9),
    "A £3.7 billion package of household support will take the edge off",
    "revenue_change", "gbp", period=2028, tb="fiscal_year", pk=P_HEP_VAT,
    c={"sign_convention": SC_COST, "horizon": "2026-27 and 2027-28 (p.17: £3.4bn and £0.3bn)"},
    kind="cumulative", model="arithmetic", norm=BN,
    hint="a £100 Household Energy Payment and a three-month extension of the VAT cut",
    note="Table 6.1 lines 1 and 2 sum to £3,685m over 2026-27 and 2027-28.")
add("V2", "p.16, paragraph 1", "27 per cent", 27,
    "jump by more than a quarter (27 per cent) from its Q4 2026 value",
    "average_energy_bill_change", "percent", period=2027, tb="point_in_time", geo="GB",
    c={"comparison": "Q1 2027 Energy Price Cap vs Q4 2026", "household_type": "typical dual-fuel household",
       "sign_convention": "positive = higher bills"},
    model="arithmetic", note="RF analysis of EDF price cap predictions (fn 10).")
add("V2", "p.16, paragraph 1", "£2,192", 2192,
    "to reach £2,192 in Q1 2027",
    "typical_energy_bill", "gbp", period=2027, tb="point_in_time", geo="GB",
    c={"household_type": "typical dual-fuel household (Ofgem TDCV: 9,500 kWh gas, 2,500 kWh electricity)",
       "basis": "Energy Price Cap, annualised, Q1 2027"},
    model="arithmetic",
    note="p.5 describes the same £2,192 as the bill 'next year'; the 28 October release gives £2,210 as the 2027 average.")
add("V2", "p.16, paragraph 1", "£608", 608,
    "£608 (38 per cent) higher than a year earlier",
    "average_energy_bill_change", "gbp", period=2027, tb="point_in_time", geo="GB",
    c={"comparison": "Q1 2027 vs Q1 2026", "household_type": "typical dual-fuel household",
       "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.16, paragraph 1", "38 per cent", 38,
    "£608 (38 per cent) higher than a year earlier",
    "average_energy_bill_change", "percent", period=2027, tb="point_in_time", geo="GB",
    c={"comparison": "Q1 2027 vs Q1 2026", "household_type": "typical dual-fuel household",
       "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.17, paragraph 1", "£12", 12,
    "worth £12 to a household with typical levels of electricity consumption",
    "energy_bill_change", "gbp", fy="2027-28", mk=VAT, geo="GB",
    c={"household_type": "household with typical electricity consumption",
       "component": "three-month extension of the VAT cut (April to 1 July 2027)",
       "row_type": "measure_component",
       "sign_convention": "positive = saving (a reduction in the bill)"},
    model="arithmetic", hint="a three-month extension to the VAT cut on electricity bills",
    note="The extension covers April to June 2027. Workbook F7 H12 has the whole cut at 12.80 in 2027-28 (2026-27 prices).")
add("V2", "p.17, paragraph 1", "£40", 40,
    "taking the total nine-month benefit of the cut to £40",
    "energy_bill_change", "gbp", period=2028, tb="fiscal_year", mk=VAT, geo="GB",
    c={"household_type": "household with typical electricity consumption",
       "horizon": "1 October 2026 to 1 July 2027 (nine months)",
       "sign_convention": "positive = saving (a reduction in the bill)"},
    kind="cumulative", model="arithmetic", hint="the total nine-month benefit of the cut",
    note="The whole cut, i.e. Table 6.1 line 2's span (workbook F7: 26.77 in 2026-27 plus 12.80 in 2027-28).")
add("V2", "p.17, paragraph 2", "£3.4 billion", dec("3.4", 1e9),
    "Together, these measures cost £3.4 billion in 2026-27",
    "revenue_change", "gbp", fy="2026-27", pk=P_HEP_VAT, c={"sign_convention": SC_COST},
    model="arithmetic", norm=BN, hint="a £100 Household Energy Payment and a three-month extension of the VAT cut",
    note="Table 6.1 lines 1 and 2 in 2026-27 sum to £3,380m, so the £3.4bn includes the whole VAT cut, not only the extension.")
add("V2", "p.17, paragraph 2", "45 per cent", 0.45,
    "more than two-fifths (45 per cent) of the total £7.6 billion cost",
    "share_of_total_policy_cost", "share", fy="2026-27", pk=P_HEP_VAT,
    c={"denominator": "the total cost of Budget decisions in 2026-27 (£7.6bn)"},
    model="arithmetic", norm=PCT_SHARE)
add("V2", "p.17, paragraph 2", "£7.6 billion", dec("7.6", 1e9),
    "the total £7.6 billion cost of Budget decisions this year",
    "revenue_change", "gbp", fy="2026-27", mk=TOTAL, c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=BN,
    note=RESTATED_HMT + " total policy decisions (-£7,595m in 2026-27).")
add("V2", "p.17, paragraph 2", "£0.3 billion", dec("0.3", 1e9),
    "a further £0.3 billion in 2027-28",
    "revenue_change", "gbp", fy="2027-28", pk=P_HEP_VAT, c={"sign_convention": SC_COST},
    model="arithmetic", norm=BN, note="Table 6.1 lines 1 and 2 in 2027-28: £0m and £305m.")
add("V2", "p.17, bullet 1", "£363", 363,
    "real-terms spending on energy is forecast to rise by £363 this year",
    "average_energy_bill_change", "gbp", fy="2026-27", geo="GB",
    c={"household_type": "typical household", "scenario": "before any support",
       "price_basis": "2026-27 prices (fn 13)", "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.17, bullet 2", "£217", 217,
    "brings that increase down to £217",
    "average_energy_bill_change", "gbp", fy="2026-27", geo="GB",
    c={"household_type": "typical household", "scenario": "after support announced before this Budget",
       "price_basis": "2026-27 prices (fn 13)", "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.17, bullet 2", "£1,848", 1848,
    "(£1,848 compared with £1,860)",
    "typical_energy_bill", "gbp", fy="2026-27", geo="GB",
    c={"household_type": "typical household", "scenario": "after support announced before this Budget only",
       "price_basis": "2026-27 prices (fn 13)"},
    model="arithmetic")
add("V2", "p.17, bullet 2", "£1,860", 1860,
    "(£1,848 compared with £1,860)",
    "typical_energy_bill", "gbp", fy="2022-23", geo="GB",
    c={"household_type": "typical household", "scenario": "net of 2022-23 support, before the £150 Council Tax rebate",
       "price_basis": "2026-27 prices (fn 13)"},
    model="arithmetic")
add("V2", "p.17, bullet 3", "£62", 62,
    "will typically still pay £62 more for energy this year than in 2022-23",
    "average_energy_bill_change", "gbp", fy="2026-27", geo="England",
    c={"subgroup": "households in Council Tax bands A to D in England",
       "comparison": "2026-27 vs 2022-23, each after its Council Tax rebate",
       "price_basis": "2026-27 prices (fn 13)", "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.17, bullet 4", "£358", 358,
    "set to rise by a further £358 (20 per cent) in 2027-28",
    "average_energy_bill_change", "gbp", fy="2027-28", geo="GB",
    c={"subgroup": "households set to receive the £100 rebate", "comparison": "2027-28 vs 2026-27",
       "price_basis": "2026-27 prices (fn 13)", "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.17, bullet 4", "20 per cent", 20,
    "set to rise by a further £358 (20 per cent) in 2027-28",
    "average_energy_bill_change", "percent", fy="2027-28", geo="GB",
    c={"subgroup": "households set to receive the £100 rebate", "comparison": "2027-28 vs 2026-27",
       "sign_convention": "positive = higher bills"},
    model="arithmetic")
add("V2", "p.17, fn 12", "£7", 7,
    "this will only save the typical household £7 in 2027-28",
    "energy_bill_change", "gbp", fy="2027-28", pk=P_GSL, geo="GB",
    c={"household_type": "typical household", "sign_convention": "positive = saving (a reduction in the bill)"},
    model="arithmetic", hint="the Gas Supplier Levy would be funded through general taxation")
add("V2", "p.18, Figure 7 annotation (2022-23)", "£1,686", 1686,
    "After rebate: £1,686",
    "typical_energy_bill", "gbp", fy="2022-23", geo="GB",
    c={"household_type": "typical dual-fuel household", "scenario": "net of support, after the 2022 Council Tax rebate",
       "price_basis": "2026-27 prices"},
    model="arithmetic", table=FIG[7], col="Net bill after Council Tax rebate, 2022-23")
add("V2", "p.18, Figure 7 annotation (2026-27)", "£1,748", 1748,
    "After rebate: £1,748",
    "typical_energy_bill", "gbp", fy="2026-27", geo="GB",
    c={"household_type": "typical dual-fuel household", "scenario": "net of support, after the Household Energy Payment",
       "price_basis": "2026-27 prices"},
    model="arithmetic", table=FIG[7], col="Net bill after Council Tax rebate, 2026-27")
GAS = dict(pk=P_GAS_SC, geo="GB", model="survey_microdata",
           hint="scrap the gas standing charge, moving the £108 a year paid by the typical household onto unit rates (Q4 2026 price cap)")
add("V2", "p.18, paragraph 1", "around one-tenth", 10,
    "raise gas unit rates by around one-tenth",
    "unit_rate_change", "percent", period=2026, tb="point_in_time",
    c={"basis": "Q4 2026 price cap"}, norm="'one-tenth' → 10 per cent", **GAS)
GAS_C = {"denominator": "gas-connected households", "timing": "by the end of 2027 or soon after"}
add("V2", "p.18, paragraph 1", "57 per cent", 0.57,
    "57 per cent of gas-connected households (13.3 million) would be better off",
    "share_gaining", "share", period=2028, tb="fiscal_year", c=GAS_C, norm=PCT_SHARE, **GAS)
add("V2", "p.18, paragraph 1", "13.3 million", dec("13.3", 1e6),
    "57 per cent of gas-connected households (13.3 million) would be better off",
    "gainer_count", "households", period=2028, tb="fiscal_year", c=GAS_C, norm="million × 1e6", **GAS)
add("V2", "p.18, paragraph 1", "£46", 46,
    "would be better off, by £46 a year on average",
    "average_annual_gain", "gbp", period=2028, tb="fiscal_year",
    c=dict(GAS_C, subgroup="households better off"), **GAS)
add("V2", "p.18, paragraph 1", "43 per cent", 0.43,
    "and 43 per cent (9.9 million) worse off, by an average of £61",
    "share_losing", "share", period=2028, tb="fiscal_year", c=GAS_C, norm=PCT_SHARE, **GAS)
add("V2", "p.18, paragraph 1", "9.9 million", dec("9.9", 1e6),
    "and 43 per cent (9.9 million) worse off, by an average of £61",
    "affected_count", "households", period=2028, tb="fiscal_year",
    c=dict(GAS_C, subgroup="households worse off"), norm="million × 1e6", **GAS)
add("V2", "p.18, paragraph 1", "£61", -61,
    "and 43 per cent (9.9 million) worse off, by an average of £61",
    "average_household_income_change", "gbp", period=2028, tb="fiscal_year",
    c=dict(GAS_C, subgroup="households worse off", sign_convention=SC_GAIN), norm=LOSS, **GAS)
add("V2", "p.18, paragraph 2", "50 per cent", 0.5,
    "half (50 per cent) of all households in the poorer half",
    "share_gaining", "share", period=2028, tb="fiscal_year",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "denominator": "all households in the group"},
    norm=PCT_SHARE, **GAS)
add("V2", "p.18, paragraph 2", "46 per cent", 0.46,
    "compared with 46 per cent in the richer half",
    "share_gaining", "share", period=2028, tb="fiscal_year",
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "denominator": "all households in the group"},
    norm=PCT_SHARE, **GAS)
add("V2", "p.19, paragraph 1", "38 per cent", 0.38,
    "just 38 per cent of households with two children",
    "share_gaining", "share", period=2028, tb="fiscal_year",
    c={"household_type": "households with two children"}, norm=PCT_SHARE, **GAS)
add("V2", "p.19, paragraph 1", "31 per cent", 0.31,
    "and 31 per cent of those with three or more, will be better off",
    "share_gaining", "share", period=2028, tb="fiscal_year",
    c={"household_type": "households with three or more children"}, norm=PCT_SHARE, **GAS)
add("V2", "p.19, paragraph 1", "50 per cent", 0.5,
    "compared with 50 per cent of households without children",
    "share_gaining", "share", period=2028, tb="fiscal_year",
    c={"household_type": "households without children"}, norm=PCT_SHARE, **GAS)
add("V2", "p.19, paragraph 2", "£1.4 billion", dec("1.4", 1e9),
    "together costing just under £1.4 billion",
    "revenue_change", "gbp", period=2028, tb="fiscal_year", mk=FD,
    c={"sign_convention": SC_COST, "horizon": "2026-27 and 2027-28"},
    kind="range_high", att="restated", model="hmt_costing_obr_certified", norm=BN,
    hint="delayed the reversal of the 5p cut to Fuel Duty and April’s RPI uprating until July 2027",
    note=RESTATED_HMT + " line 3 (-£575m and -£780m, £1,355m together).")
add("V2", "p.19, paragraph 3", "£4.4 billion", dec("4.4", 1e9),
    "the Government’s £4.4 billion cost of living package for 2025-26 and 2026-27",
    "revenue_change", "gbp", period=2027, tb="fiscal_year", mk=PKG,
    c={"sign_convention": SC_COST,
       "costing_basis": "Fuel Duty counted at the share accruing directly to households (fn 19)",
       "horizon": "2025-26 and 2026-27 (as printed)"},
    model="arithmetic", norm=BN, conf="medium", hint=COLA_PKG,
    note="The years look misprinted: the measures fall in 2026-27 and 2027-28 (Table 6.1 lines 1-3). Period kept as printed.")
add("V2", "p.19, paragraph 3", "87 per cent", 0.87,
    "87 per cent of the bottom half of the income distribution",
    "eligibility_rate", "share", fy="2026-27", mk=HEP, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS,
       "subgroup": "live in Council Tax bands A-D"},
    model="survey_microdata", norm=PCT_SHARE, hint="The Household Energy Payment")
add("V2", "p.19, paragraph 3", "73 per cent", 0.73,
    "and 73 per cent of the top live in Council Tax bands A-D",
    "eligibility_rate", "share", fy="2026-27", mk=HEP, geo="England",
    c={"income_group": "top_half", "income_axis": HALF_AXIS,
       "subgroup": "live in Council Tax bands A-D"},
    model="survey_microdata", norm=PCT_SHARE, hint="The Household Energy Payment")
add("V2", "p.19, paragraph 3", "52 per cent", 0.52,
    "we estimate that 52 per cent of the whole cost of living package",
    "spending_share", "share", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "modelling_geography": F8_GEO},
    norm=PCT_SHARE, hint=COLA_PKG)
add("V2", "p.19, paragraph 3", "48 per cent", 0.48,
    "with the other 48 per cent going to the top half",
    "spending_share", "share", period=2028, tb="fiscal_year", mk=PKG,
    c={"income_group": "top_half", "income_axis": HALF_AXIS, "horizon": TWO_YEARS,
       "modelling_geography": F8_GEO},
    norm=PCT_SHARE, hint=COLA_PKG)
add("V2", "p.20, paragraph 1", "around four-in-five", 0.8,
    "with around four-in-five properties in England eligible for support",
    "eligibility_rate", "share", fy="2026-27", mk=HEP, geo="England",
    c={"unit_population": "properties (dwellings in Council Tax bands A-D)"},
    model="administrative_data", bench="administrative_fact", norm="'four-in-five' → 0.8",
    hint="a £100 rebate for those living in Council Tax bands A-D")
add("V2", "p.20, paragraph 1", "around one-in-eight", 0.125,
    "around one-in-eight households in the bottom half of the income distribution",
    "affected_share", "share", fy="2026-27", mk=HEP, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS,
       "denominator": "households in the bottom half of the income distribution",
       "subgroup": "live in higher-band properties and will miss out on the Household Energy Payment"},
    model="survey_microdata", norm="'one-in-eight' → 0.125",
    hint="a £100 rebate for those living in Council Tax bands A-D")
add("V2", "p.21, paragraph 1", "over 900,000", 900000,
    "the over 900,000 low-income private renting families in Britain",
    "affected_count", "families", fy="2026-27", geo="GB",
    c={"subgroup": "pay more in rent than the support they receive with housing costs (Local Housing Allowance)",
       "unit_population": "low-income private renting families"},
    kind="range_low", note="Context for the LHA freeze, which the Budget left in place ('today').")
add("V2", "p.21, paragraph 2", "up to 70,000", 70000,
    "The scheme is expected to support up to 70,000 families",
    "participant_count", "families", period=2030, tb="fiscal_year", mk=YFH, geo="England",
    c={"horizon": "scheme total; the sentence costs it in 2029-30"},
    kind="range_high", att="restated", model="hm_government_publication", conf="medium",
    hint="the ‘Your First Home’ scheme",
    note="Table 6.1 line 37's title says 'around 70,000 first-time buyers'.")
add("V2", "p.21, paragraph 2", "£95 million", dec("95", 1e6),
    "at a cost of £95 million in 2029-30",
    "revenue_change", "gbp", fy="2029-30", mk=YFH, geo="England",
    c={"sign_convention": "positive = cost to the Exchequer (RF calls the figure a cost)"},
    att="restated", model="hmt_costing_obr_certified", norm=M, conf="medium",
    hint="the ‘Your First Home’ scheme",
    note="Table 6.1 line 37 prints +95 in 2029-30, a yield ('net income from developer fees'), so RF's 'cost' has the opposite sign. Value staged as printed.")
add("V2", "p.21, paragraph 3", "over a million", dec("1", 1e6),
    "Prolonging the LHA freeze into 2027-28 means over a million families lose out",
    "gainer_count", "families", fy="2027-28", pk=O_LHA, geo="England",
    c={"unit_population": "private renting families (benefit units)",
       "framing": "RF: lose out from prolonging the LHA freeze into 2027-28; they would gain if LHA were unfrozen"},
    kind="range_low", norm="'a million' → 1,000,000 (lower bound)",
    hint="Prolonging the LHA freeze into 2027-28",
    note="Geography from Figure 9 (England); workbook F9 M22 counts 1,572,152.")
add("V2", "p.21, paragraph 3", "91 per cent", 0.91,
    "91 per cent of them in the bottom half of the income distribution",
    "affected_share", "share", fy="2027-28", pk=O_LHA, geo="England",
    c={"income_group": "bottom_half", "income_axis": HALF_AXIS,
       "denominator": "private renting families who lose out from the prolonged LHA freeze"},
    norm=PCT_SHARE, hint="Prolonging the LHA freeze into 2027-28",
    note="Workbook F9 M19 0.906.")
add("V2", "p.22, paragraph 1", "38.6 per cent", 38.6,
    "rising to 38.6 per cent by 2031-32",
    "tax_to_gdp_ratio", "percent", fy="2031-32",
    c={"statistic": "National Accounts taxes as a share of GDP (fn 24)"}, model="arithmetic")
add("V2", "p.22, paragraph 1", "5.7 percentage points", 5.7,
    "set to rise by another 5.7 percentage points in the 12 years from 2019-20",
    "tax_to_gdp_ratio_change", "percentage_points", fy="2031-32",
    c={"statistic": "National Accounts taxes as a share of GDP", "horizon": "2019-20 to 2031-32"},
    model="arithmetic")
# Figure 10 data labels. Mapped to series and years through workbook F10
# rows 46 and 54; both series are -1.75 in 2026-27 and the chart prints one
# label there, staged once on the net direct effects series.
for fy_, raw in (("2026-27", "-£1.7bn"), ("2027-28", "+£0.3bn"), ("2028-29", "+£3.1bn"),
                 ("2029-30", "+£5.8bn"), ("2030-31", "+£6.6bn"), ("2031-32", "+£7.5bn")):
    add("V2", f"p.23, Figure 10 data label, 'Net direct effects', {fy_}", raw,
        dec(raw.replace("£", "").replace("bn", "").replace("+", ""), 1e9), raw,
        "revenue_change", "gbp", fy=fy_, pk=P_OBR_TAX, c={"sign_convention": SC_F10},
        att="restated", model="obr_efo_forecast", norm=BN + "; sign as printed",
        table=FIG[10], col=f"Net direct effects, {fy_}", hint="Net direct effects (the OBR's direct effect of tax measures)",
        note=RESTATED_OBR + " Table 3.1 direct effect of tax measures, sign flipped by RF."
        + (" The single 2026-27 label serves both lines (both -1.75 in workbook F10)." if fy_ == "2026-27" else ""))
for fy_, raw in (("2027-28", "-£2.0bn"), ("2028-29", "-£0.7bn"), ("2029-30", "+£1.5bn"),
                 ("2030-31", "+£1.9bn"), ("2031-32", "+£2.7bn")):
    add("V2", f"p.23, Figure 10 data label, 'Net effect if Fuel Duty frozen', {fy_}", raw,
        dec(raw.replace("£", "").replace("bn", "").replace("+", ""), 1e9), raw,
        "revenue_change", "gbp", fy=fy_, pk=O_TAX_FREEZE, c={"sign_convention": SC_F10},
        model="arithmetic", norm=BN + "; sign as printed",
        table=FIG[10], col=f"Net effect if Fuel Duty frozen, {fy_}",
        hint="Net effect if Fuel Duty frozen",
        note="The OBR's direct effect of tax measures plus its constant-duty-rate alternative (workbook F10 row 54).")
add("V2", "p.23, paragraph 2", "around £1.5 billion", dec("1.5", 1e9),
    "and raises around £1.5 billion",
    "revenue_change", "gbp", period=2029, tb="fiscal_year", mk=BANK,
    c={"sign_convention": SC_YIELD, "horizon": "the surcharge's 15 months (Table 6.1: 2026-27 to 2028-29)"},
    kind="cumulative", att="restated", model="hmt_costing_obr_certified", norm=BN,
    hint="The Bank Surcharge is to be increased from 3 per cent to 6 per cent",
    note=RESTATED_HMT + " line 55 (£305m + £950m + £220m = £1,475m; workbook F10 J49 1.475).")
add("V2", "p.24, paragraph 2", "around £20 billion", dec("20", 1e9),
    "receipts would be around £20 billion higher this year",
    "revenue_change", "gbp", fy="2026-27", pk=O_FD_RPI,
    c={"sign_convention": SC_YIELD, "counterfactual": "Fuel Duty rates risen in line with RPI since January 2011"},
    model="arithmetic", norm=BN, hint="If duty rates had risen in line with RPI")
add("V2", "p.24, paragraph 3", "£4.3 billion", dec("4.3", 1e9),
    "If Fuel Duty instead remained frozen, the cost in 2029-30 would be £4.3 billion",
    "revenue_change", "gbp", fy="2029-30", pk=O_FD_FREEZE,
    c={"sign_convention": SC_COST,
       "counterfactual": "rates held at 52.95p a litre instead of the scheduled July 2027 rise to 60.59p (over 14 per cent)"},
    model="arithmetic", norm=BN, hint="If Fuel Duty instead remained frozen",
    note="The OBR's constant-duty-rate alternative less its central Fuel Duty forecast (fn 27; workbook F10 row 48, -4.29 in 2029-30).")
WORKER = {"household_type": "typical part-time worker on the adult minimum wage earning £12,739 in 2027-28 (£13.21 an hour, 18.5 hours a week; fn 29)"}
add("V2", "p.25, paragraph 1", "£34", 34,
    "will earn £12,739 and pay £34 in Income Tax and £10 in employee NICs",
    "tax_liability", "gbp", fy="2027-28", c=dict(WORKER, tax="Income Tax"), model="arithmetic",
    note="Worked example: the worker's tax; a pensioner on the same income pays nothing under the Pension Tax Allowance.")
add("V2", "p.25, paragraph 1", "£10", 10,
    "will earn £12,739 and pay £34 in Income Tax and £10 in employee NICs",
    "tax_liability", "gbp", fy="2027-28", c=dict(WORKER, tax="employee National Insurance contributions"),
    model="arithmetic", note="Worked example (Pension Tax Allowance comparison).")
add("V2", "p.25, paragraph 1", "nothing", 0,
    "a pensioner receiving the same income will pay nothing",
    "tax_liability", "gbp", fy="2027-28", mk=PTA,
    c={"household_type": "pensioner with an income of £12,739 in 2027-28", "tax": "Income Tax"},
    model="arithmetic", norm="'nothing' → 0", hint="the new Pension Tax Allowance",
    note="Worked example (mode 3).")
add("V2", "p.25, paragraph 2", "£150 million", dec("150", 1e6),
    "only reaching £150 million in 2029-30",
    "revenue_change", "gbp", fy="2029-30", mk=PTA, c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=M, hint="the new Pension Tax Allowance",
    note=RESTATED_HMT + " line 52 (-£150m in 2029-30).")
add("V2", "p.26, paragraph 1", "£145 million", dec("145", 1e6),
    "Further revenue (around £145 million per year) has been raised through Gambling Duties",
    "revenue_change", "gbp", period=2030, tb="fiscal_year", mk=MGD,
    c={"sign_convention": SC_YIELD, "horizon": "per year (Table 6.1 line 56: £145m a year from 2029-30)"},
    att="restated", model="hmt_costing_obr_certified", norm=M, conf="medium",
    hint="Gambling Duties ... well-targeted at machine gaming",
    note=RESTATED_HMT + " line 56 (135, 150, 145, 145, 145 from 2027-28). RF prints no year.")
add("V2", "p.27, paragraph 2", "£300 million", dec("300", 1e6),
    "at an estimated cost of £300 million a year by 2031-32",
    "revenue_change", "gbp", fy="2031-32", mk=FOUNDERS, c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=M, hint="Founders’ Relief",
    note=RESTATED_HMT + " line 26 (-£300m in 2031-32).")
add("V2", "p.27, paragraph 4", "£2.6 billion", dec("2.6", 1e9),
    "worth £2.6 billion in 2026-27",
    "revenue_change", "gbp", fy="2026-27", mk=HEP, c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=BN, hint="the Household Energy Payment",
    note=RESTATED_HMT + " line 1 (-£2,625m); fn 37: the cost includes funds for the devolved governments.")
add("V2", "p.27, paragraph 4", "£3 billion", dec("3", 1e9),
    "increased RDEL by an average of £3 billion a year",
    "rdel_change", "gbp", period=2029, tb="fiscal_year", pk=P_RDEL,
    c={"horizon": "current Spending Review period (2026-27 to 2028-29)", "statistic": "annual average",
       "sign_convention": "positive = higher departmental spending"},
    model="arithmetic", norm=BN, hint="decisions in this Budget, excluding the Household Energy Payment",
    note="fn 37: underspend, forecast and classification changes and the pensions valuation are stripped out.")
add("V2", "p.27, paragraph 4", "£6.7 billion", dec("6.7", 1e9),
    "amounting to a total of £6.7 billion between 2026-27 and 2031-32",
    "revenue_change", "gbp", period=2032, tb="fiscal_year", mk=DIP,
    c={"sign_convention": SC_COST, "horizon": "2026-27 to 2031-32"},
    kind="cumulative", att="restated", model="hmt_costing_obr_certified", norm=BN, conf="medium",
    hint="an addition to pay for the Defence Investment Plan (DIP)",
    note=RESTATED_HMT + " line 40, matched by its sum (-£6,670m over 2026-27 to 2031-32); RF calls it an addition to pay for the DIP, Table 6.1 titles the line 'Commitment to further savings made at announcement on 30 June 2026'.")
add("V2", "p.29, paragraph 1", "1.7 per cent", 1.7,
    "grow by an average of 1.7 per cent a year in real per-person terms",
    "real_spending_growth", "percent", period=2029, tb="fiscal_year",
    c={"statistic": "day-to-day departmental spending (RDEL), real per person, average annual growth",
       "horizon": "2023-24 to 2028-29"},
    model="arithmetic")
add("V2", "p.29, paragraph 2", "1.4 per cent", 1.4,
    "where real annual growth averages 1.4 per cent",
    "real_spending_growth", "percent", period=2029, tb="fiscal_year",
    c={"statistic": "capital departmental spending (CDEL), real annual growth", "horizon": "this Parliament"},
    model="arithmetic")
add("V2", "p.29, paragraph 2", "2.3 per cent", 2.3,
    "drift to 2.3 per cent of GDP in 2031-32",
    "psni_share_of_gdp", "percent", fy="2031-32", att="restated", model="obr_efo_forecast",
    note=RESTATED_OBR + ".")
add("V2", "p.30, paragraph 1", "0.5 per cent", 0.5,
    "expected to grow by just 0.5 per cent between 2028-29 and 2031-32",
    "real_spending_growth", "percent", period=2032, tb="fiscal_year",
    c={"statistic": "real RDEL per person", "horizon": "2028-29 to 2031-32"},
    model="arithmetic", conf="medium",
    note="The text does not say whether this is total or a yearly average; Figure 14 plots average annual changes.")
add("V2", "p.30, paragraph 2", "2.7 per cent", 2.7,
    "take defence spending to only 2.7 per cent of GDP by 2029-30",
    "defence_spending_share_of_gdp", "percent", fy="2029-30",
    att="restated", model="hm_government_publication", hint="the Defence Investment Plan")
add("V2", "p.30, paragraph 2", "£10 billion", dec("10", 1e9),
    "leaving an additional £10 billion requirement by 2030-31",
    "spending_pressure", "gbp", fy="2030-31",
    c={"scenario": "defence spending reaches 3 per cent of GDP"}, model="arithmetic", norm=BN)
add("V2", "p.30, paragraph 2", "£6 billion", dec("6", 1e9),
    "of which £6 billion will be day-to-day spending",
    "spending_pressure", "gbp", fy="2030-31",
    c={"scenario": "defence spending reaches 3 per cent of GDP", "component": "day-to-day spending (RDEL)"},
    model="arithmetic", norm=BN)
UNPROT = {"subgroup": "‘unprotected’ departments, real funding per person",
          "sign_convention": "positive = size of the real-terms cut from the Parliament's peak"}
add("V2", "p.31, paragraph 1", "2 per cent", 2,
    "of 2 per cent in 2030-31 from their peak in this Parliament",
    "real_spending_change", "percent", fy="2030-31",
    c=dict(UNPROT, scenario="Spring Forecast (March 2026) plans"), model="arithmetic")
add("V2", "p.31, paragraph 1", "3 per cent", 3,
    "increased that cut to 3 per cent",
    "real_spending_change", "percent", fy="2030-31",
    c=dict(UNPROT, scenario="October 2026 plans (higher inflation, pressures folded into existing budgets)"),
    model="arithmetic")
add("V2", "p.31, paragraph 1", "6 per cent", 6,
    "would raise them to 6 per cent",
    "real_spending_change", "percent", fy="2030-31",
    c=dict(UNPROT, scenario="October 2026 plans with the defence spending gap filled within current totals"),
    model="arithmetic")
add("V2", "p.34, Box 3", "£10 million", dec("10", 1e6),
    "forecast to cost the Treasury £10 million in 2027-28",
    "revenue_change", "gbp", fy="2027-28", mk=BRR, geo="England", c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=M,
    hint="letting authorities keep some of the growth in Business Rates revenues",
    note=RESTATED_HMT + " line 21 (-£10m in 2027-28).")
add("V2", "p.34, Box 3", "£140 million", dec("140", 1e6),
    "rising to £140 million in the final year of the forecast (2031-32)",
    "revenue_change", "gbp", fy="2031-32", mk=BRR, geo="England", c={"sign_convention": SC_COST},
    att="restated", model="hmt_costing_obr_certified", norm=M,
    hint="letting authorities keep some of the growth in Business Rates revenues",
    note=RESTATED_HMT + " line 21 (-£140m in 2031-32).")
add("V2", "p.35, paragraph 2", "£13 billion", dec("13", 1e9),
    "£13 billion higher on average over the next five years",
    "forecast_borrowing_change", "gbp", period=2031, tb="fiscal_year",
    c={"basis": "post-measures", "comparison": "October 2026 post-measures vs March 2026 forecast",
       "horizon": NEXT5, "statistic": "annual average", "sign_convention": SC_BORROW},
    model="arithmetic", norm=BN)
add("V2", "p.35, paragraph 2", "£2 billion", dec("2", 1e9),
    "£2 billion more than the £11 billion deterioration due to economic and fiscal news",
    "decisions_effect_on_borrowing", "gbp", period=2031, tb="fiscal_year", pk=P_OBR_DECISIONS,
    c={"horizon": NEXT5, "statistic": "annual average", "sign_convention": SC_BORROW},
    model="arithmetic", norm=BN, hint="the Budget’s tax and spending measures")
for raw, fy_ in (("4.4 per cent", "2025-26"), ("4.2 per cent", "2026-27"), ("3.4 per cent", "2027-28")):
    quote = {"2025-26": "falling from 4.4 per cent of GDP in 2025-26",
             "2026-27": "to 4.2 per cent of GDP in 2026-27",
             "2027-28": "and 3.4 per cent in 2027-28"}[fy_]
    add("V2", "p.35, paragraph 2", raw, float(raw.split()[0]), quote,
        "psnb_share_of_gdp", "percent", fy=fy_, c={"basis": "post-measures"},
        att="restated", model="obr_efo_forecast", note=RESTATED_OBR + ".")
add("V2", "p.35, fn 47", "no overall impact", 0,
    "policies announced in the Budget have no overall impact on borrowing",
    "decisions_effect_on_borrowing", "gbp", period=2032, tb="fiscal_year", pk=P_OBR_DECISIONS,
    c={"horizon": "averaged over the full October forecast window, 2026-27 to 2031-32",
       "statistic": "annual average", "sign_convention": SC_BORROW},
    att="restated", model="obr_efo_forecast", norm="'no overall impact' → 0",
    note=RESTATED_OBR + " ('the OBR estimates').")
add("V2", "p.36, paragraph 1", "£23.6 billion", dec("23.6", 1e9),
    "the Government held £23.6 billion of headroom against its current balance rule",
    "fiscal_headroom", "gbp", fy="2029-30",
    c={"rule": "current balance", "forecast_vintage": "March 2026 Spring Forecast"},
    att="restated", model="obr_efo_forecast", norm=BN, note="Restates the OBR's March 2026 forecast.")
add("V2", "p.36, paragraph 1", "£14.5 billion", dec("14.5", 1e9),
    "restoring it to £14.5 billion",
    "fiscal_headroom", "gbp", fy="2029-30",
    c={"rule": "current balance", "forecast_vintage": "October 2026, post-measures"},
    att="restated", model="obr_efo_forecast", norm=BN, note=RESTATED_OBR + ".")
add("V2", "p.36, paragraph 1", "62 per cent", 0.62,
    "about three-fifths (62 per cent) of its March level",
    "headroom_share_of_previous", "share", fy="2029-30",
    c={"denominator": "headroom after the March 2026 Spring Forecast (£23.6bn)"},
    model="arithmetic", norm=PCT_SHARE)
add("V2", "p.37, paragraph 1", "£18 billion", dec("18", 1e9),
    "roughly equivalent to £18 billion of headroom in year three",
    "fiscal_headroom", "gbp", period=2030, tb="fiscal_year",
    c={"comparison": "year-three equivalent of the £24 billion left in year four in March",
       "horizon": "year three of the forecast (the fiscal-rule year)"},
    model="arithmetic", norm=BN, conf="medium")
add("V2", "p.38, paragraph 1", "£26 billion", dec("26", 1e9),
    "into a deficit of £26 billion",
    "current_budget_balance", "gbp", fy="2029-30",
    c={"sign_convention": "positive = current budget deficit",
       "scenario": "current balance underperforms the forecast by 1 per cent of GDP three years ahead"},
    model="arithmetic", norm=BN)
add("V2", "p.39, paragraph 2", "£12 billion", dec("12", 1e9),
    "forecast to be £12 billion in surplus by the end of the Parliament",
    "primary_balance", "gbp", fy="2028-29", c={"sign_convention": "positive = surplus"},
    model="arithmetic", norm=BN)
add("V2", "p.39, paragraph 2", "£64 billion", dec("-64", 1e9),
    "versus a £64 billion deficit if it had not changed",
    "primary_balance", "gbp", fy="2028-29",
    c={"sign_convention": "positive = surplus", "scenario": "primary balance held at its 2023-24 share of GDP"},
    model="arithmetic", norm=BN + "; 'deficit' → negative")
add("V2", "p.39, paragraph 2", "£76 billion", dec("76", 1e9),
    "That £76 billion improvement is more than fully accounted for",
    "primary_balance_change", "gbp", fy="2028-29",
    c={"horizon": "2023-24 to 2028-29", "sign_convention": "positive = improvement (towards surplus)"},
    model="arithmetic", norm=BN)
add("V2", "p.39, paragraph 2", "£107 billion", dec("107", 1e9),
    "by £107 billion of higher tax revenues",
    "tax_revenue_change", "gbp", fy="2028-29",
    c={"horizon": "2023-24 to 2028-29 (fn 53 computes it to 2029-30)", "sign_convention": "positive = higher receipts"},
    model="arithmetic", norm=BN, conf="medium",
    note="fn 53: 'the forecasted change in public sector current receipts as a proportion of GDP between 2023-24 and 2029-30, multiplied by forecasted GDP in 2029-30', while the text says 2028-29.")
PARL = dict(fy="2029-30", pk=P_PARLIAMENT, base="rf_start_of_parliament_policy",
            hint="all permanent personal tax and benefit changes announced this Parliament")
add("V2", "p.40, paragraph 2", "£320", 320,
    "annual incomes will, on average, be £320 higher for households in the bottom quintile",
    "average_household_income_change", "gbp",
    c={"income_group": "quintile_1", "income_axis": "net equivalised household income quintile, after housing costs",
       "housing_costs": "ahc", "unit_population": "households", "sign_convention": SC_GAIN,
       "price_basis": "2026-27 prices (Figure 20)"}, **PARL)
add("V2", "p.40, paragraph 2", "£2,000", -2000,
    "compared to £2,000 lower for those in the top quintile",
    "average_household_income_change", "gbp",
    c={"income_group": "quintile_5", "income_axis": "net equivalised household income quintile, after housing costs",
       "housing_costs": "ahc", "unit_population": "households", "sign_convention": SC_GAIN,
       "price_basis": "2026-27 prices (Figure 20)"}, norm=LOSS, **PARL)
add("V2", "p.41, paragraph 1", "0.9 per cent", -0.9,
    "between 0.9 per cent and 2.2 per cent lower on average in 2029-30",
    "pct_change_after_tax_income", "percent",
    c={"subgroup": "household income quintiles 2 to 5", "housing_costs": "ahc",
       "unit_population": "households", "sign_convention": SC_GAIN}, kind="range_high", norm=LOSS, **PARL)
add("V2", "p.41, paragraph 1", "2.2 per cent", -2.2,
    "between 0.9 per cent and 2.2 per cent lower on average in 2029-30",
    "pct_change_after_tax_income", "percent",
    c={"subgroup": "household income quintiles 2 to 5", "housing_costs": "ahc",
       "unit_population": "households", "sign_convention": SC_GAIN}, kind="range_low", norm=LOSS, **PARL)
CARER = {"household_type": "carer on the National Living Wage, not on Universal Credit (fn 56)",
         "scenario": "current rules, before the taper"}
add("V2", "p.42, Box 4", "£280", 280,
    "a sharp drop in their net income – from £280 to £216 a week",
    "net_weekly_income", "gbp_per_week", fy="2026-27", mk=CA,
    c=dict(CARER, hours="16 hours a week"), model="arithmetic",
    hint="end the Carer’s Allowance cliff edge", note="Worked example (mode 3): the cliff edge the taper removes.")
add("V2", "p.42, Box 4", "£216", 216,
    "a sharp drop in their net income – from £280 to £216 a week",
    "net_weekly_income", "gbp_per_week", fy="2026-27", mk=CA,
    c=dict(CARER, hours="17 hours a week"), model="arithmetic",
    hint="end the Carer’s Allowance cliff edge", note="Worked example (mode 3): the cliff edge the taper removes.")
add("V2", "p.42, Box 4", "48,000", 48000,
    "This is expected to benefit 48,000 carers in England and Wales",
    "gainer_count", "persons", fy="2030-31", mk=CA, geo="England and Wales",
    att="restated", model="hm_government_publication",
    hint="Carer’s Allowance withdrawn at £1 for every £1 earned above the limit",
    note="The Government's estimate (HM Government, Everyday fixes, October 2026; fn 55). The taper starts in 2030-31.")
LS = {"statistic": "median", "unit_population": "non-pensioners", "housing_costs": "ahc"}
add("V2", "p.43, paragraph 2", "1.8 per cent", 1.8,
    "median non-pensioner real incomes are projected to grow by just 1.8 per cent",
    "real_income_growth", "percent", fy="2028-29", c=dict(LS, horizon="2023-24 to 2028-29"), kind="cumulative")
add("V2", "p.43, paragraph 2", "£600", 600,
    "equivalent to a cumulative increase of £600 (in 2026-27 prices)",
    "real_income_change", "gbp", fy="2028-29",
    c=dict(LS, horizon="2023-24 to 2028-29", price_basis="2026-27 prices"), kind="cumulative")
add("V2", "p.43, paragraph 2", "5.0 per cent", 5.0,
    "real income growth of 5.0 per cent between 2023-24 and 2026-27",
    "real_income_growth", "percent", fy="2026-27", c=dict(LS, horizon="2023-24 to 2026-27"), kind="cumulative")
add("V2", "p.43, paragraph 2", "3.0 per cent", -3.0,
    "their incomes are expected to fall by 3.0 per cent between 2026-27 and 2028-29",
    "real_income_growth", "percent", fy="2028-29",
    c=dict(LS, horizon="2026-27 to 2028-29", sign_convention=SC_GAIN), kind="cumulative", norm=LOSS)
add("V2", "p.43, paragraph 2", "£1,050", -1050,
    "equivalent to a drop in annual household disposable income of £1,050",
    "real_income_change", "gbp", fy="2028-29",
    c=dict(LS, horizon="2026-27 to 2028-29", price_basis="2026-27 prices", sign_convention=SC_GAIN),
    kind="cumulative", norm=LOSS)
add("V2", "p.45, paragraph 1", "2.0 per cent", 2.0,
    "real income growth of 2.0 per cent for those at the 25th percentile",
    "real_income_growth", "percent", fy="2028-29",
    c={"statistic": "25th percentile", "unit_population": "non-pensioners", "housing_costs": "ahc",
       "horizon": "2023-24 to 2028-29"}, kind="cumulative")
add("V2", "p.45, paragraph 1", "1.1 per cent", 1.1,
    "growth of 1.1 per cent for those at the 75th percentile",
    "real_income_growth", "percent", fy="2028-29",
    c={"statistic": "75th percentile", "unit_population": "non-pensioners", "housing_costs": "ahc",
       "horizon": "2023-24 to 2028-29"}, kind="cumulative")
POV = {"housing_costs": "ahc", "poverty_line": "relative_60_median"}
add("V2", "p.45, paragraph 2", "2.6 percentage points", -2.6,
    "child poverty is set to fall across this Parliament by 2.6 percentage points",
    "poverty_rate_change", "percentage_points", fy="2028-29",
    c=dict(POV, unit_population="children", horizon="2023-24 to 2028-29",
           sign_convention="positive = rise in the poverty rate"),
    kind="cumulative", norm="printed as a fall; carried negative")
add("V2", "p.45, paragraph 2", "27.7 per cent", 0.277,
    "(from 27.7 per cent to 25.1 per cent)",
    "poverty_rate", "share", fy="2023-24", c=dict(POV, unit_population="children"),
    model="survey_microdata", bench="administrative_fact", norm=PCT_SHARE,
    note="2023-24 is HBAI outturn (the Parliament's base year).")
add("V2", "p.45, paragraph 2", "25.1 per cent", 0.251,
    "(from 27.7 per cent to 25.1 per cent)",
    "poverty_rate", "share", fy="2028-29", c=dict(POV, unit_population="children"), norm=PCT_SHARE)
for raw, val, pop in (("+0.8ppts", 0.8, "working-age adults"), ("-0.4ppts", -0.4, "pension-age adults")):
    add("V2", f"p.46, Figure 23 data label ({pop})", raw, val, raw,
        "poverty_rate_change", "percentage_points", fy="2028-29",
        c=dict(POV, unit_population=pop, horizon="change since 2023-24",
               sign_convention="positive = rise in the poverty rate"),
        kind="cumulative", norm="ppts as printed", table=FIG[23], col=f"{pop}, 2028-29",
        note="Label mapped to its series through workbook F23 (AP71 0.84 working age; AQ71 -0.42 pension age).")
add("V2", "p.47, paragraph 1", "£9 billion", dec("9", 1e9),
    "the Budget included a £9 billion top up to departmental budgets",
    "rdel_change", "gbp", period=2029, tb="fiscal_year", pk=P_RDEL,
    c={"horizon": "the current Spending Review period (2026-27 to 2028-29)",
       "sign_convention": "positive = higher departmental spending"},
    kind="cumulative", model="arithmetic", norm=BN, hint="a £9 billion top up to departmental budgets")

# ===========================================================================
# CMT: comment, 'It's good to be flexible' (29 October 2026).
# ===========================================================================
add("CMT", "paragraph 1", "£1,040", 1040,
    "worth £1,040 a year for someone working 40 hours a week",
    "annual_earnings_change", "gbp", fy="2027-28", pk=P_MIN_WAGE,
    c={"household_type": "adult minimum wage worker, 40 hours a week"}, model="arithmetic",
    hint="minimum wage rates from April 2027: the adult rate up 50p (3.9 per cent) to £13.21, youth rates up 3.9 per cent")

# ===========================================================================
# XL: the chart-data workbook. Cell values are the strings stored in the
# sheet XML (<v>), embedded below; --check-primaries re-reads them. Only the
# ranges behind charts of RF's own estimates are staged (NOTES.md lists the
# sheets left out and why).
# ===========================================================================
WORKBOOK = {
    'F7': {
        'A3': 'Financial year (key)',
        'C3': 'Bill before support',
        'D3': 'Energy Price Guarantee',
        'E3': 'Energy Bills Support Scheme',
        'F3': 'Policy levies removed',
        'H3': 'Electricity VAT cut',
        'I3': 'Net bill',
        'L3': 'Council tax rebate',
        'M3': 'Net bill including the council tax rebate',
        'A4': '2019-20',
        'C4': '1457.5217690073432',
        'D4': '0',
        'E4': '0',
        'F4': '0',
        'H4': '0',
        'I4': '1457.5217690073432',
        'L4': '0',
        'M4': '1457.5217690073432',
        'A5': '2020-21',
        'C5': '1351.0380971759059',
        'D5': '0',
        'E5': '0',
        'F5': '0',
        'H5': '0',
        'I5': '1351.0380971759059',
        'L5': '0',
        'M5': '1351.0380971759059',
        'A6': '2021-22',
        'C6': '1445.5505055181945',
        'D6': '0',
        'E6': '0',
        'F6': '0',
        'H6': '0',
        'I6': '1445.5505055181945',
        'L6': '0',
        'M6': '1445.5505055181945',
        'A7': '2022-23',
        'C7': '3229.6716147078582',
        'D7': '-907.45431450723811',
        'E7': '-462.55807470164604',
        'F7': '0',
        'H7': '0',
        'I7': '1859.6592254989739',
        'L7': '-173.45927801311726',
        'M7': '1686.1999474858567',
        'A8': '2023-24',
        'C8': '2066.2174805315267',
        'D8': '-137.93485701193069',
        'E8': '0',
        'F8': '0',
        'H8': '0',
        'I8': '1928.282623519596',
        'L8': '0',
        'M8': '1928.282623519596',
        'A9': '2024-25',
        'C9': '1642.7865223319588',
        'D9': '0',
        'E9': '0',
        'F9': '0',
        'H9': '0',
        'I9': '1642.7865223319588',
        'L9': '0',
        'M9': '1642.7865223319588',
        'A10': '2025-26',
        'C10': '1631.3597957825489',
        'D10': '0',
        'E10': '0',
        'F10': '0',
        'H10': '0',
        'I10': '1631.3597957825489',
        'L10': '0',
        'M10': '1631.3597957825489',
        'A11': '2026-27',
        'C11': '1994.3295005534867',
        'D11': '0',
        'E11': '0',
        'F11': '-119.20778473402099',
        'H11': '-26.774190681839883',
        'I11': '1848.3475251376258',
        'L11': '-100',
        'M11': '1748.3475251376258',
        'A12': '2027-28',
        'C12': '2234.7722233791355',
        'D12': '0',
        'E12': '0',
        'F12': '-115.62807307123404',
        'H12': '-12.801764200129682',
        'I12': '2106.3423861077713',
        'L12': '0',
        'M12': '2106.3423861077713',
    },
    'F8': {
        'C6': 'vigintile',
        'D6': 'Council Tax rebate',
        'E6': 'Fuel Duty freeze extension',
        'F6': 'Energy VAT cut (original)',
        'G6': 'Energy VAT cut extension',
        'J6': 'Net change in income',
        'K6': '% change in income (right axis)',
        'C7': '1',
        'C8': '2',
        'D8': '87.959794935724858',
        'E8': '22.953331009590833',
        'F8': '24.509344979933971',
        'G8': '9.9030792151912745',
        'J8': '145.32555014044095',
        'K8': '1.0567528278374649E-2',
        'C9': '3',
        'D9': '88.901182786594291',
        'E9': '24.137398832573343',
        'F9': '29.021346190694413',
        'G9': '11.724804427924511',
        'J9': '153.78473223778656',
        'K9': '8.0452479458513696E-3',
        'C10': '4',
        'D10': '88.169545510911121',
        'E10': '24.288136443934249',
        'F10': '24.018257395682955',
        'G10': '9.703362520155105',
        'J10': '146.17930187068342',
        'K10': '6.8243567067586561E-3',
        'C11': '5',
        'D11': '86.875986616872979',
        'E11': '23.984272215554086',
        'F11': '24.475033183654425',
        'G11': '9.8887349221776262',
        'J11': '145.2240269382591',
        'K11': '6.2267378900553146E-3',
        'C12': '6',
        'D12': '84.915363663727476',
        'E12': '26.163821736213716',
        'F12': '25.81319323855676',
        'G12': '10.42940442807665',
        'J12': '147.3217830665746',
        'K12': '5.3443387303150703E-3',
        'C13': '7',
        'D13': '85.319604033331416',
        'E13': '24.70168184026496',
        'F13': '24.016112908415483',
        'G13': '9.703362520155105',
        'J13': '143.74076130216696',
        'K13': '4.8080677002149989E-3',
        'C14': '8',
        'D14': '83.004825841493584',
        'E14': '23.277968070799552',
        'F14': '25.343550526980462',
        'G14': '10.239618397434544',
        'J14': '141.86596283670815',
        'K14': '4.533919398860998E-3',
        'C15': '9',
        'D15': '87.226124012900982',
        'E15': '21.714554578275113',
        'F15': '26.334303644552381',
        'G15': '10.641258601816673',
        'J15': '145.91624083754516',
        'K15': '4.3637172481021348E-3',
        'C16': '10',
        'D16': '81.909389047134027',
        'E16': '27.242934371993492',
        'F16': '26.724600327232231',
        'G16': '10.800149232121694',
        'J16': '146.67707297848145',
        'K16': '4.0902742752892069E-3',
        'C17': '11',
        'D17': '81.181920315808384',
        'E17': '24.883530668767811',
        'F17': '27.222121373285663',
        'G17': '10.998762520002966',
        'J17': '144.28633487786482',
        'K17': '3.6473475839219702E-3',
        'C18': '12',
        'D18': '81.060223023545404',
        'E18': '25.725198606275143',
        'F18': '27.076296239097587',
        'G18': '10.936971719328792',
        'J18': '144.79868958824693',
        'K18': '3.5000335860657706E-3',
        'C19': '13',
        'D19': '79.457676633748633',
        'E19': '26.27131009511152',
        'F19': '25.566577202797518',
        'G19': '10.327890969826221',
        'J19': '141.62345490148388',
        'K19': '3.2187775514644591E-3',
        'C20': '14',
        'D20': '78.975702082228963',
        'E20': '28.882298313007883',
        'F20': '27.234988296890492',
        'G20': '11.003176148622551',
        'J20': '146.09616484074988',
        'K20': '3.1027531405657953E-3',
        'C21': '15',
        'D21': '74.711312397739675',
        'E21': '25.80822680654402',
        'F21': '25.759581056869969',
        'G21': '10.407336284978729',
        'J21': '136.68645654613238',
        'K21': '2.6594617691551498E-3',
        'C22': '16',
        'D22': '70.731508750068315',
        'E22': '27.360524299975445',
        'F22': '27.848311655387398',
        'G22': '11.250339351319246',
        'J22': '137.1906840567504',
        'K22': '2.4036198526077995E-3',
        'C23': '17',
        'D23': '70.421093626559014',
        'E23': '27.099626385682384',
        'F23': '26.741756225372004',
        'G23': '10.804562860741276',
        'J23': '135.06703909835466',
        'K23': '2.1957679614585048E-3',
        'C24': '18',
        'D24': '63.758050533084315',
        'E24': '25.100096273952783',
        'F24': '25.047611284069369',
        'G24': '10.116036796086195',
        'J24': '124.02179488719266',
        'K24': '1.8467121117932625E-3',
        'C25': '19',
        'D25': '59.619947664410574',
        'E25': '24.659330921581805',
        'F25': '25.347839501515406',
        'G25': '10.239618397434544',
        'J25': '119.86673648494232',
        'K25': '1.5243410430210264E-3',
        'C26': '20',
        'D26': '43.480923920753412',
        'E26': '20.561654752269803',
        'F26': '26.746045199906948',
        'G26': '10.78690834626294',
        'J26': '101.57553221919309',
        'K26': '6.4087197867996703E-4',
    },
    'F9': {
        'M5': 'Would benefit if LHA were unfrozen',
        'N5': 'Could access Your First Home',
        'L6': '1',
        'M6': '602409',
        'N6': '0',
        'L7': '2',
        'M7': '361448',
        'N7': '5143',
        'L8': '3',
        'M8': '225697',
        'N8': '12723',
        'L9': '4',
        'M9': '145895',
        'N9': '10610',
        'L10': '5',
        'M10': '89681',
        'N10': '25933',
        'L11': '6',
        'M11': '75434',
        'N11': '43920',
        'L12': '7',
        'M12': '22234',
        'N12': '58906',
        'L13': '8',
        'M13': '26872',
        'N13': '31290',
        'L14': '9',
        'M14': '5773',
        'N14': '32175',
        'L15': '10',
        'M15': '16709',
        'N15': '8185',
        'L19': 'Bottom half',
        'M19': '0.90648359700588743',
        'N19': '0.23771326211853114',
        'L20': 'Top half',
        'M20': '9.3516402994112527E-2',
        'N20': '0.76228673788146883',
        'M22': '1572152',
        'N22': '228885',
    },
    'F10': {
        'B45': 'RF labels',
        'C45': '2026-\n27',
        'D45': '2027-\n28',
        'E45': '2028-\n29',
        'F45': '2029-\n30',
        'G45': '2030-\n31',
        'H45': '2031-\n32',
        'J45': 'Total',
        'B46': 'Net direct effects',
        'C46': '-1.748962394934833',
        'D46': '0.3445891022723464',
        'E46': '3.0778107174285685',
        'F46': '5.7593598564542612',
        'G46': '6.561813951177708',
        'H46': '7.5194144947097605',
        'B47': 'Fuel Duty',
        'C47': '-0.57499999999999996',
        'D47': '-0.78',
        'E47': '0',
        'F47': '0',
        'G47': '0',
        'H47': '0',
        'B48': '… and if Fuel Duty frozen',
        'C48': '-7.4636114533177533E-7',
        'D48': '-2.3483484846542702',
        'E48': '-3.7389555211291317',
        'F48': '-4.2893363032056087',
        'G48': '-4.6757828023106249',
        'H48': '-4.8671109188223411',
        'B49': 'Bank Surcharge',
        'C49': '0.30499999999999999',
        'D49': '0.95',
        'E49': '0.22',
        'F49': '0',
        'G49': '0',
        'H49': '0',
        'J49': '1.4749999999999999',
        'B50': 'Capital allowances',
        'C50': '0.125',
        'D50': '0.76500000000000001',
        'E50': '1.04',
        'F50': '1.075',
        'G50': '1.1000000000000001',
        'H50': '1.1200000000000001',
        'B51': 'Savings & property',
        'C51': '1.4999999999999999E-2',
        'D51': '0.16',
        'E51': '1.1299999999999999',
        'F51': '0.95499999999999996',
        'G51': '1',
        'H51': '1.0449999999999999',
        'B52': 'Tax administration, compliance and debt collection',
        'C52': '0.10715406208008789',
        'D52': '0.45449613483888379',
        'E52': '0.585410540860131',
        'F52': '2.4264741188308645',
        'G52': '2.8944025877267658',
        'H52': '3.6402230247611871',
        'B53': 'Other tax measures',
        'C53': '-1.7261164570149208',
        'D53': '-1.204907032566537',
        'E53': '0.10240017656843792',
        'F53': '1.3028857376233969',
        'G53': '1.5674113634509421',
        'H53': '1.7141914699485739',
        'B54': 'Net effect if Fuel Duty frozen',
        'C54': '-1.7489631412959783',
        'D54': '-2.003759382381924',
        'E54': '-0.66114480370056317',
        'F54': '1.4700235532486525',
        'G54': '1.8860311488670831',
        'H54': '2.6523035758874194',
    },
    'F20': {
        'C6': 'vigintile',
        'D6': 'pre-AB26 Direct tax changes',
        'E6': 'pre-AB26 Benefit changes',
        'F6': 'Pensioner Personal Allowance',
        'G6': 'Property and savings tax rise',
        'H6': 'pre-AB26 Indirect tax changes',
        'I6': 'Machine Games Levy',
        'J6': 'Remove standing charge on gas bills',
        'K6': 'AB26 Changes',
        'L6': 'Net change in income',
        'M6': '% change in income (right axis)',
        'C7': '1',
        'C8': '2',
        'D8': '-47.142947490670849',
        'E8': '646.99960828848816',
        'F8': '0',
        'G8': '-1.7782135089964868',
        'H8': '-164.23486397441957',
        'I8': '-5.1912598341987177',
        'J8': '2.828454464673996',
        'K8': '-4.1410188785212085',
        'L8': '431.48077794487654',
        'M8': '3.2796455700021668E-2',
        'C9': '3',
        'D9': '-133.98675404061214',
        'E9': '663.65562868312554',
        'F9': '7.9022937796187094',
        'G9': '-4.2623308972506493',
        'H9': '-75.270021513839311',
        'I9': '-5.04028766663032',
        'J9': '-0.88400570407247869',
        'K9': '-2.2843304883347386',
        'L9': '452.11452264033937',
        'M9': '2.4097105750032859E-2',
        'C10': '4',
        'D10': '-215.46742965135854',
        'E10': '525.82582771871967',
        'F10': '14.280216198415225',
        'G10': '-3.5456518358332687',
        'H10': '-81.148075655939465',
        'I10': '-4.1453683118925255',
        'J10': '4.9529784612896037',
        'K10': '11.542174511979034',
        'L10': '240.75249692340071',
        'M10': '1.1158914225933233E-2',
        'C11': '5',
        'D11': '-207.4928082552251',
        'E11': '320.14604335098556',
        'F11': '19.969198159104216',
        'G11': '-4.2658889139274834',
        'H11': '-113.18647487803901',
        'I11': '-4.4200285203587555',
        'J11': '4.361822383463732',
        'K11': '15.64510310828171',
        'L11': '15.111863326003174',
        'M11': '6.72689637075221E-4',
        'C12': '6',
        'D12': '-317.45131755773036',
        'E12': '189.19501959114859',
        'F12': '13.001011581765685',
        'G12': '-8.5008337694198417',
        'H12': '-130.30575534655509',
        'I12': '-4.7201539137131476',
        'J12': '4.0580591065481713',
        'K12': '3.8380830051808665',
        'L12': '-254.72397030795599',
        'M12': '-9.7547253887236805E-3',
        'C13': '7',
        'D13': '-379.50815412560041',
        'E13': '271.46539714664686',
        'F13': '9.6855760137705964',
        'G13': '-4.3207831892250397',
        'H13': '-131.5682480179421',
        'I13': '-5.2149060773117526',
        'J13': '6.0352488191529119',
        'K13': '6.185135566386716',
        'L13': '-233.42586943050893',
        'M13': '-7.9785390748041713E-3',
        'C14': '8',
        'D14': '-397.23768754649427',
        'E14': '34.708795269638358',
        'F14': '0',
        'G14': '-5.8962380869816116',
        'H14': '-98.116083117496601',
        'I14': '-5.8024242715800938',
        'J14': '4.0944379421089252',
        'K14': '-7.6042244164527801',
        'L14': '-468.24919981080529',
        'M14': '-1.5343200245851125E-2',
        'C15': '9',
        'D15': '-473.06863486740622',
        'E15': '-4.2312557391487644',
        'F15': '5.013307666132194',
        'G15': '-6.0983464864038979',
        'H15': '-116.06545346195708',
        'I15': '-6.2098672298379824',
        'J15': '4.172652438559453',
        'K15': '-3.1222536115502333',
        'L15': '-596.48759768006221',
        'M15': '-1.7755850869720063E-2',
        'C16': '10',
        'D16': '-504.51022346117679',
        'E16': '40.7600753177976',
        'F16': '0',
        'G16': '-11.257893164474808',
        'H16': '-96.44471920531214',
        'I16': '-4.2563237603462767',
        'J16': '0.91674665607570205',
        'K16': '-14.597470268745383',
        'L16': '-574.79233761743671',
        'M16': '-1.6075003122297545E-2',
        'C17': '11',
        'D17': '-634.99955085889815',
        'E17': '2.5380314824797097',
        'F17': '8.5289864412995726',
        'G17': '-4.4983644757085131',
        'H17': '-148.61111318813346',
        'I17': '-5.2276386697558337',
        'J17': '1.4151367032245616',
        'K17': '0.21811999905978752',
        'L17': '-780.85451256549209',
        'M17': '-1.9624001563633014E-2',
        'C18': '12',
        'D18': '-644.18911827984994',
        'E18': '7.3937402256997302',
        'F18': '3.6395114358178526',
        'G18': '-10.258890135766705',
        'H18': '-108.16864557242661',
        'I18': '-5.7187529497969081',
        'J18': '2.7538778517773608',
        'K18': '-9.584253797968401',
        'L18': '-754.54827742454518',
        'M18': '-1.8531838893463874E-2',
        'C19': '13',
        'D19': '-710.37706828425871',
        'E19': '3.5421248388447566',
        'F19': '6.1136763445359641',
        'G19': '-12.51510628334654',
        'H19': '-108.97114395894459',
        'I19': '-3.8597944527573418',
        'J19': '0.15642899290105561',
        'K19': '-10.104795398666862',
        'L19': '-825.9108828030254',
        'M19': '-1.8618399674419195E-2',
        'C20': '14',
        'D20': '-784.02361074255168',
        'E20': '-50.303618213896698',
        'F20': '7.4104273254389135',
        'G20': '-11.962817355597508',
        'H20': '-163.36244973262365',
        'I20': '-4.3218056643527234',
        'J20': '-2.077231510389538',
        'K20': '-10.951427204900856',
        'L20': '-1008.6411058939728',
        'M20': '-2.1413074642014206E-2',
        'C21': '15',
        'D21': '-906.16542699078127',
        'E21': '-61.260937593571725',
        'F21': '4.968578247971891',
        'G21': '-16.864037410909077',
        'H21': '-137.78371567308204',
        'I21': '-4.3363571985682938',
        'J21': '1.4806186072310084',
        'K21': '-14.751197754274472',
        'L21': '-1119.9612780117095',
        'M21': '-2.1711118358552359E-2',
        'C22': '16',
        'D22': '-1016.4606423204532',
        'E22': '-34.12815352553298',
        'F22': '1.2979181767348729',
        'G22': '-18.980686349190364',
        'H22': '-158.26232695193903',
        'I22': '-4.6601288350429968',
        'J22': '1.1277439023178886',
        'K22': '-21.215153105180601',
        'L22': '-1230.0662759031059',
        'M22': '-2.1581242636124046E-2',
        'C23': '17',
        'D23': '-1102.0653696213267',
        'E23': '-42.650856642903818',
        'F23': '1.5404859785353022',
        'G23': '-21.855793191105477',
        'H23': '-170.33485264210321',
        'I23': '-4.6419394172626198',
        'J23': '3.6342456722923089',
        'K23': '-21.323000957540486',
        'L23': '-1336.3740798638742',
        'M23': '-2.1666402161992334E-2',
        'C24': '18',
        'D24': '-1253.7836465497239',
        'E24': '-50.270959578556358',
        'F24': '1.6925963563963622',
        'G24': '-23.264411187672522',
        'H24': '-157.02636875109602',
        'I24': '-5.1148642795305932',
        'J24': '-0.30558221868705004',
        'K24': '-26.992261329493804',
        'L24': '-1488.0732362088702',
        'M24': '-2.2141229290221331E-2',
        'C25': '19',
        'D25': '-1529.5106109988992',
        'E25': '-52.564944597397698',
        'F25': '0.76555625817987172',
        'G25': '-36.148021531058475',
        'H25': '-140.30424476336339',
        'I25': '-4.3290814314677846',
        'J25': '0.64754327294940595',
        'K25': '-39.064003431396984',
        'L25': '-1761.4438037910572',
        'M25': '-2.2214262754004031E-2',
        'C26': '20',
        'D26': '-2708.7032837875595',
        'E26': '-49.09527042877744',
        'F26': '0.50617384187221015',
        'G26': '-275.39936732558999',
        'H26': '-253.83715038158698',
        'I26': '-5.6750983471283689',
        'J26': '-1.4406018881127238',
        'K26': '-282.00889371895886',
        'L26': '-3293.6445983168828',
        'M26': '-2.0872094809079964E-2',
    },
    'F21': {
        'AB1': 'Growth',
        'AD3': 'Median',
        'AD60': '**USED IN CHART',
        'B66': '2023-\n24',
        'AD66': '0',
        'B67': '2024-\n25',
        'AD67': '5.5330448866911297E-2',
        'B68': '2025-\n26',
        'AD68': '4.8373646864058317E-2',
        'B69': '2026-\n27',
        'AD69': '5.0346160874108259E-2',
        'B70': '2027-\n28',
        'AD70': '3.1117015099901391E-2',
        'B71': '2028-\n29',
        'AD71': '1.835872215777723E-2',
        'B72': '2029-\n30',
        'AD72': '1.9895040061477021E-2',
        'B73': '2030-\n31',
        'AD73': '1.8965567729738675E-2',
        'B74': '2031-\n32',
        'AD74': '1.8858261833080148E-2',
    },
    'F22': {
        'U338': 'Vigintiles…',
        'U339': '1',
        'V339': '2',
        'W339': '3',
        'X339': '4',
        'Y339': '5',
        'Z339': '6',
        'AA339': '7',
        'AB339': '8',
        'AC339': '9',
        'AD339': '10',
        'AE339': '11',
        'AF339': '12',
        'AG339': '13',
        'AH339': '14',
        'AI339': '15',
        'AJ339': '16',
        'AK339': '17',
        'AL339': '18',
        'AM339': '19',
        'AN339': '20',
        'T342': '2024-\n25',
        'U342': '0',
        'V342': '1.2015108484203507E-2',
        'W342': '5.1565058286915155E-2',
        'X342': '5.4777611374788648E-2',
        'Y342': '4.3344182414399191E-2',
        'Z342': '4.3140271390741836E-2',
        'AA342': '4.5763706964852657E-2',
        'AB342': '4.3780645028501208E-2',
        'AC342': '4.245604701854111E-2',
        'AD342': '5.038173602831475E-2',
        'AE342': '5.1849258650039642E-2',
        'AF342': '4.7499475890198095E-2',
        'AG342': '5.0540668736078098E-2',
        'AH342': '5.8299605673901356E-2',
        'AI342': '5.7527480375839879E-2',
        'AJ342': '5.5630228612184141E-2',
        'AK342': '5.1609799060660322E-2',
        'AL342': '5.4808915474942044E-2',
        'AM342': '4.302437235566936E-2',
        'AN342': '-6.7499534051203014E-3',
        'T343': '2025-\n26',
        'U343': '0',
        'V343': '-5.2053548506020286E-2',
        'W343': '-2.7231834676950673E-2',
        'X343': '-3.0088424338304276E-2',
        'Y343': '-2.4060109899995075E-2',
        'Z343': '-2.1380706746344069E-2',
        'AA343': '-1.3567193841831249E-2',
        'AB343': '-1.2102658731336646E-2',
        'AC343': '-1.1744800999076932E-2',
        'AD343': '-8.4464484092933168E-3',
        'AE343': '-2.2829991699073737E-3',
        'AF343': '-3.1328513415875836E-3',
        'AG343': '-4.8068217783214795E-3',
        'AH343': '-5.8212535740141957E-3',
        'AI343': '-3.820539628637265E-3',
        'AJ343': '-5.470825528811285E-3',
        'AK343': '-9.154193742263339E-3',
        'AL343': '-1.3629208110582769E-2',
        'AM343': '-1.7681452880057402E-2',
        'AN343': '-3.8431460832767161E-2',
        'T344': '2026-\n27',
        'U344': '0',
        'V344': '3.6523807295631316E-2',
        'W344': '3.9683765784943814E-2',
        'X344': '4.1370171508345654E-2',
        'Y344': '2.7011771664581907E-2',
        'Z344': '2.0972452762158866E-2',
        'AA344': '1.1530069340972782E-2',
        'AB344': '9.5755727889352826E-3',
        'AC344': '6.0666439820291629E-3',
        'AD344': '4.0285664534660537E-3',
        'AE344': '-2.6695574356971896E-4',
        'AF344': '-5.4098867364960057E-4',
        'AG344': '-1.658620742706951E-3',
        'AH344': '-2.9772533578183991E-3',
        'AI344': '-4.392962501687081E-3',
        'AJ344': '-5.0217392786604531E-3',
        'AK344': '-5.0384865160855163E-3',
        'AL344': '-5.6654072424152657E-3',
        'AM344': '-5.9342387718963607E-3',
        'AN344': '-4.4873225198657218E-3',
        'T345': '2027-\n28',
        'U345': '0',
        'V345': '-3.6610846944398312E-2',
        'W345': '-2.2535474755657314E-2',
        'X345': '-1.7404054615191011E-2',
        'Y345': '-2.1112510218122216E-2',
        'Z345': '-1.8251051248937999E-2',
        'AA345': '-1.7018201033144553E-2',
        'AB345': '-1.8200984736052472E-2',
        'AC345': '-1.9774096280266718E-2',
        'AD345': '-1.9465248932590717E-2',
        'AE345': '-2.0108125807721366E-2',
        'AF345': '-2.1493207468867404E-2',
        'AG345': '-1.9878032368362497E-2',
        'AH345': '-2.0766734437560386E-2',
        'AI345': '-2.1583476495841358E-2',
        'AJ345': '-1.9331052875033561E-2',
        'AK345': '-2.0116809082748932E-2',
        'AL345': '-1.9917868712224007E-2',
        'AM345': '-2.0241450055365817E-2',
        'AN345': '-2.2965561330422379E-2',
        'T346': '2028-\n29',
        'U346': '0',
        'V346': '-8.63277336426993E-3',
        'W346': '-1.1519890206790007E-2',
        'X346': '-4.2552182665684946E-3',
        'Y346': '-6.4466063698986886E-3',
        'Z346': '-7.5172428536044444E-3',
        'AA346': '-9.4982915650716482E-3',
        'AB346': '-1.1700721441953887E-2',
        'AC346': '-1.1866938242065639E-2',
        'AD346': '-1.0826816635880143E-2',
        'AE346': '-1.2095717035696674E-2',
        'AF346': '-1.2990119561347324E-2',
        'AG346': '-1.160552825383665E-2',
        'AH346': '-1.3203515015267842E-2',
        'AI346': '-1.3870733064396901E-2',
        'AJ346': '-1.311593885574569E-2',
        'AK346': '-1.2603017886280932E-2',
        'AL346': '-1.3507603707767935E-2',
        'AM346': '-1.3909157094059044E-2',
        'AN346': '-1.3793129185180386E-2',
        'T350': 'This Parliament \n(2023-24 to \n2028-29)',
        'U350': '0',
        'V350': '-5.0300098945227689E-2',
        'W350': '2.7580131611880443E-2',
        'X350': '4.236827788464459E-2',
        'Y350': '1.7068208091038706E-2',
        'Z350': '1.5532730396040417E-2',
        'AA350': '1.5969278675088017E-2',
        'AB350': '1.0115326175889505E-2',
        'AC350': '3.9110084704887527E-3',
        'AD350': '1.4249330514807479E-2',
        'AE350': '1.563567966579793E-2',
        'AF350': '7.955668483029088E-3',
        'AG350': '1.1136442057838147E-2',
        'AH350': '1.3659110007813835E-2',
        'AI350': '1.1986756443385982E-2',
        'AJ350': '1.0954235396887668E-2',
        'AK350': '3.0742576805016242E-3',
        'AL350': '2.366361175134557E-4',
        'AM350': '-1.5993642759242754E-2',
        'AN350': '-8.3856445287762704E-2',
    },
    'F23': {
        'AP3': 'Working age',
        'AQ3': 'Pension age',
        'AR3': 'Children',
        'B66': '2023-\n24',
        'AP66': '0',
        'AQ66': '0',
        'AR66': '0',
        'B67': '2024-\n25',
        'AP67': '0.46312212944030762',
        'AQ67': '1.5476934611797333',
        'AR67': '-0.27621686458587646',
        'B68': '2025-\n26',
        'AP68': '1.15632563829422',
        'AQ68': '1.1182166635990143',
        'AR68': '0.51424205303192139',
        'B69': '2026-\n27',
        'AP69': '0.83012580871582031',
        'AQ69': '0.47172382473945618',
        'AR69': '-2.0342811942100525',
        'B70': '2027-\n28',
        'AP70': '0.98159760236740112',
        'AQ70': '-5.8621913194656372E-2',
        'AR70': '-2.0546108484268188',
        'B71': '2028-\n29',
        'AP71': '0.83668380975723267',
        'AQ71': '-0.41938871145248413',
        'AR71': '-2.6014506816864014',
    },
}

XL_NOTE = ("Stored value of a cell in the chart-data workbook RF links from the Spread thin page "
           "(full precision; the PDF chart prints no data label for it).")


def cell(sheet, ref):
    return WORKBOOK[sheet][ref]


def fy_of(label):
    """'2026-\\n27' or '2026-27' -> '2026-27'."""
    return re.sub(r"\s+", "", label)


def xadd(sheet, ref, label, cat, value, metric, unit, note="", **kw):
    raw = cell(sheet, ref)
    add("XL", f"sheet {sheet}, cell {ref}", raw, value, f"{label} | {cat} | {raw}",
        metric, unit, note=(XL_NOTE + (" " + note if note else "")), **kw)


# --- Figure 7: typical household's energy bill and support, by year ------------
F7_HH = "typical dual-fuel household on the Energy Price Cap paying by direct debit (Ofgem TDCV: 2,500 kWh electricity, 9,500 kWh gas)"
F7_BILL = {"C": "bill before any support", "I": "net of support, before any Council Tax rebate",
           "M": "net of support, including the Council Tax rebate"}
for r in range(4, 13):
    fy_ = cell("F7", f"A{r}")
    for col in "CDEFHILM":
        raw = cell("F7", f"{col}{r}")
        label = cell("F7", f"{col}3")
        common = dict(fy=fy_, geo="GB", model="arithmetic", table=FIG[7], col=f"{label} / {fy_}",
                      bench="administrative_fact" if fy_ <= "2025-26" else "different_model")
        if col in F7_BILL:
            xadd("F7", f"{col}{r}", label, fy_, dec(raw), "typical_energy_bill", "gbp",
                 c={"household_type": F7_HH, "scenario": F7_BILL[col], "price_basis": "2026-27 prices (CPI)"},
                 **common)
            continue
        if Decimal(raw) == 0:
            continue  # the support did not exist that year
        if col in "EL":
            continue  # flat payments (EBSS £400, Council Tax rebates £150 and £100) are design (rule 8)
        mk, hint, note = None, None, ""
        if col == "H":
            mk, hint = VAT, "Electricity VAT cut"
            note = "The whole cut (Table 6.1 line 2) as it falls in this financial year."
        elif col == "F":
            note = "Support announced before this Budget (policy costs removed from bills)."
        xadd("F7", f"{col}{r}", label, fy_, dec(raw), "energy_bill_change", "gbp", mk=mk, hint=hint, note=note,
             c={"household_type": F7_HH, "component": label, "price_basis": "2026-27 prices (CPI)",
                "sign_convention": "negative = reduction in the typical household's annual bill"},
             norm="£ as stored; sign as stored", **common)

# --- Figure 8: temporary AB26 policies by vigintile, 2026-27 and 2027-28 ---------
F8_KEYS = {"D": dict(mk=HEP), "E": dict(mk=FD), "F": dict(mk=VAT), "G": dict(mk=VAT),
           "J": dict(mk=PKG), "K": dict(mk=PKG)}
# README rule 9: the original six months and the three-month extension are
# parts of Table 6.1 line 2, so they keep its key as measure components.
F8_PART = {"F": "the original six-month cut (1 October 2026 to the end of Q1 2027)",
           "G": "the three-month extension (April to 1 July 2027)"}
for r in range(8, 27):
    n = int(cell("F8", f"C{r}"))
    for col in "DEFGJK":
        label = cell("F8", f"{col}6")
        raw = cell("F8", f"{col}{r}")
        pct = col == "K"
        xadd("F8", f"{col}{r}", label, f"vigintile {n}", dec(raw, 100 if pct else 1),
             "pct_change_after_tax_income" if pct else "average_household_income_change",
             "percent" if pct else "gbp", period=2028, tb="fiscal_year",
             c=dict({"income_group": f"vigintile_{n}", "income_axis": VIG_AXIS, "housing_costs": "ahc",
                     "unit_population": "households", "component": label, "sign_convention": SC_GAIN,
                     "horizon": TWO_YEARS, "price_basis": "cash terms", "modelling_geography": F8_GEO},
                    **({"row_type": "measure_component", "measure_part": F8_PART[col]} if col in F8_PART else {})),
             norm="share of income as stored × 100 → percent" if pct else "£ per household per year as stored",
             hint=COLA_PKG if col in "JK" else label, table=FIG[8], col=f"{label} / vigintile {n}",
             note="Vigintile 1 is blank in the workbook. These values match Spread thin v2 (the poorer half's average of about £145).",
             **F8_KEYS[col])

# --- Figure 9: LHA unfreeze gainers and Your First Home access, by decile -------
F9_C = {"unit_population": "private renting families (benefit units)", "income_axis": DEC_AXIS,
        "housing_costs": "ahc"}
for r in range(6, 16):
    n = int(cell("F9", f"L{r}"))
    xadd("F9", f"M{r}", cell("F9", "M5"), f"decile {n}", dec(cell("F9", f"M{r}")), "gainer_count", "families",
         fy="2027-28", geo="England", pk=O_LHA, c=dict(F9_C, income_group=f"decile_{n}"),
         hint="Would benefit if LHA were unfrozen", table=FIG[9], col=f"{cell('F9', 'M5')} / decile {n}")
    xadd("F9", f"N{r}", cell("F9", "N5"), f"decile {n}", dec(cell("F9", f"N{r}")), "eligible_count", "families",
         fy="2027-28", geo="England", mk=YFH, c=dict(F9_C, income_group=f"decile_{n}"),
         hint="Could access Your First Home", table=FIG[9], col=f"{cell('F9', 'N5')} / decile {n}",
         note="Families with income under the scheme cap, able to borrow 77.5 per cent of the regional median house price and save a 2.5 per cent deposit (Figure 9 notes).")
for r, grp in ((19, "bottom_half"), (20, "top_half")):
    half = cell("F9", f"L{r}")
    xadd("F9", f"M{r}", cell("F9", "M5"), half, dec(cell("F9", f"M{r}")), "affected_share", "share",
         fy="2027-28", geo="England", pk=O_LHA,
         c=dict(F9_C, income_group=grp, denominator="private renting families who would benefit if LHA were unfrozen"),
         hint="Would benefit if LHA were unfrozen", table=FIG[9], col=f"{cell('F9', 'M5')} / {half}",
         note="The text rounds it to 91 per cent.")
    xadd("F9", f"N{r}", cell("F9", "N5"), half, dec(cell("F9", f"N{r}")), "affected_share", "share",
         fy="2027-28", geo="England", mk=YFH,
         c=dict(F9_C, income_group=grp, denominator="private renting families who could access Your First Home"),
         hint="Could access Your First Home", table=FIG[9], col=f"{cell('F9', 'N5')} / {half}",
         note="The text rounds it to 76 per cent.")
xadd("F9", "M22", cell("F9", "M5"), "total", dec(cell("F9", "M22")), "gainer_count", "families",
     fy="2027-28", geo="England", pk=O_LHA, c=dict(F9_C, income_group="all"),
     hint="Would benefit if LHA were unfrozen", table=FIG[9], col=f"{cell('F9', 'M5')} / total",
     note="The text says 'over a million families'.")
xadd("F9", "N22", cell("F9", "N5"), "total", dec(cell("F9", "N22")), "eligible_count", "families",
     fy="2027-28", geo="England", mk=YFH, c=dict(F9_C, income_group="all"),
     hint="Could access Your First Home", table=FIG[9], col=f"{cell('F9', 'N5')} / total")

# --- Figure 10: tax decisions since March, and a continued Fuel Duty freeze ----
F10_ROWS = {
    46: dict(pk=P_OBR_TAX, att="restated", model="obr_efo_forecast",
             note=RESTATED_OBR + " Table 3.1 (direct effect of tax measures), sign flipped."),
    47: dict(mk=FD, att="restated", model="hmt_costing_obr_certified",
             note=RESTATED_HMT + " line 3 (-575 and -780). The Figure 10 note says the series shows 'Fuel Duty changes announced in May and October', but its values equal line 3 alone."),
    48: dict(pk=O_FD_FREEZE, model="arithmetic",
             note="The OBR's constant-duty-rate alternative less its central Fuel Duty forecast (rows 39-40)."),
    49: dict(mk=BANK, att="restated", model="hmt_costing_obr_certified", note=RESTATED_HMT + " line 55."),
    50: dict(mk=WDA, att="restated", model="hmt_costing_obr_certified", note=RESTATED_HMT + " line 58."),
    51: dict(pk=P_SAV_PROP, att="restated", model="hmt_costing_obr_certified",
             note=RESTATED_HMT + " lines 61 and 62, summed."),
    52: dict(pk=P_OBR_ADMIN, att="restated", model="obr_efo_forecast",
             note=RESTATED_OBR + " Table 3.1 ('Tax administration, compliance and debt collection measures')."),
    53: dict(pk=P_RF_OTHER_TAX, model="arithmetic",
             note="RF's residual: net direct effects less the five named series (rows 47 and 49-52)."),
    54: dict(pk=O_TAX_FREEZE, model="arithmetic", note="Row 46 plus row 48."),
}
for r, kw in F10_ROWS.items():
    label = cell("F10", f"B{r}")
    for col in "CDEFGH":
        fy_ = fy_of(cell("F10", f"{col}45"))
        xadd("F10", f"{col}{r}", label, fy_, dec(cell("F10", f"{col}{r}"), 1e9), "revenue_change", "gbp",
             fy=fy_, c={"sign_convention": SC_F10}, norm="£ billion as stored × 1e9 → £; sign as RF plots it",
             hint=label, table=FIG[10], col=f"{label} / {fy_}", **kw)
xadd("F10", "J49", cell("F10", "B49"), cell("F10", "J45"), dec(cell("F10", "J49"), 1e9), "revenue_change", "gbp",
     period=2032, tb="fiscal_year", mk=BANK, att="restated", model="hmt_costing_obr_certified",
     c={"sign_convention": SC_F10, "horizon": "2026-27 to 2031-32"}, kind="cumulative",
     norm="£ billion as stored × 1e9 → £", hint=cell("F10", "B49"), table=FIG[10],
     col=f"{cell('F10', 'B49')} / {cell('F10', 'J45')}",
     note=RESTATED_HMT + " line 55, summed. The text rounds it to 'around £1.5 billion'.")

# --- Figure 20: permanent tax and benefit changes this Parliament, by vigintile -
F20_KEYS = {
    "D": dict(base="rf_start_of_parliament_policy",
              note="Measures announced before AB26 this Parliament (Stairway to headroom Figure 20 lists them)."),
    "E": dict(base="rf_start_of_parliament_policy",
              note="Measures announced before AB26 this Parliament (Stairway to headroom Figure 20 lists them)."),
    "F": dict(mk=PTA, note="RF's workbook label for the Pension Tax Allowance. An unplotted component of 'AB26 Changes'."),
    "G": dict(pk=P_SAV_PROP, note="The AB26 rate rises (Table 6.1 lines 61 and 62). An unplotted component of 'AB26 Changes'."),
    "H": dict(base="rf_start_of_parliament_policy",
              note="Measures announced before AB26 this Parliament (Stairway to headroom Figure 20 lists them)."),
    "I": dict(mk=MGD, note="An unplotted component of 'AB26 Changes'."),
    "J": dict(pk=P_GAS_SC, note="An unplotted component of 'AB26 Changes'."),
    "K": dict(pk=P_AB26_PERM,
              note="Equals columns F + G + I + J. The PDF's Figure 20 note lists the Pension Tax Allowance, gas standing charges and the Machine Games Levy but not the property and savings rate rise."),
    "L": dict(pk=P_PARLIAMENT, base="rf_start_of_parliament_policy"),
    "M": dict(pk=P_PARLIAMENT, base="rf_start_of_parliament_policy"),
}
for r in range(8, 27):
    n = int(cell("F20", f"C{r}"))
    for col in "DEFGHIJKLM":
        label = cell("F20", f"{col}6")
        raw = cell("F20", f"{col}{r}")
        pct = col == "M"
        kw = dict(F20_KEYS[col])
        note = kw.pop("note", "")
        xadd("F20", f"{col}{r}", label, f"vigintile {n}", dec(raw, 100 if pct else 1),
             "pct_change_after_tax_income" if pct else "average_household_income_change",
             "percent" if pct else "gbp", fy="2029-30",
             c={"income_group": f"vigintile_{n}", "income_axis": VIG_AXIS, "housing_costs": "ahc",
                "unit_population": "households", "component": label, "sign_convention": SC_GAIN,
                "price_basis": "2026-27 prices (CPI)"},
             norm="share of income as stored × 100 → percent" if pct else "£ per household per year as stored",
             hint=label, table=FIG[20], col=f"{label} / vigintile {n}",
             note=(note + " Vigintile 1 is blank in the workbook.").strip(), **kw)

# --- Figure 21: median non-pensioner income growth since 2023-24 ---------------
for r in range(67, 75):
    fy_ = fy_of(cell("F21", f"B{r}"))
    out = fy_ == "2024-25"
    xadd("F21", f"AD{r}", f"{cell('F21', 'AB1')}, {cell('F21', 'AD3')}", fy_, dec(cell("F21", f"AD{r}"), 100),
         "real_income_growth", "percent", fy=fy_, kind="cumulative",
         c={"statistic": "median", "unit_population": "non-pensioners", "housing_costs": "ahc",
            "horizon": f"2023-24 to {fy_}"},
         model="survey_microdata" if out else "landman_ttm",
         bench="administrative_fact" if out else "different_model",
         norm="growth as stored (a fraction) × 100 → percent", table=FIG[21], col=f"Median / {fy_}",
         note="Column AD is marked '**USED IN CHART' (cell AD60)." + (" 2024-25 is HBAI outturn." if out else " A projection."))

# --- Figure 22: non-pensioner income growth by vigintile ----------------------
F22_ROWS = {342: "2024-25", 343: "2025-26", 344: "2026-27", 345: "2027-28", 346: "2028-29", 350: "2028-29"}
F22_PREV = {"2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26", "2027-28": "2026-27", "2028-29": "2027-28"}
F22_COLS = ["V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN"]
for r, fy_ in F22_ROWS.items():
    cat = re.sub(r"\s*\n\s*", " ", cell("F22", f"T{r}")).strip()
    whole = r == 350
    for col in F22_COLS:
        n = int(cell("F22", f"{col}339"))
        out = fy_ == "2024-25" and not whole
        xadd("F22", f"{col}{r}", f"Vigintile {n}", cat, dec(cell("F22", f"{col}{r}"), 100),
             "real_income_growth", "percent", fy=fy_, kind="cumulative" if whole else "point",
             c={"statistic": "average equivalised household disposable income", "unit_population": "non-pensioners",
                "housing_costs": "ahc", "income_group": f"vigintile_{n}",
                "income_axis": "non-pensioner equivalised household disposable income vigintile, after housing costs",
                "horizon": "2023-24 to 2028-29 (this Parliament)" if whole else f"{F22_PREV[fy_]} to {fy_}"},
             model="survey_microdata" if out else "landman_ttm",
             bench="administrative_fact" if out else "different_model",
             norm="growth as stored (a fraction) × 100 → percent", table=FIG[22], col=f"Vigintile {n} / {cat}",
             note="Vigintile 1 (excluded: 'concerns about the reliability of data') is a 0 placeholder and not staged."
             + (" 2024-25 is HBAI outturn." if out else ""))

# --- Figure 23: change in relative AHC poverty since 2023-24 -------------------
for r in range(67, 72):
    fy_ = fy_of(cell("F23", f"B{r}"))
    out = fy_ == "2024-25"
    for col, pop in (("AP", "working-age adults"), ("AQ", "pension-age adults"), ("AR", "children")):
        label = cell("F23", f"{col}3")
        xadd("F23", f"{col}{r}", label, fy_, dec(cell("F23", f"{col}{r}")), "poverty_rate_change",
             "percentage_points", fy=fy_, kind="cumulative",
             c={"unit_population": pop, "housing_costs": "ahc", "poverty_line": "relative_60_median",
                "horizon": f"2023-24 to {fy_}", "sign_convention": "positive = rise in the poverty rate"},
             model="survey_microdata" if out else "landman_ttm",
             bench="administrative_fact" if out else "different_model",
             norm="percentage points as stored", table=FIG[23], col=f"{label} / {fy_}",
             note="2023-24 is the zero base and not staged." + (" 2024-25 is HBAI outturn." if out else ""))


# ===========================================================================
# Write, and check against the primaries
# ===========================================================================
def write():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for row in ROWS:
            gz.write((json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    OUT.write_bytes(buf.getvalue())


def _squash(text):
    """Whitespace and ASCII hyphens removed: line breaks and hyphenation differ
    between the PDF text extractors and the printed page."""
    text = html.unescape(text).replace(" ", " ").replace("­", "")
    return re.sub(r"[\s\-]+", "", text)


def _html_text(data):
    text = data.decode("utf-8")
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    return re.sub(r"<[^>]+>", " ", text)


def _pdf_text(path):
    out = []
    for args in (["-layout"], ["-raw"], []):
        out.append(subprocess.run(["pdftotext", *args, str(path), "-"], check=True,
                                  capture_output=True).stdout.decode("utf-8"))
    return "\n".join(out)


def _workbook_cells(path):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    z = zipfile.ZipFile(path)
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = {s.get("name"): "xl/" + rels[s.get("{%s}id" % ns["r"])].lstrip("/").removeprefix("xl/")
              for s in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", ns)}
    shared = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))
              for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    out = {}
    for name in WORKBOOK:
        cells = {}
        for c in ET.fromstring(z.read(sheets[name])).iter("{%s}c" % ns["m"]):
            v = c.find("m:v", ns)
            if v is not None:
                cells[c.get("r")] = shared[int(v.text)] if c.get("t") == "s" else v.text
        out[name] = cells
    return out


def check_primaries(folder):
    folder = Path(folder)
    problems = []
    manifest = [json.loads(line) for line in (HERE / "manifest.jsonl").read_text().splitlines() if line.strip()]
    by_sha = {m["sha256"]: m for m in manifest}
    texts, by_doc_sha = {}, {}
    for key, doc in DOCS.items():
        path = folder / doc["file"]
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        by_doc_sha[doc["sha"]] = key
        if sha != doc["sha"]:
            problems.append(f"{key}: {path.name} hashes to {sha}, not {doc['sha']}")
        m = by_sha.get(doc["sha"])
        if not m:
            problems.append(f"{key}: sha256 not in manifest.jsonl")
        elif m["bytes"] != len(data) or m["url"] != doc["url"]:
            problems.append(f"{key}: manifest bytes or url differ")
        if path.suffix == ".html":
            texts[key] = _squash(_html_text(data))
        elif path.suffix == ".pdf":
            texts[key] = _squash(_pdf_text(path))
    stored = _workbook_cells(folder / DOCS["XL"]["file"])
    for sheet, cells in WORKBOOK.items():
        for ref, raw in cells.items():
            if stored[sheet].get(ref) != raw:
                problems.append(f"workbook {sheet}!{ref}: embedded {raw!r}, stored {stored[sheet].get(ref)!r}")
    for i, row in enumerate(ROWS):
        key = by_doc_sha[row["publication"]["primary_sha256"]]
        if key == "XL":
            continue
        if _squash(row["quote"]) not in texts[key]:
            problems.append(f"row {i} ({key} {row['publication']['locator']}): quote not found: {row['quote']!r}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check-primaries", metavar="DIR")
    args = ap.parse_args()
    write()
    print(f"wrote {OUT.name}: {len(ROWS)} rows, sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    if args.check_primaries:
        problems = check_primaries(args.check_primaries)
        for p in problems:
            print("  " + p)
        print(f"primaries: {len(problems)} problems")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
