# Release diff: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1` → `pe6.7.6_uk2.138.0_policyengine-uk-data-1.58.2`

Movements of the event replay between two certified releases. Flags are investigation prompts, not verdicts; ratio bins are descriptive.

A numerical flag means the move exceeds max(£1m, 1% of the larger magnitude). Structural, coverage, mapping, support, inertness and construction flags are raised regardless of size. A year supported on one side only is a support flag, not coverage.

## Executions

| Field | Base | Head |
|---|---|---|
| certified_dataset_sha256 | `056e80fd8e9151d78f432a25cde863340baee81304c6216a37fb575ce8563784` | `40804ba2540458cb6f3c476d29d3bb4bc88d9ac6b401fa285ed6e4232a55aa52` |
| data_bundle | `policyengine-uk-data-1.58.1` | `policyengine-uk-data-1.58.2` |
| policyengine_core_version | `3.33.0` | `3.33.0` |
| policyengine_uk_version | `2.130.1` | `2.138.0` |
| policyengine_version | `6.5.0` | `6.7.6` |
| variant_id | `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1` | `pe6.7.6_uk2.138.0_policyengine-uk-data-1.58.2` |

Construction premises compared: base `cb587ba5f065d00e191bf3c51883bf07a9c101b59b5a6419c1a3760c3170857e`, head `90ea536c4c3fff272b6c1662761e02c4631302dfd9dd5502b00ee80ad7dbb215`.

## Flags by event

| Event | Supported years (base → head) | numerical | structural | coverage | mapping | support | inertness | construction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| autumn_budget_2024 | 2024–2029 → 2024–2029 | 60 | 10 | 0 | 0 | 0 | 10 | 0 |
| autumn_budget_2025 | 2025–2030 → 2025–2030 | 38 | 4 | 0 | 0 | 0 | 0 | 0 |
| autumn_statement_2023 | 2024–2028 → 2024–2028 | 28 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_budget_2023 | 2024–2027 → 2024–2027 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_budget_2024 | 2024–2028 → 2024–2028 | 33 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_statement_2025 | 2024–2029 → 2024–2029 | 21 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | | 204 | 14 | 0 | 0 | 0 | 10 | 0 |

## Flagged movements

Showing 200 of 209 rows with a flag other than support, rows without a numerical change first, then by absolute change. £m, positive = gain to the Exchequer.

