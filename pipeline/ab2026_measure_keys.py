"""Autumn Budget 2026 measure keys, one per HM Treasury Table 6.1 line.

The key space every AB2026 claim carries in conditions.measure_key (#230).
Keys are written out here rather than derived from titles, so a reworded
title in a later edition of the table cannot move a key. Both the Table 6.1
stager (pipeline/stage_ab2026_hmt_tables.py) and the registry builder
(pipeline/build_ab2026_registry.py) import this module, so a staged row and
its registry entry cannot disagree about a key.
"""

PREFIX = "ab2026__"

# Table 6.1 "Budget 2026 policy decisions (£ million)", lines 1-98.
TABLE_61 = {
    1: "household_energy_payment_100_bands_a_to_d",
    2: "electricity_vat_zero_rate_to_july_2027",
    3: "fuel_duty_5p_cut_extended_and_rpi_rise_deferred",
    4: "bus_fare_cap_2_england_outside_london_2027",
    5: "mileage_allowance_payments_55p",
    6: "parental_allowance_fathers_partners_adopters",
    7: "carers_allowance_earnings_taper",
    8: "uc_surplus_earnings_threshold_2500_extended",
    9: "early_years_books_access",
    10: "food_and_heating_oil_tariff_suspensions",
    11: "cash_isa_limit_held_at_20000",
    12: "business_rates_pubs_relief_35pc",
    13: "business_rates_sbrr_rhl_thresholds_raised",
    14: "business_rates_rhl_transitional_support",
    15: "trading_allowance_3000",
    16: "business_tariff_suspensions",
    17: "climate_change_levy_rates_2028",
    18: "red_diesel_duty_cut",
    19: "alcohol_duty_small_producer_relief",
    20: "good_growth_funds",
    21: "business_rates_retention_mayoral_authorities",
    22: "local_apprenticeship_services",
    23: "regional_growth_investments",
    24: "cambridge_development_corporation",
    25: "strategic_authorities_capacity_funding",
    26: "founders_relief_cgt",
    27: "rd_relief_claim_notification_form_removed",
    28: "emi2_option_limit_120000",
    29: "british_business_bank_backing_innovation",
    30: "national_wealth_fund_capital",
    31: "artificial_intelligence_package",
    32: "ev_charging_public_chargers",
    33: "rough_sleeping_investment",
    34: "rough_sleeping_reprioritised_mhclg_budgets",
    35: "social_and_affordable_homes_programme",
    36: "vat_zero_rate_land_for_social_housing",
    37: "your_first_home_equity_loan",
    38: "first_time_buyer_isa",
    39: "lifetime_isa_withdrawal_charge_20pc_above_cap",
    40: "defence_investment_plan_further_savings",
    41: "defence_investment_plan_capital_reallocation",
    42: "defence_admin_savings_reinvested",
    43: "ukraine_winter_air_defence",
    44: "uk_export_finance_defence_capacity",
    45: "hmrc_tax_gap_package",
    46: "online_marketplace_liability_uk_businesses",
    47: "dwp_fraud_and_error_prevention",
    48: "benefits_removed_hospitalised_serious_offenders",
    49: "distributions_framework_modernised",
    50: "advance_corporation_tax_abolished",
    51: "vat_reverse_charge_overseas_services_restricted",
    52: "pension_tax_allowance",
    53: "pension_death_benefits_two_year_rule_removed",
    54: "foreign_sovereign_investments_taxation",
    55: "bank_surcharge_6pc_temporary",
    56: "machine_games_duty_higher_stake_25pc",
    57: "business_rates_vape_shops_and_agcs_reliefs_removed",
    58: "writing_down_allowance_12pc_and_fya_50pc",
    59: "private_hire_operators_vat_full_fare",
    60: "badr_lifetime_limit_500000",
    61: "property_income_rates_plus_2pp",
    62: "savings_income_rates_plus_2pp",
    63: "civil_service_admin_budgets_cut_20pc",
    64: "civil_service_ai_fund",
    65: "hgv_ved_1_for_12_months",
    66: "vat_5pc_family_days_out_summer_2026",
    67: "free_bus_travel_children_august_2026",
    68: "foreign_permanent_establishment_exemption_mandatory",
    69: "electricity_generator_levy_55pc",
    70: "british_industrial_competitiveness_scheme",
    71: "carbon_price_support_removed",
    72: "youth_guarantee_and_apprenticeships_spring_2026",
    73: "union_learning_fund",
    74: "investment_for_growth",
    75: "growth_guarantee_scheme_expansion",
    76: "leeds_city_fund",
    77: "uk_india_ceta_and_double_contributions_convention",
    78: "steel_tariff_and_quotas",
    79: "securities_transfer_tax",
    80: "business_rates_ev_charging_relief",
    81: "misogyny_prevention_programmes",
    82: "infected_blood_compensation_additional_report",
    83: "student_loan_interest_cap_6pc_plan_2_and_3",
    84: "waste_crime_landfill_tax_clearances",
    85: "further_priorities_nhs_and_vawg",
    86: "company_car_tax_rates_2030_31",
    87: "supported_housing_licensing",
    88: "vat_zero_rate_donated_medicines",
    89: "vat_medical_deputies_staffing",
    90: "landfill_communities_fund_credit_cap",
    91: "franchised_higher_education_registration",
    92: "high_needs_local_authority_spending",
    93: "hvcts_deferrals_discounts_exemptions",
    94: "benefits_in_kind_payrolling_delay",
    95: "low_value_imports_customs_relief_removed",
    96: "ets_energy_from_waste_delay",
    97: "gas_distribution_revenue_recognition_spread",
    98: "us_llc_double_taxation_relief",
}

