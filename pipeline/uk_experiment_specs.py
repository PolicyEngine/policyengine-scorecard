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


# Fuel duty: a one-year freeze forgoes that April's RPI uprating of 57.95p,
# the rate from 23 March 2011. The forgone uprating is the event forecast's
# RPI for the uprating year, from the OBR's Historical official forecasts
# database (Spring 2026), sheet RPI, percentage change on a year earlier.
# Later freezes keep the higher level, and the 5p cut from 23 March 2022 is
# a cash cut, so the counterfactual is 57.95p x (1 + RPI) - 5p. Modern law
# (pe-uk 2.132.6) holds 52.95p from 23 March 2022 to 1 January 2027; the
# parameter is day-weighted over each fiscal year (fiscal_year_blend), so a
# window must cover whole fiscal years and the experiments run 2024-25 and
# 2025-26 only, inside that constant stretch.
FUEL_DUTY_2011 = 0.5795
FUEL_DUTY_CUT_2022 = 0.05
RPI_FORGONE = {
    "budget_2016": ("b2016", 1.7109009953075116, "RPI!J18", "March 2016", 2016),
    "autumn_2016": ("as2016", 3.192173090436583, "RPI!K19", "November 2016", 2017),
    "autumn_budget_2017": (
        "ab2017",
        3.3035316860136055,
        "RPI!L21",
        "November 2017",
        2018,
    ),
    "budget_2018": ("b2018", 3.138083688269977, "RPI!M23", "October 2018", 2019),
    "budget_2020": ("b2020", 2.16390512465372, "RPI!N25", "March 2020", 2020),
    "spring_budget_2021": ("sb2021", 2.5133882664885476, "RPI!O27", "March 2021", 2021),
    "autumn_budget_2021": (
        "ab2021",
        4.966476437640965,
        "RPI!P28",
        "October 2021",
        2022,
    ),
}


CARRY_REASON = (
    "The event's costings end before the population's first year. The "
    "measure is a permanent change of level whose last costing year is "
    "steady state, so later years compare with that year, scaled to the "
    "run year's base."
)


def carried(experiment: dict, fy: str) -> dict:
    return {**experiment, "carried_from_fy": fy, "carry_reason": CARRY_REASON}


def fuel_duty_freeze(event: str, measure_key: str) -> dict:
    prefix, rpi, cell, vintage, year = RPI_FORGONE[event]
    rate = round(FUEL_DUTY_2011 * (1 + rpi / 100) - FUEL_DUTY_CUT_2022, 6)
    return {
        "experiment_id": f"{prefix}_fuel_duty_freeze_{year}",
        "measure_key": measure_key,
        "construction": "reversal_on_modern_law",
        "reform": {
            "gov.hmrc.fuel_duty.petrol_and_diesel": {"2024-01-01.2026-12-31": rate}
        },
        "years": [2024, 2025],
        "heads": [
            {
                "obr_heads": ["Fuel duty"],
                "pe_variables": ["fuel_duty"],
                "channel": "tax",
                "base_sheet": "Fuel",
                "pe_base_comparable": False,
            }
        ],
        "magnitude_check": "scaled",
        "note": (
            f"Without the freeze the April {year} uprating would have applied: the "
            f"{vintage} forecast's RPI for {year}, {rpi:.3f}% ({cell}), on 57.95p. "
            f"Later freezes keep the higher level and the 2022 5p cut is in cash, so "
            f"modern law's 52.95p becomes {rate * 100:.3f}p in 2024-25 and 2025-26. "
            "pe-uk's fuel_duty covers "
            "household car fuel only, so business and haulage fuel in the OBR's "
            "base are outside it."
        ),
        "sources": [
            "OBR Historical official forecasts database, Spring 2026, sheet RPI",
            "pe-uk 2.132.6 parameters gov/hmrc/fuel_duty/petrol_and_diesel.yaml",
        ],
    }