| Event | Measure | CY | Level | Key | Base | Head | Change | Flags |
|---|---|---:|---|---|---:|---:|---:|---|
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2025 | source_row | obr_pmd_nov2025:11647:b269082735adb83b | 2,182.3 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2026 | source_row | obr_pmd_nov2025:11648:48bd77ddd06dec27 | 2,254.5 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2027 | source_row | obr_pmd_nov2025:11649:910077d14a180f90 | 2,336.0 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2028 | source_row | obr_pmd_nov2025:11650:068acce8b0873200 | 2,418.1 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2029 | source_row | obr_pmd_nov2025:11651:9a7327566a66890c | 2,500.6 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2029 | measure_year | total | 2,500.6 | 0.0 | -2,500.6 | numerical, structural, inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2029 | head | stamp_duty_land_tax | 2,500.6 | 0.0 | -2,500.6 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2028 | measure_year | total | 2,418.1 | 0.0 | -2,418.1 | numerical, structural, inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2028 | head | stamp_duty_land_tax | 2,418.1 | 0.0 | -2,418.1 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2027 | measure_year | total | 2,336.0 | 0.0 | -2,336.0 | numerical, structural, inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2027 | head | stamp_duty_land_tax | 2,336.0 | 0.0 | -2,336.0 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2026 | measure_year | total | 2,254.5 | 0.0 | -2,254.5 | numerical, structural, inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2026 | head | stamp_duty_land_tax | 2,254.5 | 0.0 | -2,254.5 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2025 | measure_year | total | 2,182.3 | 0.0 | -2,182.3 | numerical, structural, inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2025 | head | stamp_duty_land_tax | 2,182.3 | 0.0 | -2,182.3 | numerical, structural |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | measure_year | total | 2,342.3 | 1,413.4 | -928.9 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | source_row | obr_pmd_nov2025:12341:ce174c39c117892d | 213.1 | -711.1 | -924.2 | numerical, structural |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | head | income_tax | 213.1 | -711.1 | -924.2 | numerical, structural |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | measure_year | total | 2,250.5 | 1,448.0 | -802.5 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | source_row | obr_pmd_nov2025:12340:56a6872c6215ff54 | 119.2 | -681.4 | -800.6 | numerical, structural |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | head | income_tax | 119.2 | -681.4 | -800.6 | numerical, structural |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | source_row | obr_pmd_nov2025:11687:f738e039412d9872 | 2,660.3 | 1,995.5 | -664.8 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | measure_year | total | 2,660.3 | 1,995.5 | -664.8 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | head | capital_gains_tax | 2,660.3 | 1,995.5 | -664.8 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | source_row | obr_pmd_nov2025:11686:9ceb140875d859b8 | 2,572.4 | 1,930.5 | -641.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | measure_year | total | 2,572.4 | 1,930.5 | -641.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | head | capital_gains_tax | 2,572.4 | 1,930.5 | -641.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | source_row | obr_pmd_nov2025:11685:440412b0fb8c6e2d | 2,484.7 | 1,865.6 | -619.1 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | measure_year | total | 2,484.7 | 1,865.6 | -619.1 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | head | capital_gains_tax | 2,484.7 | 1,865.6 | -619.1 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | source_row | obr_pmd_nov2025:23338:27e34c93a163b4f0 | -753.2 | -1,362.8 | -609.6 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | measure_year | total | -753.2 | -1,362.8 | -609.6 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | head | universal_credit | -753.2 | -1,362.8 | -609.6 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | source_row | obr_pmd_nov2025:10235:fbb8ccda250b78e9 | -3,725.2 | -3,120.6 | 604.6 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | measure_year | total | -3,725.2 | -3,120.6 | 604.6 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | head | income_tax | -3,725.2 | -3,120.6 | 604.6 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | source_row | obr_pmd_nov2025:11684:0d39628e9b763f67 | 2,397.9 | 1,801.5 | -596.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | measure_year | total | 2,397.9 | 1,801.5 | -596.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | head | capital_gains_tax | 2,397.9 | 1,801.5 | -596.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | source_row | obr_pmd_nov2025:11683:b9096ecd110093bf | 2,321.6 | 1,745.1 | -576.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | measure_year | total | 2,321.6 | 1,745.1 | -576.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | head | capital_gains_tax | 2,321.6 | 1,745.1 | -576.5 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | source_row | obr_pmd_nov2025:10234:7fb22cdd33e49932 | -3,540.3 | -2,981.5 | 558.8 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | measure_year | total | -3,540.3 | -2,981.5 | 558.8 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | head | income_tax | -3,540.3 | -2,981.5 | 558.8 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | source_row | obr_pmd_nov2025:23337:31f0f1693e3bba3c | -746.6 | -1,152.7 | -406.1 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | measure_year | total | -746.6 | -1,152.7 | -406.1 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | head | universal_credit | -746.6 | -1,152.7 | -406.1 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | source_row | obr_pmd_nov2025:10233:f9cad5be5ec138c8 | -3,300.7 | -2,938.9 | 361.8 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | measure_year | total | -3,300.7 | -2,938.9 | 361.8 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | head | income_tax | -3,300.7 | -2,938.9 | 361.8 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | source_row | obr_pmd_nov2025:11682:73295721bdfdb9e8 | 956.3 | 726.8 | -229.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | measure_year | total | 956.3 | 726.8 | -229.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | head | capital_gains_tax | 956.3 | 726.8 | -229.5 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | measure_year | total | -1,757.8 | -1,560.0 | 197.7 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | source_row | obr_pmd_nov2025:10991:11a476b01436c0db | -1,394.7 | -1,200.1 | 194.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | head | income_tax | -1,394.7 | -1,200.1 | 194.6 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | source_row | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 | -732.7 | -924.4 | -191.7 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | measure_year | total | -732.7 | -924.4 | -191.7 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | head | universal_credit | -732.7 | -924.4 | -191.7 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | measure_year | total | 17,319.6 | 17,501.4 | 181.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | measure_year | total | -1,598.2 | -1,435.8 | 162.4 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,274.7 | -1,118.0 | 156.7 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | head | income_tax | -1,274.7 | -1,118.0 | 156.7 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,131.6 | -976.0 | 155.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | head | income_tax | -1,131.6 | -976.0 | 155.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | source_row | obr_pmd_nov2025:22206:49a0caec037600d2 | -336.2 | -181.1 | 155.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | head | child_benefit | -336.2 | -181.1 | 155.1 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | source_row | obr_pmd_nov2025:11668:a076a7d6b3992e7c | -7,898.2 | -7,757.0 | 141.2 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | head | income_tax | -7,898.2 | -7,757.0 | 141.2 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2024 | source_row | obr_pmd_nov2025:10232:aa24b205227c35bd | -3,004.4 | -2,863.3 | 141.1 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2024 | measure_year | total | -3,004.4 | -2,863.3 | 141.1 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2024 | head | income_tax | -3,004.4 | -2,863.3 | 141.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | measure_year | total | -1,439.4 | -1,320.8 | 118.6 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | source_row | obr_pmd_nov2025:11669:1cedd72c387ad84b | -8,092.9 | -7,984.2 | 108.6 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | head | income_tax | -8,092.9 | -7,984.2 | 108.6 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | source_row | obr_pmd_nov2025:11620:5446e6157f4ef4ec | 2,138.1 | 2,034.1 | -104.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | measure_year | total | 2,138.1 | 2,034.1 | -104.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | head | private_school_vat | 2,138.1 | 2,034.1 | -104.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | source_row | obr_pmd_nov2025:11617:414a87b10621e433 | 1,940.3 | 1,844.3 | -96.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | measure_year | total | 1,940.3 | 1,844.3 | -96.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | head | private_school_vat | 1,940.3 | 1,844.3 | -96.0 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -980.5 | -892.6 | 87.9 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | head | income_tax | -980.5 | -892.6 | 87.9 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2029 | measure_year | total | 7,928.6 | 7,846.0 | -82.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | source_row | obr_pmd_nov2025:11621:8bf103a18fecf781 | 2,163.0 | 2,081.3 | -81.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | measure_year | total | 2,163.0 | 2,081.3 | -81.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | head | private_school_vat | 2,163.0 | 2,081.3 | -81.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | source_row | obr_pmd_nov2025:10987:0f254c98c34bc660 | -779.6 | -861.2 | -81.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | head | income_tax | -779.6 | -861.2 | -81.6 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2030 | source_row | obr_pmd_nov2025:23530:d1bc796d9f235c4f | -3,488.2 | -3,562.3 | -74.1 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2030 | measure_year | total | -3,488.2 | -3,562.3 | -74.1 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2030 | head | universal_credit | -3,488.2 | -3,562.3 | -74.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | measure_year | total | -1,115.8 | -1,042.2 | 73.6 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2026 | source_row | obr_pmd_nov2025:23526:7a52217d035becaf | -2,694.6 | -2,765.4 | -70.8 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2026 | measure_year | total | -2,694.6 | -2,765.4 | -70.8 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2026 | head | universal_credit | -2,694.6 | -2,765.4 | -70.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | measure_year | total | -1,263.0 | -1,195.5 | 67.4 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | source_row | obr_pmd_nov2025:21630:bf9643f47e057983 | -1,687.1 | -1,747.7 | -60.6 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | measure_year | total | -1,687.1 | -1,747.7 | -60.6 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | head | universal_credit | -1,554.9 | -1,611.2 | -56.4 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2028 | source_row | obr_pmd_nov2025:23528:35553a766a3ad3d3 | -3,154.8 | -3,203.9 | -49.1 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2028 | measure_year | total | -3,154.8 | -3,203.9 | -49.1 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2028 | head | universal_credit | -3,154.8 | -3,203.9 | -49.1 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2025 | source_row | obr_pmd_nov2025:21631:75b9415771e2e20c | -1,883.1 | -1,929.1 | -46.0 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2025 | measure_year | total | -1,883.1 | -1,929.1 | -46.0 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2026 | source_row | obr_pmd_nov2025:21632:353c5d3f922bfc89 | -1,917.2 | -1,961.7 | -44.5 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2026 | measure_year | total | -1,917.2 | -1,961.7 | -44.5 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2025 | head | universal_credit | -1,738.0 | -1,781.9 | -43.9 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2026 | head | universal_credit | -1,767.2 | -1,810.4 | -43.1 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2029 | source_row | obr_pmd_nov2025:23529:1e1a237caba88918 | -3,259.2 | -3,298.6 | -39.4 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2029 | measure_year | total | -3,259.2 | -3,298.6 | -39.4 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2029 | head | universal_credit | -3,259.2 | -3,298.6 | -39.4 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2027 | head | universal_credit | -1,815.6 | -1,854.2 | -38.6 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2027 | source_row | obr_pmd_nov2025:21633:5ce95c1559b8bc39 | -1,979.1 | -2,016.2 | -37.1 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2027 | measure_year | total | -1,979.1 | -2,016.2 | -37.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | -307.8 | -344.8 | -37.0 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | head | child_benefit | -307.8 | -344.8 | -37.0 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2028 | head | universal_credit | -1,831.0 | -1,864.5 | -33.5 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2028 | source_row | obr_pmd_nov2025:21634:ff94f5b54b89d1ee | -2,000.2 | -2,031.5 | -31.4 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2028 | measure_year | total | -2,000.2 | -2,031.5 | -31.4 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,966.5 | 1,937.7 | -28.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | measure_year | total | 1,966.5 | 1,937.7 | -28.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | head | private_school_vat | 1,966.5 | 1,937.7 | -28.8 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2027 | source_row | obr_pmd_nov2025:23318:dcc529f309fec572 | 893.6 | 866.1 | -27.5 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2027 | measure_year | total | 893.6 | 866.1 | -27.5 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2027 | head | universal_credit | 893.6 | 866.1 | -27.5 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2029 | source_row | obr_pmd_nov2025:23320:4c41d84635ed82ad | 1,297.2 | 1,270.2 | -27.0 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2029 | measure_year | total | 1,297.2 | 1,270.2 | -27.0 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2029 | head | universal_credit | 1,297.2 | 1,270.2 | -27.0 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2030 | source_row | obr_pmd_nov2025:12377:ca5b9686e623d09c | 507.9 | 481.2 | -26.8 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2030 | measure_year | total | 507.9 | 481.2 | -26.8 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2030 | head | high_value_council_tax_surcharge | 507.9 | 481.2 | -26.8 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2026 | source_row | obr_pmd_nov2025:23317:1b983354102bb14d | 743.2 | 716.7 | -26.4 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2026 | measure_year | total | 743.2 | 716.7 | -26.4 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2026 | head | universal_credit | 743.2 | 716.7 | -26.4 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2028 | source_row | obr_pmd_nov2025:23319:c6ce8500db20415e | 1,053.0 | 1,026.8 | -26.3 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2028 | measure_year | total | 1,053.0 | 1,026.8 | -26.3 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2028 | head | universal_credit | 1,053.0 | 1,026.8 | -26.3 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2029 | source_row | obr_pmd_nov2025:12376:d658edd74795036b | 495.7 | 469.6 | -26.1 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2029 | measure_year | total | 495.7 | 469.6 | -26.1 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2029 | head | high_value_council_tax_surcharge | 495.7 | 469.6 | -26.1 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2028 | source_row | obr_pmd_nov2025:12375:297fca1f0cf23095 | 483.9 | 458.4 | -25.5 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2028 | measure_year | total | 483.9 | 458.4 | -25.5 | numerical |
| autumn_budget_2025 | ab2025__high_value_council_tax_surcharge | 2028 | head | high_value_council_tax_surcharge | 483.9 | 458.4 | -25.5 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | -282.5 | -303.0 | -20.4 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | head | child_benefit | -282.5 | -303.0 | -20.4 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2030 | source_row | obr_pmd_nov2025:23920:07fdfe7c4df486ae | -225.5 | -233.2 | -7.7 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2030 | head | universal_credit | -225.5 | -233.2 | -7.7 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | head | ni_class_1_employee | 260.9 | 253.6 | -7.3 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | source_row | obr_pmd_nov2025:21466:43674024394e1bc0 | 303.4 | 309.4 | 5.9 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | head | universal_credit | 303.4 | 309.4 | 5.9 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | source_row | obr_pmd_nov2025:22174:b9088212717e5ab4 | 303.4 | 309.4 | 5.9 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | head | universal_credit | 303.4 | 309.4 | 5.9 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2026 | source_row | obr_pmd_nov2025:20835:1e730fccbdf4c015 | -255.2 | -249.4 | 5.8 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2026 | measure_year | total | -255.2 | -249.4 | 5.8 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2026 | head | universal_credit | -255.2 | -249.4 | 5.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | source_row | obr_pmd_nov2025:22209:71f606ed0f936afe | -323.6 | -317.9 | 5.7 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | head | child_benefit | -323.6 | -317.9 | 5.7 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2024 | source_row | obr_pmd_nov2025:20833:270c17d92e54dca4 | -239.0 | -233.5 | 5.6 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2024 | measure_year | total | -239.0 | -233.5 | 5.6 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2024 | head | universal_credit | -239.0 | -233.5 | 5.6 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2026 | source_row | obr_pmd_nov2025:22855:dbc5baf2a54734dc | 184.7 | 190.2 | 5.5 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2026 | measure_year | total | 184.7 | 190.2 | 5.5 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2026 | head | winter_fuel_allowance | 184.7 | 190.2 | 5.5 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2025 | source_row | obr_pmd_nov2025:20834:e0b34fcdbf83f61a | -251.7 | -246.2 | 5.5 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2025 | measure_year | total | -251.7 | -246.2 | 5.5 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2025 | head | universal_credit | -251.7 | -246.2 | 5.5 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2027 | source_row | obr_pmd_nov2025:20836:76beca3818ed1fe1 | -266.0 | -260.6 | 5.4 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2027 | measure_year | total | -266.0 | -260.6 | 5.4 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2027 | head | universal_credit | -266.0 | -260.6 | 5.4 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2025 | source_row | obr_pmd_nov2025:22854:edbde987f66af165 | 175.5 | 180.7 | 5.2 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2025 | measure_year | total | 175.5 | 180.7 | 5.2 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2025 | head | winter_fuel_allowance | 175.5 | 180.7 | 5.2 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2028 | source_row | obr_pmd_nov2025:22857:92bf18d3bd843235 | 217.9 | 222.9 | 5.0 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2028 | measure_year | total | 217.9 | 222.9 | 5.0 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2028 | head | winter_fuel_allowance | 217.9 | 222.9 | 5.0 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2027 | source_row | obr_pmd_nov2025:21465:6ea19652f3e3ea6b | 292.4 | 297.2 | 4.8 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2027 | head | universal_credit | 292.4 | 297.2 | 4.8 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2027 | source_row | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 | 292.4 | 297.2 | 4.8 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2027 | head | universal_credit | 292.4 | 297.2 | 4.8 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2026 | source_row | obr_pmd_nov2025:21464:190052623cdf04c0 | 282.0 | 286.6 | 4.6 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2026 | head | universal_credit | 282.0 | 286.6 | 4.6 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2026 | source_row | obr_pmd_nov2025:22172:8c021f0cf80fe71b | 282.0 | 286.6 | 4.6 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2026 | head | universal_credit | 282.0 | 286.6 | 4.6 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | head | ni_class_1_employee | 263.9 | 259.4 | -4.4 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | source_row | obr_pmd_nov2025:21463:fd9bc11d19465ecb | 266.2 | 270.6 | 4.4 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | head | universal_credit | 266.2 | 270.6 | 4.4 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | source_row | obr_pmd_nov2025:22171:93d8943dfe121528 | 266.2 | 270.6 | 4.4 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | head | universal_credit | 266.2 | 270.6 | 4.4 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | source_row | obr_pmd_nov2025:21462:c775903b43caf723 | 241.1 | 245.5 | 4.4 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | head | universal_credit | 241.1 | 245.5 | 4.4 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | source_row | obr_pmd_nov2025:22170:45627d3976bd492a | 241.1 | 245.5 | 4.4 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | head | universal_credit | 241.1 | 245.5 | 4.4 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | head | housing_benefit | -132.2 | -136.5 | -4.3 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2029 | source_row | obr_pmd_nov2025:22858:6050e74df71edc1c | 228.8 | 232.9 | 4.1 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2029 | measure_year | total | 228.8 | 232.9 | 4.1 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2029 | head | winter_fuel_allowance | 228.8 | 232.9 | 4.1 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2027 | source_row | obr_pmd_nov2025:22856:c29981419df6c6f6 | 216.2 | 219.7 | 3.4 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2027 | measure_year | total | 216.2 | 219.7 | 3.4 | numerical |

