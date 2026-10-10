# UK replay engine comparison

Base: `populace-uk-2023__pe-uk-2.89.2`. New: `uk-data-1.58.0__pe-uk-2.125.1`.

Amounts are £m, positive for a gain to the Exchequer. Calendar year Y proxies fiscal year Y–(Y+1). Ratios and bins are descriptive, not a score. Attribution comes only from the authored evidence file: a sized driver cites a computed run, and an unsized one names a mechanism without a number.

4584 OBR source rows: 18 base_only, 142 computed_in_both, 30 construction_changed, 4394 uncomputed_in_both.

## Measures computed in at least one bundle

| Event | Measure | OBR title |
|---|---|---|
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026 |
| autumn_budget_2024 | `employer_nics_package` | Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold |
| autumn_budget_2024 | `private_school_vat_20pct` | VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025 |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024 |
| autumn_budget_2024 | `winter_fuel_means_test` | Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024 |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | Local Housing Allowance (LHA): set to the 30th percentile from April 2024 |
| spring_budget_2023 | `pension_annual_allowance_package` | Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023 |
| spring_budget_2023 | `uc_childcare_cap_increase` | DWP: increase the maximum support available in Universal Credit for childcare costs |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024 |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30 |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30 |

## Computed measures by fiscal year

Each line sums a measure's computed heads for one source FY. OBR is summed over the same heads. Change is new minus base.