# Spring Budget 2021's freeze of the personal allowance and basic rate limit
# to 2025-26. Without it each would be indexed by the previous September's
# CPI (ONS: 3.1% 2021, 10.1% 2022, 6.7% 2023, 1.7% 2024), the allowance
# rounded up to £10 and the basic rate limit to £100 (ITA 2007 s. 57 and
# s. 21). NICs' upper earnings and profits limits follow the higher rate
# threshold (allowance plus limit), the weekly limit at 1/52 of it.
def indexed(
    start: float, step: int, rates=(0.031, 0.101, 0.067, 0.017), first: int = 2022
) -> dict[int, float]:
    """Index from ``first`` onward by each rate, rounding up to ``step``."""
    out, value = {}, start
    for year, rate in zip(range(first, first + len(rates)), rates):
        value = -(-value * (1 + rate) // step) * step
        out[year] = float(value)
    return out


PA_CF = indexed(12_570, 10)
BRL_CF = indexed(37_700, 100)
HRT_CF = {year: PA_CF[year] + BRL_CF[year] for year in PA_CF}

# Budget 2018 brought the £12,500 allowance and £50,000 higher rate threshold
# forward a year. The pre-measure path indexes the 2018-19 £11,850 and
# £34,500 by the previous September's CPI (ONS: 2.4% 2018, 1.7% 2019, 0.5%
# 2020; same rounding), to £12,420 and £36,300 in 2021-22, which the later
# freezes then hold: the counterfactual sits £150 and £1,400 below modern
# law in every later year.
PA_B2018 = indexed(11_850, 10, rates=(0.024, 0.017, 0.005), first=2019)
BRL_B2018 = indexed(34_500, 100, rates=(0.024, 0.017, 0.005), first=2019)
B2018_PA = PA_B2018[2021]  # the 2021-22 level, which the freezes hold
B2018_BRL = BRL_B2018[2021]


# Budget 2018's £1,000 a year work-allowance increase: £198 and £409 a month
# would have stayed in April 2019 instead of £287 and £503. Each modern
# allowance keeps the later upratings and Autumn Budget 2021's £500, so the
# counterfactual removes the 2019 difference carried forward: x (293/287)
# to April 2021, then the allowance's own growth from its November 2021
# level (335 with housing; 515/503 and 557 without).
def b2018_work_allowance(
    modern: dict[int, int], diff: float, april_2021: tuple, november_2021: float
) -> dict[int, float]:
    before, after = april_2021
    return {
        year: float(round(value - diff * (after / before) * (value / november_2021)))
        for year, value in modern.items()
        if year in (2024, 2025)
    }


# Budget 2010 (June): child benefit frozen for 2011-12 to 2013-14 instead of
# rising with the previous September's CPI (ONS: 3.1% 2010, 5.2% 2011, 2.2%
# 2012). Every later rate scales by the forgone factor.
CB_FREEZE = 1.031 * 1.052 * 1.022

# Spending Review 2020: the standard minimum guarantee rose from £173.75 to
# £177.10 (single) and £265.20 to £270.30 (couple) in April 2021, where the
# statutory minimum, earnings growth, was negative and so a freeze (Social
# Security Administration Act 1992 s. 150A). Later amounts scale by the
# frozen-over-uprated ratio.
SMG_FREEZE = {"SINGLE": 173.75 / 177.10, "COUPLE": 265.20 / 270.30}


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
    specs[ab21]["experiments"].append(
        fuel_duty_freeze(ab21, f"{ab21}__fuel_duty_one_year_freeze_in_2022_23")
    )
    sb21 = "spring_budget_2021"
    sr20 = "spending_review_2020"
    b20 = "budget_2020"
    specs[sb21] = {
        "obr_forecast_vintage": "March 2021",
        "experiments": [
            {
                "experiment_id": "sb2021_personal_allowance_hrt_freeze",
                "measure_key": f"{sb21}__income_tax_maintain_personal_allowance_and_higher_rate_threshold_at_2021",
                "construction": "reversal_on_modern_law",
                "reform": {
                    "gov.hmrc.income_tax.allowances.personal_allowance.amount": yearly(
                        {y: PA_CF[y] for y in (2024, 2025)}
                    ),
                    "gov.hmrc.income_tax.rates.uk[1].threshold": yearly(
                        {y: BRL_CF[y] for y in (2024, 2025)}
                    ),
                    "gov.hmrc.income_tax.rates.dividends[1].threshold": yearly(
                        {y: BRL_CF[y] for y in (2024, 2025)}
                    ),
                    "gov.hmrc.national_insurance.class_1.thresholds.upper_earnings_limit": yearly(
                        {y: money(HRT_CF[y] / 52) for y in (2024, 2025)}
                    ),
                    "gov.hmrc.national_insurance.class_4.thresholds.upper_profits_limit": yearly(
                        {y: HRT_CF[y] for y in (2024, 2025)}
                    ),
                },
                "heads": [
                    INCOME_TAX,
                    nics_group(["NICs"]),
                    {
                        "obr_heads": ["Capital gains tax"],
                        "pe_variables": ["capital_gains_tax"],
                        "channel": "tax",
                        "base_sheet": "CGT",
                        "pe_base_comparable": True,
                    },
                    uc_group(),
                ],
                "magnitude_check": "sign_only",
                "magnitude_reason": (
                    "A threshold freeze's yield depends on inflation since the "
                    "event: the counterfactual indexes by outturn CPI (10.1% in "
                    "September 2022), far above the March 2021 forecast the OBR "
                    "costed against (PLAN.md names this case)."
                ),
                "note": (
                    f"Indexed counterfactual: personal allowance £{PA_CF[2024]:,.0f} "
                    f"(2024-25) and £{PA_CF[2025]:,.0f} (2025-26), basic rate limit "
                    f"£{BRL_CF[2024]:,.0f} and £{BRL_CF[2025]:,.0f}, so the higher rate "
                    f"threshold and NICs upper limits £{HRT_CF[2024]:,.0f} and "
                    f"£{HRT_CF[2025]:,.0f}. Modern law: £12,570, £37,700, £50,270. The "
                    "dividend higher-rate band moves with the basic rate limit; the "
                    "primary threshold keeps Spring Statement 2022's £12,570 and Scottish "
                    "bands are devolved."
                ),
                "sources": [
                    "Finance Act 2021 s. 5 (https://www.legislation.gov.uk/ukpga/2021/26/section/5)",
                    "Income Tax Act 2007 s. 21 and s. 57 (indexation and rounding)",
                    "ONS CPI annual rate, September 2021-2024: 3.1%, 10.1%, 6.7%, 1.7%",
                ],
            },
            fuel_duty_freeze(sb21, f"{sb21}__fuel_duty_one_year_freeze_in_2021_22"),
        ],
    }
    specs[sr20] = {
        "obr_forecast_vintage": "November 2020",
        "experiments": [
            {
                "experiment_id": "sr2020_pension_credit_smg_uprating",
                "measure_key": f"{sr20}__pension_credit_uprating_of_the_standard_minimum_guarantee",
                "construction": "reversal_on_modern_law",
                "reform": {
                    f"gov.dwp.pension_credit.guarantee_credit.minimum_guarantee.{kind}": yearly(
                        {
                            y: money(v * SMG_FREEZE[kind])
                            for y, v in (
                                SMG_SINGLE if kind == "SINGLE" else SMG_COUPLE
                            ).items()
                            if y in (2024, 2025)
                        }
                    )
                    for kind in ("SINGLE", "COUPLE")
                },
                "heads": [uc_group(["pension_credit"])],
                "magnitude_check": "scaled",
                "note": (
                    "Without the April 2021 uprating the guarantee stays at its "
                    "statutory minimum, a freeze (negative earnings growth); modern "
                    "single and couple amounts for 2024-25 and 2025-26 scale by "
                    "173.75/177.10 and 265.20/270.30."
                ),
                "sources": [
                    "The Social Security Benefits Up-rating Order 2021 (https://www.legislation.gov.uk/uksi/2021/162/made)",
                    "Social Security Administration Act 1992 s. 150A",
                    "pe-uk 2.132.6 parameters gov/dwp/pension_credit/guarantee_credit/minimum_guarantee.yaml",
                ],
            }
        ],
    }
    b18, ab17, b17 = "budget_2018", "autumn_budget_2017", "budget_2017"
    specs[b18] = {
        "obr_forecast_vintage": "October 2018",
        "experiments": [
            carried(
                {
                    "experiment_id": "b2018_personal_allowance_12500_hrt_50000",
                    "measure_key": f"{b18}__personal_allowance_and_higher_rate_threshold_increase_to_12_500_and_50_0",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.allowances.personal_allowance.amount": {
                            window(2024, 2025): B2018_PA
                        },
                        "gov.hmrc.income_tax.rates.uk[1].threshold": {
                            window(2024, 2025): B2018_BRL
                        },
                        "gov.hmrc.income_tax.rates.dividends[1].threshold": {
                            window(2024, 2025): B2018_BRL
                        },
                        "gov.hmrc.national_insurance.class_1.thresholds.upper_earnings_limit": {
                            window(2024, 2025): money((B2018_PA + B2018_BRL) / 52)
                        },
                        "gov.hmrc.national_insurance.class_4.thresholds.upper_profits_limit": {
                            window(2024, 2025): B2018_PA + B2018_BRL
                        },
                    },
                    "years": [2024, 2025],
                    "heads": [INCOME_TAX, nics_group(["NICs"]), uc_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        f"Pre-measure path: personal allowance £{B2018_PA:,.0f}, basic rate "
                        f"limit £{B2018_BRL:,.0f}, so the higher rate threshold and NICs "
                        f"upper limits £{B2018_PA + B2018_BRL:,.0f} (modern law £12,570, "
                        "£37,700, £50,270). The dividend higher-rate band moves with the "
                        "basic rate limit; the primary threshold keeps Spring Statement "
                        "2022's £12,570; Scottish bands are devolved."
                    ),
                    "sources": [
                        "Finance Act 2019 s. 5 (https://www.legislation.gov.uk/ukpga/2019/1/section/5)",
                        "ONS CPI annual rate, September 2018-2020: 2.4%, 1.7%, 0.5%",
                    ],
                },
                "2023-24",
            ),
            carried(
                {
                    "experiment_id": "b2018_uc_work_allowance_1000",
                    "measure_key": f"{b18}__universal_credit_1_000_increase_to_work_allowance",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.dwp.universal_credit.means_test.work_allowance.with_housing": yearly(
                            b2018_work_allowance(WA_WITH, 287 - 198, (287, 293), 335)
                        ),
                        "gov.dwp.universal_credit.means_test.work_allowance.without_housing": yearly(
                            b2018_work_allowance(WA_WITHOUT, 503 - 409, (503, 515), 557)
                        ),
                    },
                    "years": [2024, 2025],
                    "heads": [uc_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "Removes the April 2019 increase (£287 and £503 a month instead "
                        "of £198 and £409), carried forward through later upratings."
                    ),
                    "sources": [
                        "The Universal Credit (Work Allowance) Amendment Regulations 2018",
                        "pe-uk 2.132.6 parameters gov/dwp/universal_credit/means_test/work_allowance.yaml",
                    ],
                },
                "2023-24",
            ),
            carried(
                fuel_duty_freeze(b18, f"{b18}__fuel_duty_freeze_for_2019_20"), "2023-24"
            ),
        ],
    }
    specs[ab17] = {
        "obr_forecast_vintage": "November 2017",
        "experiments": [
            carried(
                {
                    "experiment_id": "ab2017_sdlt_first_time_buyers_relief",
                    "measure_key": f"{ab17}__stamp_duty_land_tax_abolish_for_first_time_buyers_up_to_300_000",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.stamp_duty.residential.purchase.main.first.max": {
                            window(2024, 2025): 0.0
                        }
                    },
                    "years": [2024, 2025],
                    "heads": [stamp_duty_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "Removes first-time buyers' relief: a zero price limit sends every "
                        "purchase to the main scale. First-time-buyer status is an imputed "
                        "input; pe-uk 2.132.6 also lacks the 2022-25 Growth Plan limits."
                    ),
                    "sources": [
                        "Finance Act 2018 s. 41 (https://www.legislation.gov.uk/ukpga/2018/3/section/41)",
                        "pe-uk 2.132.6 parameters gov/hmrc/stamp_duty/residential/purchase/main/first/max.yaml",
                    ],
                },
                "2022-23",
            ),
            carried(
                fuel_duty_freeze(ab17, f"{ab17}__fuel_duty_freeze_for_2018_19"),
                "2022-23",
            ),
        ],
    }
    specs[b17] = {
        "obr_forecast_vintage": "March 2017",
        "experiments": [
            carried(
                {
                    "experiment_id": "b2017_class_4_main_rate_plus_2pp",
                    "measure_key": f"{b17}__class_4_nics_increase_to_10_from_april_2018_and_11_from_april_2019",
                    "construction": "forward_on_modern_law",
                    "reform": {
                        "gov.hmrc.national_insurance.class_4.rates.main": {
                            window(2024, 2025): 0.08
                        }
                    },
                    "years": [2024, 2025],
                    "heads": [nics_group(["NICs"]), INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": (
                        "The increase was withdrawn a week after the Budget, so modern law "
                        "lacks it; the experiment adds its 2pp to the modern 6% main rate. "
                        "The OBR's costing is net of incorporation responses, which a static "
                        "run does not have."
                    ),
                    "sources": [
                        "Spring Budget 2017 para 3.18 (https://www.gov.uk/government/publications/spring-budget-2017-documents)",
                        "pe-uk 2.132.6 parameters gov/hmrc/national_insurance/class_4/rates/main.yaml",
                    ],
                },
                "2021-22",
            )
        ],
    }
    b16, as16, as15, sb15 = "budget_2016", "autumn_2016", "autumn_2015", "budget_2015_2"
    specs[as16] = {
        "obr_forecast_vintage": "November 2016",
        "experiments": [
            carried(
                fuel_duty_freeze(as16, f"{as16}__fuel_duty_freeze_in_2017_18"),
                "2021-22",
            )
        ],
    }
    specs[b16] = {
        "obr_forecast_vintage": "March 2016",
        "experiments": [
            carried(
                {
                    "experiment_id": "b2016_trading_and_property_allowances",
                    "measure_key": f"{b16}__sharing_economy_1_000_allowance_for_both_trading_and_property_income",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.allowances.trading_allowance": {
                            window(2024, 2025): 0.0
                        },
                        "gov.hmrc.income_tax.allowances.property_allowance": {
                            window(2024, 2025): 0.0
                        },
                    },
                    "years": [2024, 2025],
                    "heads": [INCOME_TAX, nics_group(["NICs"])],
                    "magnitude_check": "scaled",
                    "note": (
                        "Removes the £1,000 trading and property allowances (modern law "
                        "keeps both). Class 4 profits are taken after the trading allowance, "
                        "so NICs move too."
                    ),
                    "sources": [
                        "Finance (No. 2) Act 2017 Sch. 3 (https://www.legislation.gov.uk/ukpga/2017/32/schedule/3)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/allowances/{trading,property}_allowance.yaml",
                    ],
                },
                "2020-21",
            ),
            carried(
                fuel_duty_freeze(b16, f"{b16}__fuel_duty_freeze_in_april_2016"),
                "2020-21",
            ),
        ],
    }
    specs[as15] = {
        "obr_forecast_vintage": "November 2015",
        "experiments": [
            carried(
                {
                    "experiment_id": "as2015_sdlt_additional_dwellings_surcharge",
                    "measure_key": f"{as15}__stamp_duty_land_tax_higher_rates_on_additional_properties",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        f"gov.hmrc.stamp_duty.residential.purchase.additional.rate[{i}].rate": {
                            window(2025): rate
                        }
                        for i, rate in enumerate((0.02, 0.04, 0.07, 0.12, 0.14))
                    },
                    "years": [2025, 2026],
                    "heads": [stamp_duty_group()],
                    "magnitude_check": "scaled",
                    "note": (
                        "Takes the original 3pp surcharge off the additional-dwellings "
                        "scale, keeping Autumn Budget 2024's further 2pp: from 2025-26 the "
                        "scale becomes the main scale plus 2pp (2%, 4%, 7%, 12%, 14%) "
                        "instead of plus 5pp. 2024-25 is left out because its main scale "
                        "carries the Growth Plan relief for part of the year."
                    ),
                    "sources": [
                        "Finance Act 2016 s. 128 and Sch. 4A FA 2003",
                        "Autumn Budget 2024 Table 5.1 (the 2pp increase from 31 October 2024)",
                        "pe-uk parameters gov/hmrc/stamp_duty/residential/purchase/additional/rate.yaml",
                    ],
                },
                "2020-21",
            )
        ],
    }
    specs[sb15] = {
        "obr_forecast_vintage": "July 2015",
        "experiments": [
            carried(
                {
                    "experiment_id": "sb2015_two_child_limit",
                    "measure_key": f"{sb15}__limit_child_element_of_tax_credits_and_uc_to_2_children_for_new_claims",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.dwp.universal_credit.elements.child.limit.child_count": {
                            window(2024, 2025): 100.0
                        },
                        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": {
                            window(2024, 2025): 100.0
                        },
                    },
                    "years": [2024, 2025],
                    "heads": [
                        {
                            "obr_heads": ["Tax credits", "Welfare inside cap"],
                            "pe_variables": ["universal_credit", "child_tax_credit"],
                            "channel": "spending",
                            "base_sheet": "Welfare in",
                            "pe_base_comparable": False,
                        }
                    ],
                    "magnitude_check": "sign_only",
                    "magnitude_reason": (
                        "The limit applies to children born from 6 April 2017, so its yield "
                        "grows each year until every child is covered; the 2020-21 costing "
                        "is not steady state."
                    ),
                    "note": (
                        "Removes the two-child limit in 2024-25 and 2025-26 (a child count "
                        "of 100 stands for none). Modern law abolishes it from April 2026 "
                        "(Autumn Budget 2025), so later years have nothing to move."
                    ),
                    "sources": [
                        "Welfare Reform and Work Act 2016 s. 13-14",
                        "pe-uk parameters gov/dwp/universal_credit/elements/child/limit/child_count.yaml",
                    ],
                },
                "2020-21",
            )
        ],
    }
    b10, a10, b12, a13, b15 = (
        "budget_2010_2",
        "autumn_2010",
        "budget_2012",
        "autumn_2013",
        "budget_2015",
    )

    def welfare(variables, heads=("Social security benefits",)) -> dict:
        return {
            "obr_heads": list(heads),
            "pe_variables": list(variables),
            "channel": "spending",
            "base_sheet": "Total welfare",
            "pe_base_comparable": False,
        }

    hicbc_leg = {
        "obr_heads": [],
        "pe_variables": ["income_tax"],
        "channel": "tax",
        "pe_base_comparable": False,
        "note": (
            "The charge is income tax in PolicyEngine; the OBR books the measure "
            "as reduced benefit spending."
        ),
    }
    specs[b10] = {
        "obr_forecast_vintage": "June 2010",
        "experiments": [
            carried(
                {
                    "experiment_id": "b2010_vat_standard_rate_20",
                    "measure_key": f"{b10}__vat_increase_main_rate_to_20_from_4_january_2011",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.vat.standard_rate": {window(2024, 2025): 0.175}
                    },
                    "years": [2024, 2025],
                    "heads": [
                        {
                            "obr_heads": ["VAT"],
                            "pe_variables": ["vat"],
                            "channel": "tax",
                            "base_sheet": "VAT",
                            "pe_base_comparable": False,
                        }
                    ],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the 17.5% standard rate. pe-uk's VAT is household "
                        "consumption grossed up by its coverage factor; the OBR's base "
                        "also includes VAT that businesses and government cannot recover."
                    ),
                    "sources": [
                        "Finance (No. 2) Act 2010 s. 3",
                        "pe-uk 2.132.6 parameters gov/hmrc/vat/standard_rate.yaml",
                    ],
                },
                "2014-15",
            ),
            carried(
                {
                    "experiment_id": "b2010_child_benefit_three_year_freeze",
                    "measure_key": f"{b10}__child_benefit_freeze_for_3_years_from_2011_12",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        f"gov.hmrc.child_benefit.amount.{kind}": yearly(
                            {
                                y: round(round(v * CB_FREEZE / 0.05) * 0.05, 2)
                                for y, v in amounts.items()
                            }
                        )
                        for kind, amounts in (
                            ("eldest", {2024: 25.60, 2025: 26.05}),
                            ("additional", {2024: 16.95, 2025: 17.25}),
                        )
                    },
                    "years": [2024, 2025],
                    "heads": [welfare(["child_benefit"]), hicbc_leg],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the CPI upratings the freeze forwent in April 2011, "
                        "2012 and 2013 (September CPI 3.1%, 5.2%, 2.2%, ONS): every modern "
                        f"rate scaled by {CB_FREEZE:.6f}, rounded to 5p. The higher "
                        "benefit raises the high-income charge, an income-tax leg."
                    ),
                    "sources": [
                        "Budget 2010 (June) Table 2.1",
                        "ONS CPI annual rate, September 2010-2012: 3.1%, 5.2%, 2.2%",
                        "pe-uk 2.132.6 parameters gov/hmrc/child_benefit/amount/*.yaml",
                    ],
                },
                "2014-15",
            ),
        ],
    }
    specs[a10] = {
        "obr_forecast_vintage": "November 2010",
        "experiments": [
            carried(
                {
                    "experiment_id": "as2010_high_income_child_benefit_charge",
                    "measure_key": f"{a10}__child_benefit_remove_from_families_with_a_higher_rate_taxpayer_from_janu",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {
                            window(2024, 2025): 1e9
                        },
                        "gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {
                            window(2024, 2025): 1e9 + 1e4
                        },
                    },
                    "years": [2024, 2025],
                    "heads": [welfare(["child_benefit"]), hicbc_leg],
                    "magnitude_check": "scaled",
                    "note": (
                        "Removes the charge (a phase-out from £1bn stands for none), "
                        "whatever later events made of its design. Families who opted out "
                        "of child benefit resume it once their charge share falls below "
                        "pe-uk's opt-out threshold."
                    ),
                    "sources": [
                        "Finance Act 2012 Sch. 1 (Income Tax (Earnings and Pensions) Act 2003 s. 681B-681H)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/charges/CB_HITC/*.yaml",
                    ],
                },
                "2015-16",
            )
        ],
    }
    specs[b12] = {
        "obr_forecast_vintage": "March 2012",
        "experiments": [
            carried(
                {
                    "experiment_id": "b2012_additional_rate_45p",
                    "measure_key": f"{b12}__income_tax_reduce_additional_rate_to_45p_in_2013_14",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.rates.uk[2].rate": {
                            window(2024, 2025): 0.5
                        },
                        "gov.hmrc.income_tax.rates.savings.additional": {
                            window(2024, 2025): 0.5
                        },
                        "gov.hmrc.income_tax.rates.property.additional": {
                            window(2024, 2025): 0.5
                        },
                    },
                    "years": [2024, 2025],
                    "heads": [INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": (
                        "Restores the 50% additional rate on non-savings, savings and "
                        "property income. The dividend additional rate's 2013 cut (42.5% "
                        "to 37.5%) is left out: the 2016 dividend reform rebuilt that "
                        "schedule. The OBR's costing is dominated by the taxable-income "
                        "response, which a static run does not have."
                    ),
                    "sources": [
                        "Finance Act 2012 s. 1",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/rates/{uk,savings,property}.yaml",
                    ],
                },
                "2016-17",
            )
        ],
    }
    specs[a13] = {
        "obr_forecast_vintage": "December 2013",
        "experiments": [
            carried(
                {
                    "experiment_id": "as2013_marriage_allowance",
                    "measure_key": f"{a13}__income_tax_transferable_marriage_allowance",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.allowances.marriage_allowance.max": {
                            window(2024, 2025): 0.0
                        }
                    },
                    "years": [2024, 2025],
                    "heads": [
                        INCOME_TAX,
                        welfare(["universal_credit", "housing_benefit"]),
                    ],
                    "magnitude_check": "scaled",
                    "note": (
                        "Removes the transferable allowance (modern law: 10% of the "
                        "personal allowance)."
                    ),
                    "sources": [
                        "Finance Act 2014 s. 11 (Income Tax Act 2007 s. 55A-55E)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/allowances/marriage_allowance/max.yaml",
                    ],
                },
                "2018-19",
            )
        ],
    }
    specs[b15] = {
        "obr_forecast_vintage": "March 2015",
        "experiments": [
            carried(
                {
                    "experiment_id": "b2015_personal_savings_allowance",
                    "measure_key": f"{b15}__savings_tax_allowance_and_isa_flexibility",
                    "construction": "reversal_on_modern_law",
                    "reform": {
                        "gov.hmrc.income_tax.allowances.personal_savings_allowance.basic": {
                            window(2024, 2025): 0.0
                        },
                        "gov.hmrc.income_tax.allowances.personal_savings_allowance.higher": {
                            window(2024, 2025): 0.0
                        },
                    },
                    "years": [2024, 2025],
                    "heads": [INCOME_TAX],
                    "magnitude_check": "scaled",
                    "note": (
                        "Removes the personal savings allowance (£1,000 basic rate, £500 "
                        "higher rate); the measure's ISA flexibility leg has no "
                        "counterpart."
                    ),
                    "sources": [
                        "Finance (No. 2) Act 2015 s. 4 (Income Tax Act 2007 s. 12B)",
                        "pe-uk 2.132.6 parameters gov/hmrc/income_tax/allowances/personal_savings_allowance/*.yaml",
                    ],
                },
                "2019-20",
            )
        ],
    }
    specs[b20] = {
        "obr_forecast_vintage": "March 2020",
        "experiments": [fuel_duty_freeze(b20, f"{b20}__fuel_duty_freeze_for_2020_21")],
    }
    return specs


def registry_ref(event: str) -> dict:
    """The event's registry, or the inventory for an event without one."""
    relative = f"data/uk/events/{event}_measures.json"
    if not (ROOT / relative).exists():
        relative = "data/uk/events/inventory.jsonl"
        return {
            "kind": "inventory",
            "path": relative,
            "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
        }
    return {
        "path": relative,
        "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
    }


def build() -> dict[str, bytes]:
    from pipeline import uk_policy_experiment as experiments_module

    out = {}
    for event, body in experiments().items():
        reference = registry_ref(event)
        registry, _ = experiments_module.load_registry(
            {"registry": reference, "event_slug": event}
        )
        spec = {
            "schema_version": 1,
            "kind": experiments_module.SPEC_KIND,
            "label": experiments_module.LABEL,
            "label_text": experiments_module.label_text(registry["event_name"]),
            "event_slug": event,
            "registry": reference,
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