## Years supported on one side only

Each has a packet; the population of one release cannot supply the year.

| Event | CY | Level | Rows |
|---|---:|---|---:|
| none | | | |

## PE/OBR ratio-bin transitions (source rows on both sides)

### autumn_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1100 |
| obr_zero | obr_zero | 1 |
| opposite_sign | opposite_sign | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 6 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 4 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 1 |
| same_sign_ratio_at_least_2 | not_available | 5 |
| same_sign_ratio_at_least_2 | same_sign_ratio_1.25_to_2 | 1 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 7 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 5 |

### autumn_budget_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 28 |
| not_available | not_available | 1422 |
| obr_zero | obr_zero | 1 |
| opposite_sign | same_sign_ratio_0.8_to_1.25 | 1 |
| pe_zero | pe_zero | 19 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 10 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 16 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 8 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 6 |
| same_sign_ratio_below_0.5 | opposite_sign | 1 |

### autumn_statement_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1066 |
| pe_zero | pe_zero | 13 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 7 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 17 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 11 |

### spring_budget_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| not_available | not_available | 1008 |
| pe_zero | pe_zero | 4 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 8 |

### spring_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 776 |
| pe_zero | pe_zero | 8 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 2 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.5_to_0.8 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 10 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 4 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 11 |

### spring_statement_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 4 |
| not_available | not_available | 486 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 1 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 2 |
| same_sign_ratio_below_0.5 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 2 |