| Event | Measure | FY | OBR | PE base | PE new | Change | Status | Drivers |
|---|---|---|---:|---:|---:|---:|---|---|
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2024-25 | 0.0 | — | 963.0 | — | construction_changed | construction_change (unsized), data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2025-26 | 1,005.0 | 4,655.3 | 2,337.8 | -2,317.5 | construction_changed | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2026-27 | 95.8 | 4,793.6 | 2,414.6 | -2,379.0 | construction_changed | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2027-28 | -75.8 | 4,952.4 | 2,502.0 | -2,450.4 | construction_changed | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2028-29 | 755.7 | 5,113.0 | 2,590.3 | -2,522.6 | construction_changed | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2029-30 | 985.9 | 5,273.8 | 2,678.8 | -2,595.0 | construction_changed | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `employer_nics_package` | 2024-25 | 0.0 | 0.0 | 0.0 | 0.0 | computed_in_both | unchanged |
| autumn_budget_2024 | `employer_nics_package` | 2025-26 | 23,737.6 | 16,011.3 | 16,827.1 | 815.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `employer_nics_package` | 2026-27 | 23,610.4 | 16,246.7 | 17,077.9 | 831.2 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `employer_nics_package` | 2027-28 | 24,027.1 | 16,422.5 | 17,298.2 | 875.7 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `employer_nics_package` | 2028-29 | 24,748.6 | 16,629.9 | 17,485.9 | 856.0 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `employer_nics_package` | 2029-30 | 25,494.7 | 16,744.7 | 17,902.8 | 1,158.1 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `private_school_vat_20pct` | 2025-26 | 1,505.7 | 1,258.4 | 1,972.7 | 714.3 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `private_school_vat_20pct` | 2026-27 | 1,557.7 | 1,292.3 | 2,022.8 | 730.5 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `private_school_vat_20pct` | 2027-28 | 1,608.9 | 1,323.0 | 2,065.8 | 742.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `private_school_vat_20pct` | 2028-29 | 1,664.3 | 1,354.9 | 2,176.6 | 821.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `private_school_vat_20pct` | 2029-30 | 1,726.5 | 1,388.0 | 2,166.5 | 778.5 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2025-26 | 208.3 | 2,039.0 | 2,190.5 | 151.5 | computed_in_both | data_release (unsized) |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2026-27 | 334.2 | 2,106.5 | 2,263.0 | 156.5 | computed_in_both | data_release (unsized) |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2027-28 | 413.5 | 2,182.6 | 2,344.8 | 162.2 | computed_in_both | data_release (unsized) |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2028-29 | 450.8 | 2,259.3 | 2,427.2 | 168.0 | computed_in_both | data_release (unsized) |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2029-30 | 490.3 | 2,336.4 | 2,510.1 | 173.7 | computed_in_both | data_release (unsized) |
| autumn_budget_2024 | `winter_fuel_means_test` | 2024-25 | 1,324.0 | 1,713.9 | 1,494.9 | -219.0 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `winter_fuel_means_test` | 2025-26 | 1,378.0 | 349.9 | 185.5 | -164.4 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `winter_fuel_means_test` | 2026-27 | 1,420.0 | 367.9 | 193.8 | -174.1 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `winter_fuel_means_test` | 2027-28 | 1,439.0 | 397.3 | 218.6 | -178.7 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `winter_fuel_means_test` | 2028-29 | 1,459.0 | 417.6 | 226.9 | -190.7 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_budget_2024 | `winter_fuel_means_test` | 2029-30 | 1,501.0 | 453.2 | 241.1 | -212.1 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2024-25 | -8,643.5 | -10,996.3 | -10,518.8 | 477.5 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2025-26 | -8,422.8 | -11,591.5 | -11,190.4 | 401.1 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2026-27 | -8,487.2 | -11,965.4 | -11,644.5 | 320.9 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2027-28 | -8,609.3 | -12,246.8 | -11,972.8 | 274.1 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2028-29 | -8,789.2 | -12,554.1 | -12,257.7 | 296.4 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2023-24 | 0.0 | 0.0 | — | — | base_only | window_change (unsized) |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2024-25 | -344.6 | -502.5 | -381.6 | 120.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2025-26 | -343.0 | -509.8 | -396.7 | 113.2 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2026-27 | -210.4 | -531.1 | -407.8 | 123.3 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2027-28 | -156.1 | -1,326.9 | -421.2 | 905.7 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (sized, £786.8m) |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2028-29 | -110.5 | -1,042.6 | -436.4 | 606.2 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (sized, £495.9m) |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2023-24 | 0.0 | 0.0 | — | — | base_only | window_change (unsized) |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2024-25 | -321.2 | -550.7 | -286.8 | 263.9 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2025-26 | -299.2 | -558.3 | -290.5 | 267.9 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2026-27 | -209.7 | -575.8 | -305.8 | 270.0 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2027-28 | -175.3 | -598.9 | -324.8 | 274.1 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2028-29 | -153.5 | -623.0 | -343.8 | 279.2 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2023-24 | 0.0 | 0.0 | — | — | base_only | window_change (unsized) |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2024-25 | -952.6 | -584.6 | -1,736.6 | -1,152.0 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2025-26 | -1,092.1 | -799.8 | -1,916.1 | -1,116.3 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2026-27 | -1,188.5 | -833.7 | -1,946.3 | -1,112.6 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2027-28 | -1,259.9 | -859.1 | -2,004.7 | -1,145.7 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2028-29 | -1,273.0 | -859.8 | -2,025.5 | -1,165.6 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `pension_annual_allowance_package` | 2023-24 | -89.9 | -3,693.2 | — | — | base_only | window_change (unsized) |
| spring_budget_2023 | `pension_annual_allowance_package` | 2024-25 | -248.3 | -4,297.5 | -2,781.3 | 1,516.2 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `pension_annual_allowance_package` | 2025-26 | -425.6 | -5,395.1 | -3,047.4 | 2,347.7 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `pension_annual_allowance_package` | 2026-27 | -435.7 | -6,040.7 | -3,279.4 | 2,761.3 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `pension_annual_allowance_package` | 2027-28 | -442.2 | -6,456.5 | -3,451.1 | 3,005.3 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2023-24 | -41.3 | -2.3 | — | — | base_only | window_change (unsized) |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2024-25 | -86.8 | -1.8 | -218.2 | -216.4 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2025-26 | -75.4 | -1.7 | -228.9 | -227.1 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2026-27 | -81.6 | -1.9 | -232.6 | -230.7 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2027-28 | -86.8 | -2.1 | -241.9 | -239.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2023-24 | 0.0 | 0.0 | — | — | base_only | window_change (unsized) |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2024-25 | -9,281.8 | -10,996.3 | -10,518.8 | 477.5 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2025-26 | -9,058.6 | -11,591.5 | -11,190.4 | 401.1 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2026-27 | -9,128.6 | -11,965.4 | -11,644.5 | 320.9 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2027-28 | -9,244.0 | -12,246.8 | -11,972.8 | 274.1 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2028-29 | -9,436.4 | -12,554.1 | -12,257.7 | 296.4 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2023-24 | 0.0 | 0.0 | — | — | base_only | window_change (unsized) |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2024-25 | -658.2 | -1,101.8 | -573.0 | 528.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2025-26 | -681.0 | -1,117.2 | -580.6 | 536.6 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2026-27 | -496.3 | -1,152.5 | -611.5 | 541.0 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2027-28 | -431.1 | -1,199.2 | -649.4 | 549.8 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2028-29 | -390.7 | -1,247.2 | -688.8 | 558.4 | computed_in_both | data_release (unsized), nics_freeze (unsized), other_engine_change (unsized) |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2023-24 | 0.0 | 0.0 | — | — | base_only | window_change (unsized) |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2024-25 | -541.0 | -1,491.8 | -1,158.4 | 333.4 | computed_in_both | data_release (unsized), hicbc_opt_out (sized, £-273.4m), other_engine_change (unsized) |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2025-26 | -636.0 | -1,592.8 | -1,315.5 | 277.2 | computed_in_both | data_release (unsized), hicbc_opt_out (sized, £-277.8m), other_engine_change (unsized) |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2026-27 | -641.0 | -1,720.6 | -1,473.9 | 246.7 | computed_in_both | data_release (unsized), hicbc_opt_out (sized, £-301.6m), other_engine_change (unsized) |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2027-28 | -647.0 | -1,844.2 | -1,609.7 | 234.5 | computed_in_both | data_release (unsized), hicbc_opt_out (sized, £-321.2m), other_engine_change (unsized) |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2028-29 | -658.0 | -1,972.0 | -1,738.8 | 233.2 | computed_in_both | data_release (unsized), hicbc_opt_out (sized, £-366.9m), other_engine_change (unsized) |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2024-25 | 0.0 | 0.0 | 0.0 | 0.0 | computed_in_both | unchanged |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2025-26 | 0.0 | 0.0 | 0.0 | 0.0 | computed_in_both | unchanged |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2026-27 | 760.3 | 264.1 | 746.1 | 482.0 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2027-28 | 1,555.7 | 338.6 | 904.9 | 566.4 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2028-29 | 2,328.4 | 436.3 | 1,088.2 | 651.9 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2029-30 | 3,053.5 | 626.6 | 1,354.9 | 728.3 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2024-25 | 0.0 | 0.0 | 0.0 | 0.0 | computed_in_both | unchanged |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2025-26 | 0.0 | 0.0 | 0.0 | 0.0 | computed_in_both | unchanged |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2026-27 | -667.4 | -403.7 | -720.9 | -317.2 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2027-28 | -938.1 | -409.5 | -731.5 | -322.0 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2028-29 | -1,224.4 | -414.3 | -746.1 | -331.8 | computed_in_both | data_release (unsized), other_engine_change (unsized) |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2029-30 | -1,546.1 | -421.9 | -753.3 | -331.4 | computed_in_both | data_release (unsized), other_engine_change (unsized) |

## Attribution evidence

Why each driver is named. A paired-run or computed artifact behind a sized driver is bound by hash in the attribution file.

### `capital_gains_main_rates_and_reliefs` (autumn_budget_2024)