# Table 6.2 "Budget 2026 Financial Transactions (cash impact, £ million)".
# Each line is the financial-transactions leg of a Table 6.1 measure, except
# line 4 (Sovereign AI), which has no Table 6.1 line and so its own key.
TABLE_62 = {
    1: TABLE_61[20],
    2: TABLE_61[30],
    3: TABLE_61[29],
    4: "sovereign_ai_financial_transactions",
    5: TABLE_61[37],
    6: TABLE_61[37],
    7: TABLE_61[74],
    8: TABLE_61[24],
    9: TABLE_61[47],
}

# Table 6.4 "Measures announced at Spring Statement 2026 or earlier that will
# take effect from 29 October 2026 or later": recostings of earlier events'
# measures, keyed to those events' registries (full keys, not slugs).
TABLE_64 = {
    1: ("autumn_budget_2025", "ab2025__cbam_indirect_emissions_removed"),
    2: ("autumn_budget_2025", "ab2025__student_finance_lle_launch_and_loan_outlay"),
    3: ("autumn_budget_2025", "ab2025__ppf_and_fas_pre_1997_inflation_protection"),
    4: (
        "autumn_budget_2025",
        "ab2025__fya_zero_emission_cars_and_charge_points_extended",
    ),
    5: ("autumn_budget_2025", "ab2025__student_loans_plan2_threshold_freeze"),
    6: ("autumn_budget_2025", "ab2025__property_income_separate_rates"),
    7: ("autumn_budget_2025", "ab2025__apd_higher_rate_extended_to_private_jets"),
    8: ("autumn_budget_2025", "ab2025__db_pension_scheme_surplus_extraction"),
    9: ("autumn_budget_2025", "ab2025__ets_expansion_to_international_maritime"),
    10: ("autumn_budget_2025", "ab2025__sdil_threshold_cut_and_milk_based_drinks"),
    11: ("autumn_budget_2025", "ab2025__high_value_council_tax_surcharge"),
    12: ("autumn_budget_2025", "ab2025__eved_mileage_supplement_electric_and_phev"),
    13: ("autumn_budget_2025", "ab2025__low_value_imports_customs_reform"),
    14: ("autumn_budget_2025", "ab2025__salary_sacrifice_pension_nics_cap_2000"),
    15: (
        "autumn_budget_2024",
        "autumn_budget_2024__company_car_tax_set_appropriate_percentages_for_electric_vehicles_hybrids_and_internal_combustion_engine_vehic_f0345c3d",
    ),
    16: (
        "autumn_budget_2024",
        "autumn_budget_2024__inheritance_tax_include_unused_pension_funds_and_death_benefits_payable_from_a_pension_in_the_value_of_estates_215d16bf",
    ),
    17: (
        "spring_budget_2024",
        "spring_budget_2024__carbon_border_adjustment_mechanism_cbam_introduce_from_1_january_2027_46125f17",
    ),
}

# Packages: compositions of Table 6.1 lines that HM Treasury totals or that
# outside producers score as one thing. A producer's package row joins here
# when its scope is exactly these lines; any other scope is a proposal.
PACKAGES = {
    "package_total_policy_decisions": {
        "title": "Table 6.1 total policy decisions",
        "lines": sorted(TABLE_61),
        "table_61_row": "Total policy decisions",
    },
    "package_total_tax_policy_decisions": {
        "title": "Table 6.1 total tax policy decisions",
        "lines": None,  # the table's own Tax/Spend head split
        "table_61_row": "Total tax policy decisions",
    },
    "package_total_spending_policy_decisions": {
        "title": "Table 6.1 total spending policy decisions",
        "lines": None,
        "table_61_row": "Total spending policy decisions",
    },
    "package_household_energy_vat_and_fuel_duty": {
        "title": "The Household Energy Payment, zero VAT on domestic electricity and the fuel duty cut, together",
        "lines": [1, 2, 3],
        "table_61_row": None,
    },
    "package_policyengine_seven": {
        "title": "The seven household measures PolicyEngine modelled on Budget day, together",
        "lines": [1, 2, 3, 7, 15, 52, 61],
        "table_61_row": None,
    },
}


def key(line):
    """The full measure key of a Table 6.1 line."""
    return PREFIX + TABLE_61[line]


def package_key(slug):
    return PREFIX + slug