## Investigation packets

* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029.md)
* [autumn_budget_2024__employer_nics_package__2028](packets/autumn_budget_2024__employer_nics_package__2028.md)
* [autumn_budget_2024__employer_nics_package__2029](packets/autumn_budget_2024__employer_nics_package__2029.md)
* [autumn_budget_2024__private_school_vat_20pct__2025](packets/autumn_budget_2024__private_school_vat_20pct__2025.md)
* [autumn_budget_2024__private_school_vat_20pct__2026](packets/autumn_budget_2024__private_school_vat_20pct__2026.md)
* [autumn_budget_2024__private_school_vat_20pct__2028](packets/autumn_budget_2024__private_school_vat_20pct__2028.md)
* [autumn_budget_2024__private_school_vat_20pct__2029](packets/autumn_budget_2024__private_school_vat_20pct__2029.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2025](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2025.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2026](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2026.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2027](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2027.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2028](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2028.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2029](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2029.md)
* [autumn_budget_2024__winter_fuel_means_test__2025](packets/autumn_budget_2024__winter_fuel_means_test__2025.md)
* [autumn_budget_2024__winter_fuel_means_test__2026](packets/autumn_budget_2024__winter_fuel_means_test__2026.md)
* [autumn_budget_2024__winter_fuel_means_test__2027](packets/autumn_budget_2024__winter_fuel_means_test__2027.md)
* [autumn_budget_2024__winter_fuel_means_test__2028](packets/autumn_budget_2024__winter_fuel_means_test__2028.md)
* [autumn_budget_2024__winter_fuel_means_test__2029](packets/autumn_budget_2024__winter_fuel_means_test__2029.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2028](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2028.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2028](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2028.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2029](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2029.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2030](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2030.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2028](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2028.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2029](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2029.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2030](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2030.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2029](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2029.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2030](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2030.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2026](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2026.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2028](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2028.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2029](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2029.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2030](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2030.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2024](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2024.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2025](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2025.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2026](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2026.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2027](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2027.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2028](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2028.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2024](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2024.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2025](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2025.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2026](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2026.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2027](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2027.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2028](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2028.md)
* [spring_budget_2023__pension_annual_allowance_package__2024](packets/spring_budget_2023__pension_annual_allowance_package__2024.md)
* [spring_budget_2023__pension_annual_allowance_package__2025](packets/spring_budget_2023__pension_annual_allowance_package__2025.md)
* [spring_budget_2023__pension_annual_allowance_package__2026](packets/spring_budget_2023__pension_annual_allowance_package__2026.md)
* [spring_budget_2023__pension_annual_allowance_package__2027](packets/spring_budget_2023__pension_annual_allowance_package__2027.md)
* [spring_budget_2023__uc_childcare_cap_increase__2024](packets/spring_budget_2023__uc_childcare_cap_increase__2024.md)
* [spring_budget_2023__uc_childcare_cap_increase__2025](packets/spring_budget_2023__uc_childcare_cap_increase__2025.md)
* [spring_budget_2023__uc_childcare_cap_increase__2026](packets/spring_budget_2023__uc_childcare_cap_increase__2026.md)
* [spring_budget_2023__uc_childcare_cap_increase__2027](packets/spring_budget_2023__uc_childcare_cap_increase__2027.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2024](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2024.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2025](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2025.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2026](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2026.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2027](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2027.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2028](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2028.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2024](packets/spring_budget_2024__hicbc_threshold_and_taper__2024.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2025](packets/spring_budget_2024__hicbc_threshold_and_taper__2025.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2026](packets/spring_budget_2024__hicbc_threshold_and_taper__2026.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2027](packets/spring_budget_2024__hicbc_threshold_and_taper__2027.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2028](packets/spring_budget_2024__hicbc_threshold_and_taper__2028.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2026](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2026.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2027](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2027.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2028](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2028.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2027](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2027.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2028](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2028.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2029](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2029.md)
