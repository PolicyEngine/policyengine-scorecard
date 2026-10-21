"""Build the policy-experiment specs: past measures as changes to modern law.

Each experiment restates one registry measure on modern law
(docs/uk_replay/POLICY_EXPERIMENTS.md). The arithmetic behind every
counterfactual value is here, next to its source, and the builder binds each
event registry by SHA-256.

Modern-law values are pe-uk 2.132.6's processed values for the year (its
parameter files, read at the release tag). A construction states only the
pre-measure world; where an engine's current law already equals it, the run
reports construction_noop, which is how a measure missing from an engine's
law shows up.

    python3 -m pipeline.uk_experiment_specs            # write data/uk/experiments/<event>.json
    python3 -m pipeline.uk_experiment_specs --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / "data" / "uk" / "experiments"
LAST = 2035  # windows run to here; the population's data years bound the run

NICS = ["ni_class_1_employee", "ni_class_1_employer", "ni_class_2", "ni_class_4"]


def window(first: int, last: int = LAST) -> str:
    return f"{first}-01-01.{last}-12-31"


def yearly(values: dict[int, float]) -> dict[str, float]:
    return {window(year, year): value for year, value in sorted(values.items())}


def money(value: float, places: int = 2) -> float:
    return round(value + 0.0, places)


def nics_group(obr_heads: list[str]) -> dict:
    return {
        "obr_heads": obr_heads,
        "pe_variables": NICS,
        "channel": "tax",
        "base_sheet": "NICS",
        "pe_base_comparable": True,
    }


INCOME_TAX = {
    "obr_heads": ["Income tax"],
    "pe_variables": ["income_tax"],
    "channel": "tax",
    "base_sheet": "IT",
    "pe_base_comparable": True,
}


def uc_group(variables=("universal_credit",)) -> dict:
    return {
        "obr_heads": ["Welfare inside cap"],
        "pe_variables": list(variables),
        "channel": "spending",
        "base_sheet": "Welfare in",
        "pe_base_comparable": False,
    }


# --- shared reforms ------------------------------------------------------------

# The 1.25pp NICs increase that the Health and Social Care Levy replaced, added
# to modern rates. pe-uk 2.132.6 processed rates: employee main 8% and
# additional 2% from 2024; employer 13.8% in 2024 (its 15% is keyed
# 2025-01-01); Class 4 main 6% and additional 2% from 2024.
PLUS_125 = {
    "gov.hmrc.national_insurance.class_1.rates.employee.main": {window(2024): 0.0925},
    "gov.hmrc.national_insurance.class_1.rates.employee.additional": {
        window(2024): 0.0325
    },
    "gov.hmrc.national_insurance.class_1.rates.employer": {
        window(2024, 2024): 0.1505,
        window(2025): 0.1625,
    },
    "gov.hmrc.national_insurance.class_4.rates.main": {window(2024): 0.0725},
    "gov.hmrc.national_insurance.class_4.rates.additional": {window(2024): 0.0325},
}
PLUS_125_NOTE = (
    "The levy was 1.25% on the same earnings and profits as NICs, so the "
    "construction adds 1.25pp to every modern Class 1 and Class 4 rate "
    "(employee 8%→9.25%, additional 2%→3.25%, employer 13.8%→15.05% in 2024 "
    "and 15%→16.25% from 2025, Class 4 6%→7.25% and 2%→3.25%). Missing legs: "
    "the levy on earnings above State Pension age, and the separate dividend "
    "rate increase (its own measure)."
)
PLUS_125_SOURCES = [
    "Health and Social Care Levy Act 2021 s. 2-3 (https://www.legislation.gov.uk/ukpga/2021/28)",
    "pe-uk 2.132.6 parameters gov/hmrc/national_insurance/class_1/rates/*.yaml and class_4/rates/*.yaml",
]

# The basic rate at 19% from April 2024 (Spring Statement 2022), on modern
# law: the UK basic rate, and the savings and property basic rates, which
# pe-uk 2.132.6 keeps in their own schedules (20% to April 2027, 22% after,
# the Autumn Budget 2025 +2pp kept on top of the cut).
BASIC_19 = {
    "gov.hmrc.income_tax.rates.uk[0].rate": {window(2024): 0.19},
    "gov.hmrc.income_tax.rates.savings.basic": {
        window(2024, 2026): 0.19,
        window(2027): 0.21,
    },
    "gov.hmrc.income_tax.rates.property.basic": {
        window(2024, 2026): 0.19,
        window(2027): 0.21,
    },
}
BASIC_19_NOTE = (
    "The UK basic rate on non-savings, savings and property income falls to "
    "19% from 2024-25 (21% from 2027-28, keeping Autumn Budget 2025's +2pp "
    "on savings and property income). Scottish rates on non-savings income "
    "are devolved and unchanged; dividend rates are separate and unchanged. "
    "The Welsh adjustment and block-grant effects are separate rows."
)
BASIC_19_SOURCES = [
    "Spring Statement 2022, para 4.11 (https://www.gov.uk/government/publications/spring-statement-2022-documents)",
    "pe-uk 2.132.6 parameters gov/hmrc/income_tax/rates/{uk,savings,property}.yaml",
]

# Primary threshold and lower profits limit without the July 2022 alignment.
# The pre-measure 2022-23 level was £9,880 (£190 a week); the default April
# 2023 uprating is September 2022 CPI, 10.1% (ONS), giving £10,878 (£209.19 a
# week), which the later freezes (Autumn Statement 2022 to April 2028,
# Autumn Budget 2025 to April 2031) then hold.
PT_CF_ANNUAL = round(9880 * 1.101)
PT_CF_WEEKLY = money(PT_CF_ANNUAL / 52)
PT_LPL = {
    "gov.hmrc.national_insurance.class_1.thresholds.primary_threshold": {
        window(2024, 2030): PT_CF_WEEKLY
    },
    "gov.hmrc.national_insurance.class_4.thresholds.lower_profits_limit": {
        window(2024, 2030): float(PT_CF_ANNUAL)
    },
}

# Secondary threshold without the freeze from April 2023: £175 a week
# (£9,100) uprated by September 2022 CPI (10.1%) and September 2023 CPI
# (6.7%), both ONS. From April 2025 Autumn Budget 2024 sets £5,000, which
# the counterfactual keeps.
ST_CF_2024 = money(175 * 1.101 * 1.067)

# Double lock in 2022-23: State Pension and the standard minimum guarantee
# rose 3.1% (September 2021 CPI) instead of 8.3% (May-July 2021 earnings
# growth), Social Security (Up-rating of Benefits) Act 2022. Every later
# amount scales by 1.083 / 1.031.
DOUBLE_LOCK = 1.083 / 1.031
NEW_SP = {2024: 221.20, 2025: 230.25, 2026: 241.30}
BASIC_SP = {2024: 169.50, 2025: 176.45, 2026: 184.90}
SMG_SINGLE = {2024: 218.15, 2025: 227.10, 2026: 238.00}
SMG_COUPLE = {2024: 332.95, 2025: 346.60, 2026: 363.25}

# Universal Credit taper 55% and the £500 a year work-allowance increase
# (Autumn Budget 2021): 293 → 335 and 515 → 557 a month in November 2021.
# Later CPI upratings apply to either level alike, so the counterfactual
# scales each modern amount by 293/335 or 515/557, rounded to £1 as DWP does.
WA_WITH = {2024: 404, 2025: 411, 2026: 427}
WA_WITHOUT = {2024: 673, 2025: 684, 2026: 710}

SDLT_PRE_2022 = {
    "gov.hmrc.stamp_duty.residential.purchase.main.subsequent[1].rate": 0.02,
    "gov.hmrc.stamp_duty.residential.purchase.main.subsequent[1].threshold": 125_000.0,
    "gov.hmrc.stamp_duty.residential.purchase.main.first.rate[1].threshold": 300_000.0,
    "gov.hmrc.stamp_duty.residential.purchase.main.first.max": 500_000.0,
}
SDLT_GROWTH_PLAN = {
    "gov.hmrc.stamp_duty.residential.purchase.main.subsequent[1].rate": 0.0,
    "gov.hmrc.stamp_duty.residential.purchase.main.subsequent[1].threshold": 125_000.0,
    "gov.hmrc.stamp_duty.residential.purchase.main.first.rate[1].threshold": 425_000.0,
    "gov.hmrc.stamp_duty.residential.purchase.main.first.max": 625_000.0,
}
SDLT_SOURCES = [
    "Stamp Duty Land Tax (Reduction) Act 2022 (https://www.legislation.gov.uk/ukpga/2022/58)",
    "pe-uk 2.132.6 parameters gov/hmrc/stamp_duty/residential/purchase/main/*",
]


def stamp_duty_group() -> dict:
    return {
        "obr_heads": ["Stamp duty"],
        "pe_variables": ["stamp_duty_land_tax"],
        "channel": "tax",
        "base_sheet": "PTT",
        "pe_base_comparable": False,
    }


def experiments() -> dict[str, dict]:
    ab21 = "autumn_budget_2021"
    ss22 = "spring_statement_2022"
    as22 = "autumn_statement_2022"
    specs = {
        ab21: {
            "obr_forecast_vintage": "October 2021",
            "experiments": [
                {
                    "experiment_id": "ab2021_hscl_nics_plus_1_25pp",
                    "measure_key": f"{ab21}__health_and_social_care_levy_introduced_from_april_2022_gross_yield",
                    "construction": "forward_on_modern_law",
                    "reform": PLUS_125,
                    "heads": [
                        nics_group(["Health and social care levy", "NICs"]),
                        INCOME_TAX,
                    ],
                    "magnitude_check": "scaled",
                    "mirror_of": f"{as22}:as2022_reverse_nics_1_25pp",
                    "note": "Modern law has no levy, so the experiment adds it. "
                    + PLUS_125_NOTE,
                    "sources": PLUS_125_SOURCES,
                },
                {
                    "experiment_id": "ab2021_dividend_rates_plus_1_25pp",
                    "measure_key": f"{ab21}__increase_rates_of_dividend_tax_by_1_25_from_april_2022",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.rates.dividends[0].rate": {
                            window(2024, 2025): 0.075,
                            window(2026): 0.095,
                        },
                        "gov.hmrc.income_tax.rates.dividends[1].rate": {
                            window(2024, 2025): 0.325,
                            window(2026): 0.345,
                        },
                        "gov.hmrc.income_tax.rates.dividends[2].rate": {
                            window(2024): 0.381
                        },
                        "gov.hmrc.income_tax.rates.dividends[3].rate": {
                            window(2024): 0.381
                        },
                    },
                    "heads": [INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": (
                        "Modern dividend rates are 8.75%, 33.75% and 39.35% (10.75% and "
                        "35.75% from April 2026, Autumn Budget 2025); the reversal takes "
                        "1.25pp off each, keeping the 2026 increase. pe-uk's fourth "
                        "dividend bracket (39.35% above £10m) moves with the additional rate."
                    ),
                    "sources": [
                        "Finance Act 2022 s. 4 (https://www.legislation.gov.uk/ukpga/2022/3/section/4/enacted)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/rates/dividends.yaml",
                    ],
                },
                {
                    "experiment_id": "ab2021_uc_taper_55_work_allowance_500",
                    "measure_key": f"{ab21}__universal_credit_reduce_taper_rate_from_63p_to_55p_and_500_p_a_increase",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.dwp.universal_credit.means_test.reduction_rate": {
                            window(2024): 0.63
                        },
                        "gov.dwp.universal_credit.means_test.work_allowance.with_housing": yearly(
                            {y: float(round(v * 293 / 335)) for y, v in WA_WITH.items()}
                        ),
                        "gov.dwp.universal_credit.means_test.work_allowance.without_housing": yearly(
                            {
                                y: float(round(v * 515 / 557))
                                for y, v in WA_WITHOUT.items()
                            }
                        ),
                    },
                    "heads": [uc_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the 63% taper and removes the £500 a year work-allowance "
                        "increase: modern monthly allowances scaled by 293/335 (with housing) "
                        "and 515/557 (without), rounded to £1, for 2024-25 to 2026-27."
                    ),
                    "sources": [
                        "The Universal Credit (Work Allowance and Taper) (Amendment) Regulations 2021 (https://www.legislation.gov.uk/uksi/2021/1283/made)",
                        "pe-uk 2.132.6 parameters gov/dwp/universal_credit/means_test/{reduction_rate,work_allowance}.yaml",
                    ],
                },
                {
                    "experiment_id": "ab2021_state_pension_double_lock",
                    "measure_key": f"{ab21}__state_pension_and_pension_credit_uprate_with_double_lock_in_2022_23",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.dwp.state_pension.new_state_pension.amount": yearly(
                            {y: money(v * DOUBLE_LOCK) for y, v in NEW_SP.items()}
                        ),
                        "gov.dwp.state_pension.basic_state_pension.amount": yearly(
                            {y: money(v * DOUBLE_LOCK) for y, v in BASIC_SP.items()}
                        ),
                        "gov.dwp.pension_credit.guarantee_credit.minimum_guarantee.SINGLE": yearly(
                            {y: money(v * DOUBLE_LOCK) for y, v in SMG_SINGLE.items()}
                        ),
                        "gov.dwp.pension_credit.guarantee_credit.minimum_guarantee.COUPLE": yearly(
                            {y: money(v * DOUBLE_LOCK) for y, v in SMG_COUPLE.items()}
                        ),
                    },
                    "heads": [
                        {
                            "obr_heads": ["Welfare outside cap"],
                            "pe_variables": ["state_pension"],
                            "channel": "spending",
                            "base_sheet": "Welfare out",
                            "pe_base_comparable": False,
                        },
                        uc_group(["pension_credit"]),
                    ],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the 8.3% earnings uprating in April 2022: every modern "
                        "new and basic State Pension and standard minimum guarantee amount "
                        "for 2024-25 to 2026-27 scaled by 1.083/1.031."
                    ),
                    "sources": [
                        "Social Security (Up-rating of Benefits) Act 2022 s. 1 (https://www.legislation.gov.uk/ukpga/2022/5/section/1/enacted)",
                        "pe-uk 2.132.6 parameters gov/dwp/state_pension/*/amount.yaml, gov/dwp/pension_credit/guarantee_credit/minimum_guarantee.yaml",
                    ],
                },
            ],
        },
        ss22: {
            "obr_forecast_vintage": "March 2022",
            "experiments": [
                {
                    "experiment_id": "ss2022_basic_rate_19",
                    "measure_key": f"{ss22}__income_tax_reduce_basic_rate_from_20_to_19_from_april_2024",
                    "construction": "forward_on_modern_law",
                    "reform": BASIC_19,
                    "heads": [INCOME_TAX],
                    "magnitude_check": "scaled",
                    "mirror_of": f"{as22}:as2022_maintain_basic_rate_20",
                    "note": "The cut never took effect, so modern law lacks it. "
                    + BASIC_19_NOTE,
                    "sources": BASIC_19_SOURCES,
                },
                {
                    "experiment_id": "ss2022_basic_rate_19_welfare",
                    "measure_key": f"{ss22}__income_tax_reduce_basic_rate_from_20_to_19_from_april_20243",
                    "construction": "forward_on_modern_law",
                    "reform": BASIC_19,
                    "heads": [uc_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "The same change, scored on the measure's welfare row: higher "
                        "net earnings lower Universal Credit. " + BASIC_19_NOTE
                    ),
                    "sources": BASIC_19_SOURCES,
                },
                {
                    "experiment_id": "ss2022_nics_primary_threshold_lpl",
                    "measure_key": f"{ss22}__national_insurance_increase_annual_primary_threshold_and_lower_profits_l",
                    "construction": "reversal_on_modern_law",
                    "reform": PT_LPL,
                    "heads": [
                        nics_group(["Health and social care levy", "NICs"]),
                        INCOME_TAX,
                    ],
                    "magnitude_check": "scaled",
                    "note": (
                        f"Without the July 2022 alignment the primary threshold and lower "
                        f"profits limit would be £9,880 uprated by September 2022 CPI (10.1%) "
                        f"to £{PT_CF_ANNUAL:,} (£{PT_CF_WEEKLY} a week) from April 2023, then held "
                        "by the later freezes. Modern law has £12,570. The modern employee "
                        "rate is 8%, against 12% plus the 1.25% levy when the OBR costed it."
                    ),
                    "sources": [
                        "National Insurance Contributions (Increase of Thresholds) Act 2022 (https://www.legislation.gov.uk/ukpga/2022/16)",
                        "ONS CPI annual rate, September 2022: 10.1%",
                        "pe-uk 2.132.6 parameters class_1/thresholds/primary_threshold.yaml, class_4/thresholds/lower_profits_limit.yaml",
                    ],
                },
                {
                    "experiment_id": "ss2022_nics_primary_threshold_lpl_welfare",
                    "measure_key": f"{ss22}__national_insurance_increase_annual_primary_threshold_and_lower_profits_l_2",
                    "construction": "reversal_on_modern_law",
                    "reform": PT_LPL,
                    "heads": [uc_group()],
                    "magnitude_check": "scaled",
                    "note": "The same change, scored on the measure's welfare row.",
                    "sources": [
                        "National Insurance Contributions (Increase of Thresholds) Act 2022 (https://www.legislation.gov.uk/ukpga/2022/16)",
                    ],
                },
            ],
        },
        as22: {
            "obr_forecast_vintage": "November 2022",
            "experiments": [
                {
                    "experiment_id": "as2022_reverse_nics_1_25pp",
                    "measure_key": f"{as22}__national_insurance_reverse_temporary_1_25pp_increase_in_nics_rates_from",
                    "construction": "reversal_on_modern_law",
                    "reform": PLUS_125,
                    "heads": [
                        nics_group(["Health and social care levy", "NICs"]),
                        INCOME_TAX,
                        uc_group(),
                    ],
                    "magnitude_check": "scaled",
                    "mirror_of": f"{ab21}:ab2021_hscl_nics_plus_1_25pp",
                    "note": "Modern law has neither the increase nor the levy, so the reversal restores the levy. "
                    + PLUS_125_NOTE,
                    "sources": PLUS_125_SOURCES,
                },
                {
                    "experiment_id": "as2022_maintain_basic_rate_20",
                    "measure_key": f"{as22}__income_tax_maintaining_the_basic_rate_at_20",
                    "construction": "reversal_on_modern_law",
                    "reform": BASIC_19,
                    "heads": [INCOME_TAX, uc_group()],
                    "magnitude_check": "scaled",
                    "mirror_of": f"{ss22}:ss2022_basic_rate_19",
                    "note": "The pre-measure world had the 19% basic rate. "
                    + BASIC_19_NOTE,
                    "sources": BASIC_19_SOURCES,
                },
                {
                    "experiment_id": "as2022_employer_secondary_threshold_freeze",
                    "measure_key": f"{as22}__national_insurance_maintain_employer_secondary_threshold_at_current_leve",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {
                            window(2024, 2024): ST_CF_2024
                        }
                    },
                    "heads": [nics_group(["NICs"]), INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": (
                        f"Without the freeze the threshold would be £175 a week uprated by "
                        f"September 2022 and September 2023 CPI (10.1%, 6.7%) to £{ST_CF_2024} in "
                        "2024-25. From April 2025 Autumn Budget 2024's £5,000 supersedes the "
                        "freeze on modern law, so later years have nothing to move."
                    ),
                    "sources": [
                        "Autumn Statement 2022 Table 5.1 (https://www.gov.uk/government/publications/autumn-statement-2022-documents)",
                        "ONS CPI annual rate: September 2022 10.1%, September 2023 6.7%",
                        "pe-uk 2.132.6 parameters class_1/thresholds/secondary_threshold.yaml",
                    ],
                },
                {
                    "experiment_id": "as2022_additional_rate_threshold_125140",
                    "measure_key": f"{as22}__income_tax_reduce_additional_rate_threshold_from_150_000_to_125_140_from",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.rates.uk[2].threshold": {
                            window(2024): 150_000.0
                        },
                        "gov.hmrc.income_tax.rates.dividends[2].threshold": {
                            window(2024): 150_000.0
                        },
                    },
                    "heads": [INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the £150,000 additional-rate threshold for non-savings, "
                        "savings (pe-uk's savings bands follow the UK thresholds) and "
                        "dividend income. Scottish thresholds are devolved and unchanged."
                    ),
                    "sources": [
                        "Finance Act 2023 s. 4 (https://www.legislation.gov.uk/ukpga/2023/1/section/4/enacted)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/rates/{uk,dividends}.yaml",
                    ],
                },
                {
                    "experiment_id": "as2022_dividend_allowance_500",
                    "measure_key": f"{as22}__income_tax_reduce_the_dividend_allowance_from_2_000_to_1_000_from_april",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.allowances.dividend_allowance": {
                            window(2024): 2_000.0
                        }
                    },
                    "heads": [INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": "Restores the £2,000 dividend allowance (modern law: £500).",
                    "sources": [
                        "Finance Act 2023 s. 5 (https://www.legislation.gov.uk/ukpga/2023/1/section/5/enacted)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/allowances/dividend_allowance.yaml",
                    ],
                },
                {
                    "experiment_id": "as2022_cgt_annual_exempt_amount_3000",
                    "measure_key": f"{as22}__capital_gains_tax_reduce_the_annual_exempt_amount_from_12_300_to_6_000_f",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.cgt.annual_exempt_amount": {window(2024): 12_300.0}
                    },
                    "heads": [
                        {
                            "obr_heads": ["Capital gains tax"],
                            "pe_variables": ["capital_gains_tax"],
                            "channel": "tax",
                            "base_sheet": "CGT",
                            "pe_base_comparable": True,
                        },
                        INCOME_TAX,
                    ],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the £12,300 annual exempt amount (modern law: £3,000). "
                        "pe-uk labels this parameter under active development."
                    ),
                    "sources": [
                        "Finance Act 2023 s. 8 (https://www.legislation.gov.uk/ukpga/2023/1/section/8/enacted)",
                        "pe-uk 2.132.6 parameters gov/hmrc/cgt/annual_exempt_amount.yaml",
                    ],
                },
                {
                    "experiment_id": "as2022_benefit_cap_cpi_uprating",
                    "measure_key": f"{as22}__benefit_cap_levels_uprate_by_cpi_in_2023_24",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.dwp.benefit_cap.single.in_london": {
                            window(2024): 15_410.0
                        },
                        "gov.dwp.benefit_cap.single.outside_london": {
                            window(2024): 13_400.0
                        },
                        "gov.dwp.benefit_cap.non_single.in_london": {
                            window(2024): 23_000.0
                        },
                        "gov.dwp.benefit_cap.non_single.outside_london": {
                            window(2024): 20_000.0
                        },
                    },
                    "heads": [uc_group(["universal_credit", "housing_benefit"])],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the 2016 cap levels, which the April 2023 10.1% uprating "
                        "replaced and modern law still holds."
                    ),
                    "sources": [
                        "The Benefit Cap (Annual Limit) (Amendment) Regulations 2023 (https://www.legislation.gov.uk/uksi/2023/335/made)",
                        "pe-uk 2.132.6 parameters gov/dwp/benefit_cap.yaml",
                    ],
                },
                {
                    "experiment_id": "as2022_sdlt_nil_rate_bands_2024",
                    "measure_key": f"{as22}__stamp_duty_land_tax_increases_to_nil_rate_thresholds_from_23_september_2",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        path: {window(2024, 2024): value}
                        for path, value in SDLT_PRE_2022.items()
                    },
                    "heads": [stamp_duty_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "2024-25 without the Growth Plan relief: the 2% band from £125,000, "
                        "first-time buyers' relief to £300,000 on prices to £500,000. The "
                        "relief ended on 31 March 2025, so later years have nothing to move."
                    ),
                    "sources": SDLT_SOURCES,
                },
                {
                    "experiment_id": "as2022_sdlt_end_growth_plan_relief",
                    "measure_key": f"{as22}__stamp_duty_land_tax_ending_the_growth_plan_change_on_31_march_2025",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        path: {window(2025): value}
                        for path, value in SDLT_GROWTH_PLAN.items()
                    },
                    "heads": [stamp_duty_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "The pre-measure world kept the Growth Plan relief: nil rate to "
                        "£250,000 (the 2% band removed), first-time buyers' relief to "
                        "£425,000 on prices to £625,000, from 2025-26."
                    ),
                    "sources": SDLT_SOURCES,
                },
            ],
        },
    }
    return specs


def registry_ref(event: str) -> dict:
    relative = f"data/uk/events/{event}_measures.json"
    return {
        "path": relative,
        "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
    }


def build() -> dict[str, bytes]:
    from pipeline import uk_policy_experiment as experiments_module

    out = {}
    for event, body in experiments().items():
        registry = json.loads(
            (ROOT / f"data/uk/events/{event}_measures.json").read_bytes()
        )
        spec = {
            "schema_version": 1,
            "kind": experiments_module.SPEC_KIND,
            "label": experiments_module.LABEL,
            "label_text": experiments_module.label_text(registry["event_name"]),
            "event_slug": event,
            "registry": registry_ref(event),
            "obr_forecast_vintage": body["obr_forecast_vintage"],
            "built_by": "pipeline/uk_experiment_specs.py",
            "experiments": body["experiments"],
        }
        experiments_module.validate_spec(
            spec, registry, experiments_module.load_bases()
        )
        out[f"{event}.json"] = experiments_module.canonical_bytes(spec)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    stale = []
    for name, payload in build().items():
        path = SPEC_DIR / name
        if args.check:
            if not path.exists() or path.read_bytes() != payload:
                stale.append(name)
        else:
            path.write_bytes(payload)
            print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        print(f"stale experiment specs: {stale}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
