# Recent OBR fiscal-event replays

The inventories use the pinned uk-data-1.58.0__pe-uk-2.125.1 bundle definition with policyengine-uk 2.125.1. A seeded registry does not establish a completed numerical replay. Available comparisons use one source head and fiscal year per row.

Numerical comparison outputs available: 5. Registry inventories available: 5.

| Event | Replay state | Measures | Source rows | Computed rows | Computed FYs |
|---|---|---:|---:|---:|---|
| [autumn_budget_2024](autumn_budget_2024/COMPARISON.md) | Registered construction replay complete | 74 | 1134 | 34 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29, 2029-30 |
| [autumn_statement_2023](autumn_statement_2023/COMPARISON.md) | Registered construction replay complete | 77 | 1116 | 50 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29 |
| [spring_budget_2023](spring_budget_2023/COMPARISON.md) | Registered construction replay complete | 89 | 1020 | 12 | 2024-25, 2025-26, 2026-27, 2027-28 |
| [spring_budget_2024](spring_budget_2024/COMPARISON.md) | Registered construction replay complete | 49 | 816 | 40 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29 |
| [spring_statement_2025](spring_statement_2025/COMPARISON.md) | Registered construction replay complete | 32 | 498 | 12 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29, 2029-30 |

## Source inventory accounting

These amounts sum all source heads and costing years, including zero cells. They are inventory totals, not one-year event costings or numerical agreement statistics.

| Event / class | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |
|---|---:|---:|---:|---:|
| autumn_budget_2024 / expressible | 0 | 0 | 0.000 | 0.000 |
| autumn_budget_2024 / partial | 5 | 60 | 148.279 | 152.288 |
| autumn_budget_2024 / not_expressible | 43 | 438 | 42.163 | 71.094 |
| autumn_budget_2024 / out_of_household_scope | 26 | 636 | -380.606 | 477.285 |
| autumn_statement_2023 / expressible | 0 | 0 | 0.000 | 0.000 |
| autumn_statement_2023 / partial | 4 | 84 | -55.217 | 65.982 |
| autumn_statement_2023 / not_expressible | 35 | 318 | 15.971 | 21.286 |
| autumn_statement_2023 / out_of_household_scope | 38 | 714 | -67.493 | 99.223 |
| spring_budget_2023 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_budget_2023 / partial | 2 | 18 | -2.014 | 2.014 |
| spring_budget_2023 / not_expressible | 39 | 324 | -22.202 | 40.640 |
| spring_budget_2023 / out_of_household_scope | 48 | 678 | -63.834 | 83.759 |
| spring_budget_2024 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_budget_2024 / partial | 3 | 48 | -51.930 | 58.201 |
| spring_budget_2024 / not_expressible | 26 | 276 | 9.152 | 28.291 |
| spring_budget_2024 / out_of_household_scope | 20 | 492 | -1.255 | 25.416 |
| spring_statement_2025 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_statement_2025 / partial | 2 | 18 | 2.365 | 13.031 |
| spring_statement_2025 / not_expressible | 17 | 156 | 13.906 | 22.174 |
| spring_statement_2025 / out_of_household_scope | 13 | 324 | -10.696 | 39.774 |

### Not-expressible gap split

construction_pending identifies unfinished replay constructions; model_or_data_gap identifies evidenced model or data limitations.

| Event / gap kind | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |
|---|---:|---:|---:|---:|
| autumn_budget_2024 / construction_pending | 14 | 114 | -2.503 | 21.454 |
| autumn_budget_2024 / model_or_data_gap | 29 | 324 | 44.666 | 49.640 |
| autumn_statement_2023 / construction_pending | 24 | 204 | 8.607 | 10.499 |
| autumn_statement_2023 / model_or_data_gap | 11 | 114 | 7.364 | 10.787 |
| spring_budget_2023 / construction_pending | 23 | 180 | -18.605 | 22.208 |
| spring_budget_2023 / model_or_data_gap | 16 | 144 | -3.597 | 18.432 |
| spring_budget_2024 / construction_pending | 17 | 192 | -4.211 | 14.828 |
| spring_budget_2024 / model_or_data_gap | 9 | 84 | 13.364 | 13.463 |
| spring_statement_2025 / construction_pending | 6 | 42 | 4.520 | 4.858 |
| spring_statement_2025 / model_or_data_gap | 11 | 114 | 9.386 | 17.316 |

## Agreement profile