FY 2024-25:

- **construction_change** (unsized)
  - Registry construction_adjustments cgt_fiscal_year_blend_annual_reversal: the CGT rate parameters carry fiscal_year_blend at 2.125.1, so processed 2024 already blends in the 30 October 2024 increase and the reversal starts on 1 January 2024. At 2.89.2 the increase first appears in 2025 and FY2024-25 was a timing gap.
- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1806: Correct the capital gains rate effective date and annualise the split year (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1861: Charge BADR, residential property and carried interest gains at their own CGT rates (merged after 2.89.2, in 2.125.1)
  - The 1.58.0 dataset has one pooled capital_gains column and none of the gain-type inputs #1861 reads, so those branches take their default (docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md, dataset input contract).

FY 2025-26 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1806: Correct the capital gains rate effective date and annualise the split year (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1861: Charge BADR, residential property and carried interest gains at their own CGT rates (merged after 2.89.2, in 2.125.1)
  - The 1.58.0 dataset has one pooled capital_gains column and none of the gain-type inputs #1861 reads, so those branches take their default (docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md, dataset input contract).
  - Note: The construction digest differs because of the 2024 start date, but from 2025 both bundles execute the same full-year reversal.

### `employer_nics_package` (autumn_budget_2024)

FY 2025-26 to 2026-27:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#2165: Annualise the employer NI secondary threshold to the statutory £5,000 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1895: Charge employer NI on employees over state pension age (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1881: Stop stacking the trading allowance on expenses already netted from profit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2172: Model landlords' finance-cost tax reduction and stop the property allowance stacking (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1939: Compute the State Pension triple lock from its statutory inputs (merged after 2.89.2, in 2.125.1)

FY 2027-28 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **nics_freeze** (unsized)
  - PolicyEngine/policyengine-uk#1959: Hold NICs thresholds at 2026-27 levels through 2030-31 (merged after 2.89.2, in 2.125.1)
  - Diagnostic nics_threshold_freeze_end_date: at 2.89.2 the Class 4 limits rise with CPI from 2027 (lower profits limit £12,821 in 2027); at 2.125.1 they stay at £12,570 and £50,270 through 2030. Thresholds are identical at both pins before 2027, so this driver applies from FY2027-28 only. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#2165: Annualise the employer NI secondary threshold to the statutory £5,000 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1895: Charge employer NI on employees over state pension age (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1881: Stop stacking the trading allowance on expenses already netted from profit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2172: Model landlords' finance-cost tax reduction and stop the property allowance stacking (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1939: Compute the State Pension triple lock from its statutory inputs (merged after 2.89.2, in 2.125.1)

### `private_school_vat_20pct` (autumn_budget_2024)

FY 2025-26 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1896: Replace generic child and adult flags with each programme's legal definitions (merged after 2.89.2, in 2.125.1)
  - Attendance is imputed from each household's weighted net-income percentile (attends_private_school.py:55-96 at 2.125.1), so engine changes to taxes and benefits can move it. The formula differs between the pins only in the child flag: is_child at 2.89.2, age_under_18 at 2.125.1.

### `sdlt_additional_dwelling_surcharge_2pp` (autumn_budget_2024)

FY 2025-26 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
  - Diagnostic sdlt_additional_purchase_stock_pe_uk_2238: identical output at 2.89.2 and 2.125.1, so PolicyEngine/policyengine-uk#2238 (a purchasing household's whole other-property stock charged as an additional purchase) is present at both pins and does not explain this change. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).

### `winter_fuel_means_test` (autumn_budget_2024)

FY 2024-25 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1939: Compute the State Pension triple lock from its statutory inputs (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1922: Split additional State Pension by the period's State Pension type (merged after 2.89.2, in 2.125.1)

### `class_1_employee_nics_main_rate_cut_2p` (autumn_statement_2023)

FY 2024-25 to 2026-27:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

FY 2027-28 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **nics_freeze** (unsized)
  - PolicyEngine/policyengine-uk#1959: Hold NICs thresholds at 2026-27 levels through 2030-31 (merged after 2.89.2, in 2.125.1)
  - Diagnostic nics_threshold_freeze_end_date: at 2.89.2 the Class 4 limits rise with CPI from 2027 (lower profits limit £12,821 in 2027); at 2.125.1 they stay at £12,570 and £50,270 through 2030. Thresholds are identical at both pins before 2027, so this driver applies from FY2027-28 only. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `class_2_self_employed_nics_abolition` (autumn_statement_2023)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2026-27:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#2058: Fix Class 2 and Class 4 NICs against SSCBA 1992 for 2015-16 to 2026-27 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

FY 2027-28 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **nics_freeze** (unsized)
  - PolicyEngine/policyengine-uk#1959: Hold NICs thresholds at 2026-27 levels through 2030-31 (merged after 2.89.2, in 2.125.1)
  - Diagnostic nics_threshold_freeze_end_date: at 2.89.2 the Class 4 limits rise with CPI from 2027 (lower profits limit £12,821 in 2027); at 2.125.1 they stay at £12,570 and £50,270 through 2030. Thresholds are identical at both pins before 2027, so this driver applies from FY2027-28 only. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
- **other_engine_change** (sized in the table above)
  - results/uk/events/engine_pairs/populace-uk-2023__pe-uk-2.89.2__uk-data-1.58.0__pe-uk-2.125.1/autumn_statement_2023__class_2_self_employed_nics_abolition_2027__ni_class_4.json
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2058: Fix Class 2 and Class 4 NICs against SSCBA 1992 for 2015-16 to 2026-27 (merged after 2.89.2, in 2.125.1)
  - At 2.89.2 the Class 4 annual maximum includes Class 2 (ni_class_4_maximum.py:20-28), so restoring a Class 2 rate moves Class 4. At 2.125.1 Class 2 leaves that maximum from 6 April 2024 (ni_class_4_maximum.py:28-32), so it can't.
  - Note: The size is the ni_class_4 component only: its effect in this measure-year goes to zero whatever the population. The change in ni_class_2 itself is not sized.

### `class_4_self_employed_nics_main_rate_cut_1p` (autumn_statement_2023)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2026-27:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

FY 2027-28 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **nics_freeze** (unsized)
  - PolicyEngine/policyengine-uk#1959: Hold NICs thresholds at 2026-27 levels through 2030-31 (merged after 2.89.2, in 2.125.1)
  - Diagnostic nics_threshold_freeze_end_date: at 2.89.2 the Class 4 limits rise with CPI from 2027 (lower profits limit £12,821 in 2027); at 2.125.1 they stay at £12,570 and £50,270 through 2030. Thresholds are identical at both pins before 2027, so this driver applies from FY2027-28 only. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `lha_reset_to_30th_percentile` (autumn_statement_2023)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#2022: Use published LHA determinations and apply Sch 3B paras 3 and 3A (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1844: Cap LHA at the national maximum and hold frozen rates at the last determination (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1926: Cap the eligible rent at the LHA before the Housing Benefit taper (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2006: Give sharers, boarders and lodgers their own rent, tenure and LHA category (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `pension_annual_allowance_package` (spring_budget_2023)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2027-28:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1881: Stop stacking the trading allowance on expenses already netted from profit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2172: Model landlords' finance-cost tax reduction and stop the property allowance stacking (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1939: Compute the State Pension triple lock from its statutory inputs (merged after 2.89.2, in 2.125.1)
  - Diagnostic annual_allowance_relief_and_charge_pe_uk_2237: identical output at 2.89.2 and 2.125.1, so PolicyEngine/policyengine-uk#2237 (relief capped at the Annual Allowance and the excess also charged) is present at both pins and does not explain this change. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).

### `uc_childcare_cap_increase` (spring_budget_2023)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2027-28:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1857: Add carer and UC childcare take-up inputs (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2088: Apply the UC childcare work condition's partner exceptions and treated-as-working cases (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `class_1_employee_nics_main_rate_cut_2pp` (spring_budget_2024)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2026-27:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

FY 2027-28 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **nics_freeze** (unsized)
  - PolicyEngine/policyengine-uk#1959: Hold NICs thresholds at 2026-27 levels through 2030-31 (merged after 2.89.2, in 2.125.1)
  - Diagnostic nics_threshold_freeze_end_date: at 2.89.2 the Class 4 limits rise with CPI from 2027 (lower profits limit £12,821 in 2027); at 2.125.1 they stay at £12,570 and £50,270 through 2030. Thresholds are identical at both pins before 2027, so this driver applies from FY2027-28 only. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `class_4_self_employed_nics_main_rate_cut_2pp` (spring_budget_2024)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2026-27:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

FY 2027-28 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **nics_freeze** (unsized)
  - PolicyEngine/policyengine-uk#1959: Hold NICs thresholds at 2026-27 levels through 2030-31 (merged after 2.89.2, in 2.125.1)
  - Diagnostic nics_threshold_freeze_end_date: at 2.89.2 the Class 4 limits rise with CPI from 2027 (lower profits limit £12,821 in 2027); at 2.125.1 they stay at £12,570 and £50,270 through 2030. Thresholds are identical at both pins before 2027, so this driver applies from FY2027-28 only. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1886: Charge Class 4 NI on full trading profits, without deducting Class 1 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1919: Charge Class 4 NICs on Chapter 2 profits, after capital allowances and the trading allowance (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1884: Fix Class 4 NI dropping the additional-rate band at non-round thresholds (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1899: Set State Pension age from date of birth, including the rise to 67 (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `hicbc_threshold_and_taper` (spring_budget_2024)

FY 2023-24:

- **window_change** (unsized)
  - data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json records data_year 2024, so calendar 2023 (FY2023-24) is outside the new bundle's window. See docs/uk_replay/YEARS_uk-data-1.58.0__pe-uk-2.125.1.md.

FY 2024-25 to 2028-29:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **hicbc_opt_out** (sized in the table above)
  - PolicyEngine/policyengine-uk#2140: Fix Child Benefit opt-outs, rental flags and bus fare modelling (merged after 2.89.2, in 2.125.1)
  - At 2.89.2 child_benefit is entitlement for claimants (child_benefit.py:12-13) and doesn't read the HICBC thresholds, so this measure's Child Benefit head is exactly zero. At 2.125.1 payment stops for opted-out families while the charge share stays at or above the opt-out threshold (child_benefit.py:20-35), so the head responds.
  - Diagnostic hicbc_opt_out: an opted-out family is paid and charged £1,355 at 2.89.2, and is paid £0 and charged £0 at 2.125.1. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).
  - Note: The size is the whole Child Benefit head in the new bundle. The same change also moves the income tax head, which is not sized.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1881: Stop stacking the trading allowance on expenses already netted from profit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2172: Model landlords' finance-cost tax reduction and stop the property allowance stacking (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1939: Compute the State Pension triple lock from its statutory inputs (merged after 2.89.2, in 2.125.1)

### `uc_health_element_freeze_and_new_claimant_cut` (spring_statement_2025)

FY 2026-27 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)

### `uc_standard_allowance_above_inflation` (spring_statement_2025)

FY 2026-27 to 2029-30:

- **data_release** (unsized)
  - The base pin's population is populace-uk-2023 (data year 2023); the new pin's is enhanced_frs_2024_25 from policyengine-uk-data 1.58.0 (data year 2024). No certified pairing holds the data fixed, so the data release and the engine changes are not separated. The base ratio beside each row shows how that head's certified aggregate moved.
- **other_engine_change** (unsized)
  - PolicyEngine/policyengine-uk#1815: Add Universal Credit deductions with Fair Repayment Rate cap (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1850: Fix Universal Credit claimant and qualifying-child roles (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1978: Count only claimants' income in Universal Credit (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1949: Deduct only each person's own tax and NI on earnings from UC earned income (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#1973: Apply the UC minimum income floor to net earned income against a net threshold (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2081: Apply the UC minimum income floor only to claimants subject to all work-related requirements (merged after 2.89.2, in 2.125.1)
  - PolicyEngine/policyengine-uk#2084: Model a Universal Credit claim by a member of a couple as a single person (merged after 2.89.2, in 2.125.1)
  - Diagnostic uc_standard_allowance_2027_2030_pe_uk_2239: identical output at 2.89.2 and 2.125.1, so PolicyEngine/policyengine-uk#2239 (the 2027-28 to 2029-30 standard allowance uplifts missing) is present at both pins and does not explain this change. Paired synthetic diagnostics at both pins: results/uk/events/diagnostics/engine_pairs/ (2.89.2) and results/uk/events/bundles/uk-data-1.58.0__pe-uk-2.125.1/diagnostics/ (2.125.1).

## Computed source rows

One line per OBR head and FY. The base ratio is the new-to-base ratio of the head's certified aggregate (how the tax or spending base moved); the measure ratio is the same ratio for the measure's effect.

| Event | Measure | FY / head | OBR | PE base | PE new | Change | Base bin | New bin | Status | Base ratio | Measure ratio |
|---|---|---|---:|---:|---:|---:|---|---|---|---:|---:|
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2024-25 / Capital gains tax | 0.0 | — | 963.0 | — | not_available | obr_zero | construction_changed | — | — |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2025-26 / Capital gains tax | 1,005.0 | 4,655.3 | 2,337.8 | -2,317.5 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | construction_changed | 0.54 | 0.50 |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2026-27 / Capital gains tax | 95.8 | 4,793.6 | 2,414.6 | -2,379.0 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | construction_changed | 0.54 | 0.50 |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2027-28 / Capital gains tax | -75.8 | 4,952.4 | 2,502.0 | -2,450.4 | opposite_sign | opposite_sign | construction_changed | 0.54 | 0.51 |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2028-29 / Capital gains tax | 755.7 | 5,113.0 | 2,590.3 | -2,522.6 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | construction_changed | 0.54 | 0.51 |
| autumn_budget_2024 | `capital_gains_main_rates_and_reliefs` | 2029-30 / Capital gains tax | 985.9 | 5,273.8 | 2,678.8 | -2,595.0 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | construction_changed | 0.54 | 0.51 |
| autumn_budget_2024 | `employer_nics_package` | 2024-25 / Income tax | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 0.75 | — |
| autumn_budget_2024 | `employer_nics_package` | 2024-25 / NICs | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 0.85 | — |
| autumn_budget_2024 | `employer_nics_package` | 2025-26 / Income tax | 0.1 | -8,163.5 | -7,167.0 | 996.5 | opposite_sign | opposite_sign | computed_in_both | 0.76 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2025-26 / NICs | 23,737.5 | 24,174.8 | 23,994.1 | -180.7 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2026-27 / Income tax | -312.9 | -8,507.7 | -7,456.0 | 1,051.7 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2026-27 / NICs | 23,923.3 | 24,754.4 | 24,534.0 | -220.5 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2027-28 / Income tax | -139.4 | -8,784.0 | -7,662.6 | 1,121.4 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2027-28 / NICs | 24,166.6 | 25,206.4 | 24,960.8 | -245.7 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2028-29 / Income tax | -125.0 | -8,988.4 | -7,867.6 | 1,120.9 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2028-29 / NICs | 24,873.6 | 25,618.3 | 25,353.4 | -264.9 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 1.05 |
| autumn_budget_2024 | `employer_nics_package` | 2029-30 / Income tax | -129.8 | -9,404.1 | -8,130.8 | 1,273.3 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 1.07 |
| autumn_budget_2024 | `employer_nics_package` | 2029-30 / NICs | 25,624.6 | 26,148.8 | 26,033.6 | -115.2 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.89 | 1.07 |
| autumn_budget_2024 | `private_school_vat_20pct` | 2025-26 / VAT | 1,505.7 | 1,258.4 | 1,972.7 | 714.3 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | computed_in_both | — | 1.57 |
| autumn_budget_2024 | `private_school_vat_20pct` | 2026-27 / VAT | 1,557.7 | 1,292.3 | 2,022.8 | 730.5 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | computed_in_both | — | 1.57 |
| autumn_budget_2024 | `private_school_vat_20pct` | 2027-28 / VAT | 1,608.9 | 1,323.0 | 2,065.8 | 742.8 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | computed_in_both | — | 1.56 |
| autumn_budget_2024 | `private_school_vat_20pct` | 2028-29 / VAT | 1,664.3 | 1,354.9 | 2,176.6 | 821.8 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | computed_in_both | — | 1.61 |
| autumn_budget_2024 | `private_school_vat_20pct` | 2029-30 / VAT | 1,726.5 | 1,388.0 | 2,166.5 | 778.5 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | computed_in_both | — | 1.56 |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2025-26 / Stamp duty | 208.3 | 2,039.0 | 2,190.5 | 151.5 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 1.50 | 1.07 |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2026-27 / Stamp duty | 334.2 | 2,106.5 | 2,263.0 | 156.5 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 1.52 | 1.07 |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2027-28 / Stamp duty | 413.5 | 2,182.6 | 2,344.8 | 162.2 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 1.52 | 1.07 |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2028-29 / Stamp duty | 450.8 | 2,259.3 | 2,427.2 | 168.0 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 1.51 | 1.07 |
| autumn_budget_2024 | `sdlt_additional_dwelling_surcharge_2pp` | 2029-30 / Stamp duty | 490.3 | 2,336.4 | 2,510.1 | 173.7 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 1.50 | 1.07 |
| autumn_budget_2024 | `winter_fuel_means_test` | 2024-25 / Welfare inside cap | 1,324.0 | 1,713.9 | 1,494.9 | -219.0 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 1.28 | 0.87 |
| autumn_budget_2024 | `winter_fuel_means_test` | 2025-26 / Welfare inside cap | 1,378.0 | 349.9 | 185.5 | -164.4 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 1.02 | 0.53 |
| autumn_budget_2024 | `winter_fuel_means_test` | 2026-27 / Welfare inside cap | 1,420.0 | 367.9 | 193.8 | -174.1 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 1.01 | 0.53 |
| autumn_budget_2024 | `winter_fuel_means_test` | 2027-28 / Welfare inside cap | 1,439.0 | 397.3 | 218.6 | -178.7 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 0.98 | 0.55 |
| autumn_budget_2024 | `winter_fuel_means_test` | 2028-29 / Welfare inside cap | 1,459.0 | 417.6 | 226.9 | -190.7 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 0.98 | 0.54 |
| autumn_budget_2024 | `winter_fuel_means_test` | 2029-30 / Welfare inside cap | 1,501.0 | 453.2 | 241.1 | -212.1 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 0.99 | 0.53 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2024-25 / Income tax | 369.0 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.75 | 0.96 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2024-25 / NICs | -9,128.9 | -11,082.5 | -10,762.0 | 320.5 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.85 | 0.96 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2024-25 / Welfare inside cap | 116.3 | 86.2 | 243.2 | 157.0 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_at_least_2 | computed_in_both | 2.08 | 0.96 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2025-26 / Income tax | 606.8 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.97 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2025-26 / NICs | -9,182.3 | -11,685.8 | -11,458.8 | 227.0 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.97 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2025-26 / Welfare inside cap | 152.7 | 94.2 | 268.4 | 174.1 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.09 | 0.97 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2026-27 / Income tax | 684.4 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.97 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2026-27 / NICs | -9,343.0 | -12,070.1 | -11,919.3 | 150.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | computed_in_both | 0.88 | 0.97 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2026-27 / Welfare inside cap | 171.4 | 104.7 | 274.9 | 170.2 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.09 | 0.97 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2027-28 / Income tax | 784.7 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.98 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2027-28 / NICs | -9,564.2 | -12,356.2 | -12,255.2 | 101.0 | same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | computed_in_both | 0.88 | 0.98 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2027-28 / Welfare inside cap | 170.1 | 109.3 | 282.4 | 173.0 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.09 | 0.98 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2028-29 / Income tax | 870.8 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.98 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2028-29 / NICs | -9,840.0 | -12,663.9 | -12,566.1 | 97.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | computed_in_both | 0.88 | 0.98 |
| autumn_statement_2023 | `class_1_employee_nics_main_rate_cut_2p` | 2028-29 / Welfare inside cap | 180.1 | 109.8 | 308.4 | 198.6 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.10 | 0.98 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2023-24 / Income tax | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2023-24 / NICs | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2023-24 / Welfare inside cap | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2024-25 / Income tax | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 0.75 | 0.76 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2024-25 / NICs | -348.7 | -512.2 | -420.1 | 92.1 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.85 | 0.76 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2024-25 / Welfare inside cap | 4.1 | 9.7 | 38.4 | 28.7 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.08 | 0.76 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2025-26 / Income tax | 1.7 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.78 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2025-26 / NICs | -350.1 | -519.2 | -434.6 | 84.6 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.78 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2025-26 / Welfare inside cap | 5.4 | 9.4 | 37.9 | 28.5 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.78 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2026-27 / Income tax | 141.9 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.77 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2026-27 / NICs | -358.4 | -542.5 | -444.1 | 98.4 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.77 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2026-27 / Welfare inside cap | 6.1 | 11.4 | 36.3 | 24.8 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.77 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2027-28 / Income tax | 206.5 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.32 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2027-28 / NICs | -368.7 | -1,338.8 | -461.7 | 877.2 | same_sign_ratio_at_least_2 | same_sign_ratio_1.25_to_2 | computed_in_both | 0.88 | 0.32 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2027-28 / Welfare inside cap | 6.2 | 11.9 | 40.5 | 28.6 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.32 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2028-29 / Income tax | 261.7 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.42 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2028-29 / NICs | -378.9 | -1,054.6 | -477.6 | 577.0 | same_sign_ratio_at_least_2 | same_sign_ratio_1.25_to_2 | computed_in_both | 0.88 | 0.42 |
| autumn_statement_2023 | `class_2_self_employed_nics_abolition` | 2028-29 / Welfare inside cap | 6.7 | 12.0 | 41.2 | 29.2 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.10 | 0.42 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2023-24 / Income tax | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2023-24 / NICs | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2023-24 / Welfare inside cap | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2024-25 / Income tax | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 0.75 | 0.52 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2024-25 / NICs | -325.3 | -557.2 | -304.8 | 252.3 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.85 | 0.52 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2024-25 / Welfare inside cap | 4.1 | 6.5 | 18.1 | 11.6 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.08 | 0.52 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2025-26 / Income tax | 18.9 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.52 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2025-26 / NICs | -323.5 | -564.7 | -310.6 | 254.1 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.52 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2025-26 / Welfare inside cap | 5.4 | 6.3 | 20.2 | 13.8 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.52 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2026-27 / Income tax | 114.3 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.53 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2026-27 / NICs | -330.1 | -583.5 | -327.2 | 256.3 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.53 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2026-27 / Welfare inside cap | 6.1 | 7.7 | 21.4 | 13.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.53 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2027-28 / Income tax | 161.1 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.54 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2027-28 / NICs | -342.5 | -607.0 | -347.6 | 259.4 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.54 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2027-28 / Welfare inside cap | 6.2 | 8.1 | 22.8 | 14.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.54 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2028-29 / Income tax | 202.8 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.55 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2028-29 / NICs | -363.1 | -631.3 | -368.0 | 263.2 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.55 |
| autumn_statement_2023 | `class_4_self_employed_nics_main_rate_cut_1p` | 2028-29 / Welfare inside cap | 6.7 | 8.3 | 24.2 | 16.0 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | computed_in_both | 2.10 | 0.55 |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2023-24 / Welfare inside cap | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2024-25 / Welfare inside cap | -952.6 | -584.6 | -1,736.6 | -1,152.0 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.05 | 2.97 |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2025-26 / Welfare inside cap | -1,092.1 | -799.8 | -1,916.1 | -1,116.3 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.04 | 2.40 |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2026-27 / Welfare inside cap | -1,188.5 | -833.7 | -1,946.3 | -1,112.6 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.04 | 2.33 |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2027-28 / Welfare inside cap | -1,259.9 | -859.1 | -2,004.7 | -1,145.7 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.04 | 2.33 |
| autumn_statement_2023 | `lha_reset_to_30th_percentile` | 2028-29 / Welfare inside cap | -1,273.0 | -859.8 | -2,025.5 | -1,165.6 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.04 | 2.36 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2023-24 / Income tax | -80.9 | -3,693.2 | — | — | same_sign_ratio_at_least_2 | not_available | base_only | — | — |
| spring_budget_2023 | `pension_annual_allowance_package` | 2023-24 / NICs | -9.0 | 0.0 | — | — | pe_zero | not_available | base_only | — | — |
| spring_budget_2023 | `pension_annual_allowance_package` | 2024-25 / Income tax | -233.9 | -4,297.5 | -2,781.3 | 1,516.2 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.75 | 0.65 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2024-25 / NICs | -14.4 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.85 | 0.65 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2025-26 / Income tax | -405.0 | -5,395.1 | -3,047.4 | 2,347.7 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.56 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2025-26 / NICs | -20.6 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.88 | 0.56 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2026-27 / Income tax | -414.6 | -6,040.7 | -3,279.4 | 2,761.3 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.54 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2026-27 / NICs | -21.1 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.88 | 0.54 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2027-28 / Income tax | -420.4 | -6,456.5 | -3,451.1 | 3,005.3 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.53 |
| spring_budget_2023 | `pension_annual_allowance_package` | 2027-28 / NICs | -21.7 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.88 | 0.53 |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2023-24 / Welfare inside cap | -41.3 | -2.3 | — | — | same_sign_ratio_below_0.5 | not_available | base_only | — | — |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2024-25 / Welfare inside cap | -86.8 | -1.8 | -218.2 | -216.4 | same_sign_ratio_below_0.5 | same_sign_ratio_at_least_2 | computed_in_both | 2.08 | 121.67 |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2025-26 / Welfare inside cap | -75.4 | -1.7 | -228.9 | -227.1 | same_sign_ratio_below_0.5 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 132.81 |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2026-27 / Welfare inside cap | -81.6 | -1.9 | -232.6 | -230.7 | same_sign_ratio_below_0.5 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 120.80 |
| spring_budget_2023 | `uc_childcare_cap_increase` | 2027-28 / Welfare inside cap | -86.8 | -2.1 | -241.9 | -239.8 | same_sign_ratio_below_0.5 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 116.89 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2023-24 / Income tax | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2023-24 / NICs | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2023-24 / Welfare inside cap | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2024-25 / Income tax | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 0.75 | 0.96 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2024-25 / NICs | -9,398.5 | -11,082.5 | -10,762.0 | 320.5 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.85 | 0.96 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2024-25 / Welfare inside cap | 116.8 | 86.2 | 243.2 | 157.0 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_at_least_2 | computed_in_both | 2.08 | 0.96 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2025-26 / Income tax | 259.6 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.97 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2025-26 / NICs | -9,471.7 | -11,685.8 | -11,458.8 | 227.0 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.97 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2025-26 / Welfare inside cap | 153.5 | 94.2 | 268.4 | 174.1 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.09 | 0.97 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2026-27 / Income tax | 318.8 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.97 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2026-27 / NICs | -9,619.3 | -12,070.1 | -11,919.3 | 150.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.97 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2026-27 / Welfare inside cap | 171.9 | 104.7 | 274.9 | 170.2 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.09 | 0.97 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2027-28 / Income tax | 403.9 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.98 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2027-28 / NICs | -9,817.9 | -12,356.2 | -12,255.2 | 101.0 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.98 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2027-28 / Welfare inside cap | 170.0 | 109.3 | 282.4 | 173.0 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.09 | 0.98 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2028-29 / Income tax | 472.4 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.98 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2028-29 / NICs | -10,088.4 | -12,663.9 | -12,566.1 | 97.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.98 |
| spring_budget_2024 | `class_1_employee_nics_main_rate_cut_2pp` | 2028-29 / Welfare inside cap | 179.6 | 109.8 | 308.4 | 198.6 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | computed_in_both | 2.10 | 0.98 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2023-24 / Income tax | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2023-24 / NICs | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2023-24 / Welfare inside cap | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2024-25 / Income tax | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 0.75 | 0.52 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2024-25 / NICs | -666.5 | -1,114.8 | -609.3 | 505.5 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.85 | 0.52 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2024-25 / Welfare inside cap | 8.3 | 12.9 | 36.2 | 23.3 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.08 | 0.52 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2025-26 / Income tax | -13.6 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.52 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2025-26 / NICs | -678.4 | -1,129.9 | -620.9 | 509.0 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.52 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2025-26 / Welfare inside cap | 11.0 | 12.7 | 40.3 | 27.7 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.52 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2026-27 / Income tax | 190.8 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.53 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2026-27 / NICs | -699.5 | -1,167.9 | -654.2 | 513.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.53 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2026-27 / Welfare inside cap | 12.4 | 15.4 | 42.8 | 27.3 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.53 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2027-28 / Income tax | 280.5 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.54 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2027-28 / NICs | -724.0 | -1,215.5 | -695.7 | 519.7 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.54 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2027-28 / Welfare inside cap | 12.4 | 16.2 | 46.3 | 30.1 | same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | computed_in_both | 2.09 | 0.54 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2028-29 / Income tax | 360.1 | 0.0 | 0.0 | 0.0 | pe_zero | pe_zero | computed_in_both | 0.76 | 0.55 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2028-29 / NICs | -764.3 | -1,263.9 | -737.5 | 526.4 | same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.88 | 0.55 |
| spring_budget_2024 | `class_4_self_employed_nics_main_rate_cut_2pp` | 2028-29 / Welfare inside cap | 13.5 | 16.7 | 48.7 | 31.9 | same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | computed_in_both | 2.10 | 0.55 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2023-24 / Income tax | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2023-24 / Welfare inside cap | 0.0 | 0.0 | — | — | both_zero | not_available | base_only | — | — |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2024-25 / Income tax | -222.0 | -1,491.8 | -885.0 | 606.8 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.75 | 0.78 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2024-25 / Welfare inside cap | -319.0 | 0.0 | -273.4 | -273.4 | pe_zero | same_sign_ratio_0.8_to_1.25 | computed_in_both | 0.97 | 0.78 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2025-26 / Income tax | -277.0 | -1,592.8 | -1,037.8 | 555.0 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.83 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2025-26 / Welfare inside cap | -359.0 | 0.0 | -277.8 | -277.8 | pe_zero | same_sign_ratio_0.5_to_0.8 | computed_in_both | 0.97 | 0.83 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2026-27 / Income tax | -250.0 | -1,720.6 | -1,172.3 | 548.4 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.86 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2026-27 / Welfare inside cap | -391.0 | 0.0 | -301.6 | -301.6 | pe_zero | same_sign_ratio_0.5_to_0.8 | computed_in_both | 0.97 | 0.86 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2027-28 / Income tax | -221.0 | -1,844.2 | -1,288.4 | 555.8 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.87 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2027-28 / Welfare inside cap | -426.0 | 0.0 | -321.2 | -321.2 | pe_zero | same_sign_ratio_0.5_to_0.8 | computed_in_both | 0.97 | 0.87 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2028-29 / Income tax | -193.0 | -1,972.0 | -1,371.9 | 600.1 | same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | computed_in_both | 0.76 | 0.88 |
| spring_budget_2024 | `hicbc_threshold_and_taper` | 2028-29 / Welfare inside cap | -465.0 | 0.0 | -366.9 | -366.9 | pe_zero | same_sign_ratio_0.5_to_0.8 | computed_in_both | 0.97 | 0.88 |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2024-25 / Welfare inside cap | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 2.08 | — |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2025-26 / Welfare inside cap | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 2.09 | — |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2026-27 / Welfare inside cap | 760.3 | 264.1 | 746.1 | 482.0 | same_sign_ratio_below_0.5 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 2.09 | 2.82 |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2027-28 / Welfare inside cap | 1,555.7 | 338.6 | 904.9 | 566.4 | same_sign_ratio_below_0.5 | same_sign_ratio_0.5_to_0.8 | computed_in_both | 2.09 | 2.67 |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2028-29 / Welfare inside cap | 2,328.4 | 436.3 | 1,088.2 | 651.9 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 2.10 | 2.49 |
| spring_statement_2025 | `uc_health_element_freeze_and_new_claimant_cut` | 2029-30 / Welfare inside cap | 3,053.5 | 626.6 | 1,354.9 | 728.3 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 2.09 | 2.16 |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2024-25 / Welfare inside cap | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 2.08 | — |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2025-26 / Welfare inside cap | 0.0 | 0.0 | 0.0 | 0.0 | both_zero | both_zero | computed_in_both | 2.09 | — |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2026-27 / Welfare inside cap | -667.4 | -403.7 | -720.9 | -317.2 | same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | computed_in_both | 2.09 | 1.79 |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2027-28 / Welfare inside cap | -938.1 | -409.5 | -731.5 | -322.0 | same_sign_ratio_below_0.5 | same_sign_ratio_0.5_to_0.8 | computed_in_both | 2.09 | 1.79 |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2028-29 / Welfare inside cap | -1,224.4 | -414.3 | -746.1 | -331.8 | same_sign_ratio_below_0.5 | same_sign_ratio_0.5_to_0.8 | computed_in_both | 2.10 | 1.80 |
| spring_statement_2025 | `uc_standard_allowance_above_inflation` | 2029-30 / Welfare inside cap | -1,546.1 | -421.9 | -753.3 | -331.4 | same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | computed_in_both | 2.09 | 1.79 |

## Source rows not computed in any bundle

4418 rows have no PolicyEngine value in any bundle. They are counted here by status and listed in full in `ENGINE_COMPARISON.csv` and `ENGINE_COMPARISON.json`.

| Event | Base status | New status | Rows |
|---|---|---|---:|
| autumn_budget_2024 | not_computed | not_computed | 1100 |
| autumn_statement_2023 | not_computed | not_computed | 880 |
| autumn_statement_2023 | not_computed | outside_bundle_window | 179 |
| spring_budget_2023 | not_computed | not_computed | 668 |
| spring_budget_2023 | not_computed | outside_bundle_window | 337 |
| spring_budget_2024 | not_computed | not_computed | 640 |
| spring_budget_2024 | not_computed | outside_bundle_window | 128 |
| spring_statement_2025 | not_computed | not_computed | 486 |