| Tax head | Source-row ratio bins |
|---|---|
| Aggregates levy | not_available: 6 |
| Air passenger duty | not_available: 12 |
| Alcohol duty | not_available: 36 |
| Bank surcharge | not_available: 12 |
| Betting | not_available: 18 |
| Building safety levy | not_available: 6 |
| Business rates | not_available: 54 |
| CBAM | not_available: 12 |
| Capital gains tax | not_available: 108, obr_zero: 1, opposite_sign: 1, same_sign_ratio_at_least_2: 4 |
| Climate change levy | not_available: 30 |
| Company and other credits | not_available: 60 |
| Corporation tax (onshore) | not_available: 234 |
| Council Tax | not_available: 30 |
| Crime levy | not_available: 6 |
| Customs duty | not_available: 54 |
| Electricity generators levy | not_available: 12 |
| Emissions trading scheme | not_available: 6 |
| Energy bills subsidies | not_available: 18 |
| Energy profits levy | not_available: 12 |
| Fuel Duty | not_available: 12 |
| Fuel duty | not_available: 6 |
| Gross operating surplus | not_available: 6 |
| Immigration health surcharge | not_available: 6 |
| Income tax | both_zero: 5, not_available: 410, opposite_sign: 1, pe_zero: 21, same_sign_ratio_at_least_2: 13 |
| Inheritance tax | not_available: 60 |
| Interest and dividend receipts | not_available: 54 |
| Landfill tax | not_available: 12 |
| Locally-financed capital expenditure | not_available: 24 |
| Locally-financed current expenditure | not_available: 132 |
| Multinational top-up tax | not_available: 6 |
| NICs | both_zero: 1, not_available: 175, pe_zero: 4, same_sign_ratio_0.8_to_1.25: 25, same_sign_ratio_1.25_to_2: 5 |
| Net public service pension payments | not_available: 18 |
| North sea taxes | not_available: 6 |
| Other AME (current) | not_available: 66 |
| Other departmental expenditure (capital) | not_available: 30 |
| Other departmental expenditure (current) | not_available: 12 |
| Other tax | not_available: 12 |
| PSCE in RDEL | not_available: 876 |
| PSGI in CDEL | not_available: 216 |
| Passport fees | not_available: 6 |
| Penalties | not_available: 18 |
| Plastic packaging tax | not_available: 6 |
| Scottish AME (capital)  | not_available: 12 |
| Scottish AME (current)  | not_available: 36 |
| Scottish BGA (capital) | not_available: 54 |
| Scottish BGA (current) | not_available: 684 |
| Soft drinks Levy | not_available: 6 |
| Stamp duty | not_available: 79, same_sign_ratio_at_least_2: 5 |
| Statutory gaming levy | not_available: 6 |
| Student loans | not_available: 30 |
| Tobacco duty | not_available: 48 |
| VAT | not_available: 139, same_sign_ratio_1.25_to_2: 5 |
| VAT refunds | not_available: 12 |
| Vaping duty | not_available: 18 |
| Vehicle excise duty | not_available: 18 |
| Visa fees | not_available: 12 |
| Welfare inside cap | both_zero: 4, not_available: 261, same_sign_ratio_0.5_to_0.8: 7, same_sign_ratio_0.8_to_1.25: 4, same_sign_ratio_1.25_to_2: 13, same_sign_ratio_at_least_2: 21, same_sign_ratio_below_0.5: 8 |
| Welfare outside cap | not_available: 96 |
| Welsh BGA (current) | not_available: 30 |

| Measure type | Source-row ratio bins |
|---|---|
| administration | not_available: 678 |
| business_tax | not_available: 516 |
| capital_gains_tax | not_available: 72, obr_zero: 1, opposite_sign: 1, same_sign_ratio_at_least_2: 4 |
| carers_allowance | not_available: 12 |
| child_benefit | not_available: 2, same_sign_ratio_0.5_to_0.8: 4, same_sign_ratio_0.8_to_1.25: 1, same_sign_ratio_at_least_2: 5 |
| fuel_duty | not_available: 18 |
| housing_benefit | not_available: 7, same_sign_ratio_1.25_to_2: 5 |
| income_tax | not_available: 106, pe_zero: 4, same_sign_ratio_at_least_2: 4 |
| indirect_tax | not_available: 162 |
| inheritance_tax | not_available: 90 |
| local_government_finance | not_available: 6 |
| national_insurance | both_zero: 6, not_available: 141, opposite_sign: 1, pe_zero: 21, same_sign_ratio_0.8_to_1.25: 25, same_sign_ratio_1.25_to_2: 13, same_sign_ratio_at_least_2: 21 |
| other | not_available: 840 |
| savings | not_available: 36 |
| scope | not_available: 1152 |
| stamp_duty_land_tax | not_available: 25, same_sign_ratio_at_least_2: 5 |
| tax_benefit | not_available: 156 |
| transport | not_available: 120 |
| universal_credit | both_zero: 4, not_available: 26, same_sign_ratio_0.5_to_0.8: 3, same_sign_ratio_0.8_to_1.25: 2, same_sign_ratio_at_least_2: 4, same_sign_ratio_below_0.5: 3 |
| value_added_tax | not_available: 13, same_sign_ratio_1.25_to_2: 5 |
| welfare | not_available: 240 |
| winter_fuel_payment | not_available: 18, same_sign_ratio_0.8_to_1.25: 1, same_sign_ratio_below_0.5: 5 |

## Named axes and explained share

population_vintage tags every row: the fiscal event's OBR forecast differs from the certified 2024 population and its later calibration targets. behavioural_adjustment, baseline_vintage, cy_proxies_fy and head_scope describe the other construction differences. construction_scope identifies partial measures. The pipeline does not adjust the population vintage.

Pinned employer-NIC incidence assigns the wage adjustment fully to employees while holding employer cost fixed. OBR's direct per-head costings exclude separately reported macroeconomic indirect effects. This construction/head_scope difference is named, but its contribution to the raw gaps remains unsized.

Axis-tagged coverage: 148 computed rows, £126.553bn of absolute raw gap. Explained share is available on 0 rows; relevant unsized axes withhold it on the rest. These are different quantities.

## Largest unexplained divergences

The queue below is ranked by absolute residual_plus_unsized, after any evidence-backed sized terms. It names variables and a minimal run selection for investigation. A raw gap with unsized vintage or behavioural terms does not establish a PolicyEngine model issue. Multiple years of one measure share a potential mechanism, so the queue selects one row per measure.

| Event / measure | FY / head | Residual £bn | Variables | Cause class | Evidence / diagnosis | Minimal replay |
|---|---|---:|---|---|---|---|
| autumn_budget_2024 / Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold | 2029-30 / Income tax | -8.001 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_budget_2024 --measures autumn_budget_2024__employer_nics_package --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029` |
| spring_budget_2023 / Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023 | 2027-28 / Income tax | -3.031 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_budget_2023 --measures spring_budget_2023__pension_annual_allowance_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2027` |
| autumn_statement_2023 / National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024 | 2028-29 / NICs | -2.726 | ni_class_1_employee, ni_class_1_employer, ni_class_2, ni_class_4 | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_statement_2023 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028` |
| autumn_budget_2024 / Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026 | 2027-28 / Capital gains tax | 2.578 | capital_gains_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_budget_2024 --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027` |
| spring_budget_2024 / National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024 | 2028-29 / NICs | -2.478 | ni_class_1_employee, ni_class_1_employer, ni_class_2, ni_class_4 | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_budget_2024 --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028` |
| autumn_budget_2024 / Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024 | 2029-30 / Stamp duty | 2.020 | stamp_duty_land_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_budget_2024 --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029` |
| spring_statement_2025 / Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30 | 2029-30 / Welfare inside cap | -1.699 | universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_statement_2025 --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2029` |
| autumn_budget_2024 / Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25 | 2029-30 / Welfare inside cap | -1.260 | winter_fuel_allowance | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_budget_2024 --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029` |
| spring_budget_2024 / High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024 | 2028-29 / Income tax | -1.179 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_budget_2024 --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028` |
| autumn_statement_2023 / Local Housing Allowance (LHA): set to the 30th percentile from April 2024 | 2025-26 / Welfare inside cap | -0.824 | housing_benefit, universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_statement_2023 --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025` |
| spring_statement_2025 / Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30 | 2029-30 / Welfare inside cap | 0.793 | universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_statement_2025 --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2029` |
| autumn_budget_2024 / VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025 | 2028-29 / VAT | 0.512 | private_school_vat | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_budget_2024 --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028` |
| spring_budget_2024 / National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024 | 2028-29 / Income tax | -0.360 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_budget_2024 --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028` |
| autumn_statement_2023 / National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024 | 2028-29 / Income tax | -0.262 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_statement_2023 --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028` |
| autumn_statement_2023 / National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024 | 2028-29 / Income tax | -0.203 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event autumn_statement_2023 --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028` |
| spring_budget_2023 / DWP: increase the maximum support available in Universal Credit for childcare costs | 2027-28 / Welfare inside cap | -0.155 | universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --bundle uk-data-1.58.0__pe-uk-2.125.1 --event spring_budget_2023 --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027` |

Evidence-backed PolicyEngine issue candidates recorded: 0. No upstream issues were filed by this replay lane.
