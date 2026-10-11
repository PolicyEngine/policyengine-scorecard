# Release diff: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` → `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

Movements of the event replay between two certified releases. Flags are investigation prompts, not verdicts; ratio bins are descriptive.

A numerical flag means the move exceeds max(£1m, 1% of the larger magnitude). Structural, coverage, mapping, support, inertness and construction flags are raised regardless of size. A year supported on one side only is a support flag, not coverage.

## Executions

| Field | Base | Head |
|---|---|---|
| certified_dataset_sha256 | `f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833` | `5ba399ea5ab9a6c7d4e9aaf6c623080beb34d9ad5f330f6244dbad72b8d960b6` |
| data_bundle | `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` | `policyengine-uk-data-1.58.0` |
| policyengine_core_version | `3.27.1` | `3.33.0` |
| policyengine_uk_version | `2.89.2` | `2.125.1` |
| policyengine_version | `5.0.2` | `6.2.6` |
| variant_id | `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` | `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0` |

## Flags by event

| Event | Supported years (base → head) | numerical | structural | coverage | mapping | support | inertness | construction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| autumn_budget_2024 | 2024–2029 → 2024–2029 | 84 | 0 | 0 | 0 | 0 | 0 | 6 |
| autumn_statement_2023 | 2023–2028 → 2024–2028 | 97 | 5 | 0 | 0 | 18 | 0 | 0 |
| spring_budget_2023 | 2023–2027 → 2024–2027 | 24 | 0 | 0 | 0 | 5 | 0 | 0 |
| spring_budget_2024 | 2023–2028 → 2024–2028 | 75 | 10 | 0 | 0 | 11 | 0 | 0 |
| spring_statement_2025 | 2024–2029 → 2024–2029 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | | 304 | 15 | 0 | 0 | 34 | 0 | 6 |

## Flagged movements

Showing 200 of 308 rows with a flag other than support, rows without a numerical change first, then by absolute change. £m, positive = gain to the Exchequer.

| Event | Measure | CY | Level | Key | Base | Head | Change | Flags |
|---|---|---:|---|---|---:|---:|---:|---|
| spring_budget_2023 | pension_annual_allowance_package | 2027 | source_row | obr_pmd_nov2025:10235:fbb8ccda250b78e9 | -6,456.5 | -3,451.1 | 3,005.3 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | measure_year | total | -6,456.5 | -3,451.1 | 3,005.3 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | head | income_tax | -6,456.5 | -3,451.1 | 3,005.3 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | source_row | obr_pmd_nov2025:10234:7fb22cdd33e49932 | -6,040.7 | -3,279.4 | 2,761.3 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | measure_year | total | -6,040.7 | -3,279.4 | 2,761.3 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | head | income_tax | -6,040.7 | -3,279.4 | 2,761.3 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | source_row | obr_pmd_nov2025:11687:f738e039412d9872 | 5,273.8 | 2,678.8 | -2,595.0 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | measure_year | total | 5,273.8 | 2,678.8 | -2,595.0 | numerical, construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | head | capital_gains_tax | 5,273.8 | 2,678.8 | -2,595.0 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | source_row | obr_pmd_nov2025:11686:9ceb140875d859b8 | 5,113.0 | 2,590.3 | -2,522.6 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | measure_year | total | 5,113.0 | 2,590.3 | -2,522.6 | numerical, construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | head | capital_gains_tax | 5,113.0 | 2,590.3 | -2,522.6 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | source_row | obr_pmd_nov2025:11685:440412b0fb8c6e2d | 4,952.4 | 2,502.0 | -2,450.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | measure_year | total | 4,952.4 | 2,502.0 | -2,450.4 | numerical, construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | head | capital_gains_tax | 4,952.4 | 2,502.0 | -2,450.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | source_row | obr_pmd_nov2025:11684:0d39628e9b763f67 | 4,793.6 | 2,414.6 | -2,379.0 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | measure_year | total | 4,793.6 | 2,414.6 | -2,379.0 | numerical, construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | head | capital_gains_tax | 4,793.6 | 2,414.6 | -2,379.0 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | source_row | obr_pmd_nov2025:10233:f9cad5be5ec138c8 | -5,395.1 | -3,047.4 | 2,347.7 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | measure_year | total | -5,395.1 | -3,047.4 | 2,347.7 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | head | income_tax | -5,395.1 | -3,047.4 | 2,347.7 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | source_row | obr_pmd_nov2025:11683:b9096ecd110093bf | 4,655.3 | 2,337.8 | -2,317.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | measure_year | total | 4,655.3 | 2,337.8 | -2,317.5 | numerical, construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | head | capital_gains_tax | 4,655.3 | 2,337.8 | -2,317.5 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2024 | source_row | obr_pmd_nov2025:10232:aa24b205227c35bd | -4,297.5 | -2,781.3 | 1,516.2 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2024 | measure_year | total | -4,297.5 | -2,781.3 | 1,516.2 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2024 | head | income_tax | -4,297.5 | -2,781.3 | 1,516.2 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | source_row | obr_pmd_nov2025:11669:1cedd72c387ad84b | -9,404.1 | -8,130.8 | 1,273.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | head | income_tax | -9,404.1 | -8,130.8 | 1,273.3 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2028 | source_row | obr_pmd_nov2025:21634:ff94f5b54b89d1ee | -859.8 | -2,025.5 | -1,165.6 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2028 | measure_year | total | -859.8 | -2,025.5 | -1,165.6 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | measure_year | total | 16,744.7 | 17,902.8 | 1,158.1 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | source_row | obr_pmd_nov2025:21630:bf9643f47e057983 | -584.6 | -1,736.6 | -1,152.0 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | measure_year | total | -584.6 | -1,736.6 | -1,152.0 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2027 | source_row | obr_pmd_nov2025:21633:5ce95c1559b8bc39 | -859.1 | -2,004.7 | -1,145.7 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2027 | measure_year | total | -859.1 | -2,004.7 | -1,145.7 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | source_row | obr_pmd_nov2025:11667:35345df3785dfdea | -8,784.0 | -7,662.6 | 1,121.4 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | head | income_tax | -8,784.0 | -7,662.6 | 1,121.4 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | source_row | obr_pmd_nov2025:11668:a076a7d6b3992e7c | -8,988.4 | -7,867.6 | 1,120.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | head | income_tax | -8,988.4 | -7,867.6 | 1,120.9 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2025 | source_row | obr_pmd_nov2025:21631:75b9415771e2e20c | -799.8 | -1,916.1 | -1,116.3 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2025 | measure_year | total | -799.8 | -1,916.1 | -1,116.3 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2026 | source_row | obr_pmd_nov2025:21632:353c5d3f922bfc89 | -833.7 | -1,946.3 | -1,112.6 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2026 | measure_year | total | -833.7 | -1,946.3 | -1,112.6 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2028 | head | universal_credit | -773.2 | -1,843.0 | -1,069.8 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2027 | head | universal_credit | -775.5 | -1,828.4 | -1,052.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -8,507.7 | -7,456.0 | 1,051.7 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | head | income_tax | -8,507.7 | -7,456.0 | 1,051.7 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2024 | head | universal_credit | -549.0 | -1,594.4 | -1,045.3 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2025 | head | universal_credit | -725.2 | -1,759.5 | -1,034.3 | numerical |
| autumn_statement_2023 | lha_reset_to_30th_percentile | 2026 | head | universal_credit | -754.6 | -1,783.0 | -1,028.4 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | source_row | obr_pmd_nov2025:11665:72598886f546ef8c | -8,163.5 | -7,167.0 | 996.5 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | head | income_tax | -8,163.5 | -7,167.0 | 996.5 | numerical |
| autumn_statement_2023 | class_2_self_employed_nics_abolition | 2027 | measure_year | total | -1,326.9 | -421.2 | 905.7 | numerical |
| autumn_statement_2023 | class_2_self_employed_nics_abolition | 2027 | source_row | obr_pmd_nov2025:10600:d0828a5bfb537ca4 | -1,338.8 | -461.7 | 877.2 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | measure_year | total | 16,422.5 | 17,298.2 | 875.7 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | measure_year | total | 16,629.9 | 17,485.9 | 856.0 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | measure_year | total | 16,246.7 | 17,077.9 | 831.2 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | source_row | obr_pmd_nov2025:11620:5446e6157f4ef4ec | 1,354.9 | 2,176.6 | 821.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | measure_year | total | 1,354.9 | 2,176.6 | 821.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | head | private_school_vat | 1,354.9 | 2,176.6 | 821.8 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | measure_year | total | 16,011.3 | 16,827.1 | 815.8 | numerical |
| autumn_statement_2023 | class_2_self_employed_nics_abolition | 2027 | head | ni_class_4 | -786.8 | 0.0 | 786.8 | numerical, structural |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | source_row | obr_pmd_nov2025:11621:8bf103a18fecf781 | 1,388.0 | 2,166.5 | 778.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | measure_year | total | 1,388.0 | 2,166.5 | 778.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | head | private_school_vat | 1,388.0 | 2,166.5 | 778.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2027 | source_row | obr_pmd_nov2025:11619:8726edda9aa7b020 | 1,323.0 | 2,065.8 | 742.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2027 | measure_year | total | 1,323.0 | 2,065.8 | 742.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2027 | head | private_school_vat | 1,323.0 | 2,065.8 | 742.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,292.3 | 2,022.8 | 730.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | measure_year | total | 1,292.3 | 2,022.8 | 730.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | head | private_school_vat | 1,292.3 | 2,022.8 | 730.5 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2029 | source_row | obr_pmd_nov2025:23320:4c41d84635ed82ad | 626.6 | 1,354.9 | 728.3 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2029 | measure_year | total | 626.6 | 1,354.9 | 728.3 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2029 | head | universal_credit | 626.6 | 1,354.9 | 728.3 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | source_row | obr_pmd_nov2025:11617:414a87b10621e433 | 1,258.4 | 1,972.7 | 714.3 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | measure_year | total | 1,258.4 | 1,972.7 | 714.3 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | head | private_school_vat | 1,258.4 | 1,972.7 | 714.3 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2028 | source_row | obr_pmd_nov2025:23319:c6ce8500db20415e | 436.3 | 1,088.2 | 651.9 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2028 | measure_year | total | 436.3 | 1,088.2 | 651.9 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2028 | head | universal_credit | 436.3 | 1,088.2 | 651.9 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | source_row | obr_pmd_nov2025:10987:0f254c98c34bc660 | -1,491.8 | -885.0 | 606.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | head | income_tax | -1,491.8 | -885.0 | 606.8 | numerical |
| autumn_statement_2023 | class_2_self_employed_nics_abolition | 2028 | measure_year | total | -1,042.6 | -436.4 | 606.2 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | source_row | obr_pmd_nov2025:10991:11a476b01436c0db | -1,972.0 | -1,371.9 | 600.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | head | income_tax | -1,972.0 | -1,371.9 | 600.1 | numerical |
| autumn_statement_2023 | class_2_self_employed_nics_abolition | 2028 | source_row | obr_pmd_nov2025:10601:756ded1466aa84b3 | -1,054.6 | -477.6 | 577.0 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2027 | source_row | obr_pmd_nov2025:23318:dcc529f309fec572 | 338.6 | 904.9 | 566.4 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2027 | measure_year | total | 338.6 | 904.9 | 566.4 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2027 | head | universal_credit | 338.6 | 904.9 | 566.4 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2028 | measure_year | total | -1,247.2 | -688.8 | 558.4 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,844.2 | -1,288.4 | 555.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | head | income_tax | -1,844.2 | -1,288.4 | 555.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -1,592.8 | -1,037.8 | 555.0 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | head | income_tax | -1,592.8 | -1,037.8 | 555.0 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2027 | measure_year | total | -1,199.2 | -649.4 | 549.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,720.6 | -1,172.3 | 548.4 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | head | income_tax | -1,720.6 | -1,172.3 | 548.4 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2026 | measure_year | total | -1,152.5 | -611.5 | 541.0 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2025 | measure_year | total | -1,117.2 | -580.6 | 536.6 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2024 | measure_year | total | -1,101.8 | -573.0 | 528.8 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2028 | source_row | obr_pmd_nov2025:10979:3e84f55a7dc5bd63 | -1,263.9 | -737.5 | 526.4 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2028 | head | ni_class_4 | -1,263.9 | -737.5 | 526.4 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2027 | source_row | obr_pmd_nov2025:10978:58862ededbda2b44 | -1,215.5 | -695.7 | 519.7 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2027 | head | ni_class_4 | -1,215.5 | -695.7 | 519.7 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2026 | source_row | obr_pmd_nov2025:10977:57eced9fbf6bab3b | -1,167.9 | -654.2 | 513.7 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2026 | head | ni_class_4 | -1,167.9 | -654.2 | 513.7 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2025 | source_row | obr_pmd_nov2025:10976:230199453880fc45 | -1,129.9 | -620.9 | 509.0 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2025 | head | ni_class_4 | -1,129.9 | -620.9 | 509.0 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2024 | source_row | obr_pmd_nov2025:10975:497e18b9ba827fa3 | -1,114.8 | -609.3 | 505.5 | numerical |
| spring_budget_2024 | class_4_self_employed_nics_main_rate_cut_2pp | 2024 | head | ni_class_4 | -1,114.8 | -609.3 | 505.5 | numerical |
| autumn_statement_2023 | class_2_self_employed_nics_abolition | 2028 | head | ni_class_4 | -495.9 | 0.0 | 495.9 | numerical, structural |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2026 | source_row | obr_pmd_nov2025:23317:1b983354102bb14d | 264.1 | 746.1 | 482.0 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2026 | measure_year | total | 264.1 | 746.1 | 482.0 | numerical |
| spring_statement_2025 | uc_health_element_freeze_and_new_claimant_cut | 2026 | head | universal_credit | 264.1 | 746.1 | 482.0 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | measure_year | total | -10,996.3 | -10,518.8 | 477.5 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | measure_year | total | -10,996.3 | -10,518.8 | 477.5 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | measure_year | total | -11,591.5 | -11,190.4 | 401.1 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | measure_year | total | -11,591.5 | -11,190.4 | 401.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | source_row | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 | 0.0 | -366.9 | -366.9 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | head | child_benefit | -0.0 | -366.9 | -366.9 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | measure_year | total | -1,491.8 | -1,158.4 | 333.4 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | source_row | obr_pmd_nov2025:23337:31f0f1693e3bba3c | -414.3 | -746.1 | -331.8 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | measure_year | total | -414.3 | -746.1 | -331.8 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | head | universal_credit | -414.3 | -746.1 | -331.8 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | source_row | obr_pmd_nov2025:23338:27e34c93a163b4f0 | -421.9 | -753.3 | -331.4 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | measure_year | total | -421.9 | -753.3 | -331.4 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | head | universal_credit | -421.9 | -753.3 | -331.4 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | source_row | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 | -409.5 | -731.5 | -322.0 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | measure_year | total | -409.5 | -731.5 | -322.0 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | head | universal_credit | -409.5 | -731.5 | -322.0 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | head | ni_class_1_employee | -11,086.5 | -10,764.5 | 322.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | head | ni_class_1_employee | -11,086.5 | -10,764.5 | 322.0 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | source_row | obr_pmd_nov2025:22209:71f606ed0f936afe | 0.0 | -321.2 | -321.2 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | head | child_benefit | -0.0 | -321.2 | -321.2 | numerical, structural |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2026 | measure_year | total | -11,965.4 | -11,644.5 | 320.9 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2026 | measure_year | total | -11,965.4 | -11,644.5 | 320.9 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | source_row | obr_pmd_nov2025:10549:7322b894d39fa3ec | -11,082.5 | -10,762.0 | 320.5 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | source_row | obr_pmd_nov2025:10957:34718787787f7089 | -11,082.5 | -10,762.0 | 320.5 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2026 | source_row | obr_pmd_nov2025:23335:7e9f9d66b5194ff6 | -403.7 | -720.9 | -317.2 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2026 | measure_year | total | -403.7 | -720.9 | -317.2 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2026 | head | universal_credit | -403.7 | -720.9 | -317.2 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | 0.0 | -301.6 | -301.6 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | head | child_benefit | -0.0 | -301.6 | -301.6 | numerical, structural |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | measure_year | total | -12,554.1 | -12,257.7 | 296.4 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | measure_year | total | -12,554.1 | -12,257.7 | 296.4 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2028 | measure_year | total | -623.0 | -343.8 | 279.2 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | 0.0 | -277.8 | -277.8 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | head | child_benefit | -0.0 | -277.8 | -277.8 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | measure_year | total | -1,592.8 | -1,315.5 | 277.2 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2027 | measure_year | total | -598.9 | -324.8 | 274.1 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2027 | measure_year | total | -12,246.8 | -11,972.8 | 274.1 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2027 | measure_year | total | -12,246.8 | -11,972.8 | 274.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | source_row | obr_pmd_nov2025:22206:49a0caec037600d2 | 0.0 | -273.4 | -273.4 | numerical, structural |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | head | child_benefit | -0.0 | -273.4 | -273.4 | numerical, structural |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2026 | measure_year | total | -575.8 | -305.8 | 270.0 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2025 | measure_year | total | -558.3 | -290.5 | 267.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | source_row | obr_pmd_nov2025:11674:6dd4d473c559cbea | 25,618.3 | 25,353.4 | -264.9 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2024 | measure_year | total | -550.7 | -286.8 | 263.9 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2028 | source_row | obr_pmd_nov2025:10577:55cd081c955ca847 | -631.3 | -368.0 | 263.2 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2028 | head | ni_class_4 | -631.3 | -368.0 | 263.2 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2027 | source_row | obr_pmd_nov2025:10576:033898ebb4865f78 | -607.0 | -347.6 | 259.4 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2027 | head | ni_class_4 | -607.0 | -347.6 | 259.4 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2026 | source_row | obr_pmd_nov2025:10575:e617707f9625fbba | -583.5 | -327.2 | 256.3 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2026 | head | ni_class_4 | -583.5 | -327.2 | 256.3 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2025 | source_row | obr_pmd_nov2025:10574:46d6b72964d38975 | -564.7 | -310.6 | 254.1 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2025 | head | ni_class_4 | -564.7 | -310.6 | 254.1 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2024 | source_row | obr_pmd_nov2025:10573:22a57b73322dcf42 | -557.2 | -304.8 | 252.3 | numerical |
| autumn_statement_2023 | class_4_self_employed_nics_main_rate_cut_1p | 2024 | head | ni_class_4 | -557.2 | -304.8 | 252.3 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | measure_year | total | -1,720.6 | -1,473.9 | 246.7 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2027 | source_row | obr_pmd_nov2025:20836:76beca3818ed1fe1 | -2.1 | -241.9 | -239.8 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2027 | measure_year | total | -2.1 | -241.9 | -239.8 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2027 | head | universal_credit | -2.1 | -241.9 | -239.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | measure_year | total | -1,844.2 | -1,609.7 | 234.5 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | measure_year | total | -1,972.0 | -1,738.8 | 233.2 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2026 | source_row | obr_pmd_nov2025:20835:1e730fccbdf4c015 | -1.9 | -232.6 | -230.7 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2026 | measure_year | total | -1.9 | -232.6 | -230.7 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2026 | head | universal_credit | -1.9 | -232.6 | -230.7 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | head | ni_class_1_employee | -11,689.4 | -11,461.4 | 228.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | head | ni_class_1_employee | -11,689.4 | -11,461.4 | 228.0 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2025 | source_row | obr_pmd_nov2025:20834:e0b34fcdbf83f61a | -1.7 | -228.9 | -227.1 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2025 | measure_year | total | -1.7 | -228.9 | -227.1 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2025 | head | universal_credit | -1.7 | -228.9 | -227.1 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | source_row | obr_pmd_nov2025:10550:68081ae97974ee1e | -11,685.8 | -11,458.8 | 227.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | source_row | obr_pmd_nov2025:10958:c7a912de7a1a9114 | -11,685.8 | -11,458.8 | 227.0 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2024 | source_row | obr_pmd_nov2025:22853:636080d8aa33dd8e | 1,713.9 | 1,494.9 | -219.0 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2024 | measure_year | total | 1,713.9 | 1,494.9 | -219.0 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2024 | head | winter_fuel_allowance | 1,713.9 | 1,494.9 | -219.0 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2024 | source_row | obr_pmd_nov2025:20833:270c17d92e54dca4 | -1.8 | -218.2 | -216.4 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2024 | measure_year | total | -1.8 | -218.2 | -216.4 | numerical |
| spring_budget_2023 | uc_childcare_cap_increase | 2024 | head | universal_credit | -1.8 | -218.2 | -216.4 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2029 | source_row | obr_pmd_nov2025:22858:6050e74df71edc1c | 453.2 | 241.1 | -212.1 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2029 | measure_year | total | 453.2 | 241.1 | -212.1 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2029 | head | winter_fuel_allowance | 453.2 | 241.1 | -212.1 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | source_row | obr_pmd_nov2025:21466:43674024394e1bc0 | 109.8 | 308.4 | 198.6 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | head | universal_credit | 109.8 | 308.4 | 198.6 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | source_row | obr_pmd_nov2025:22174:b9088212717e5ab4 | 109.8 | 308.4 | 198.6 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | head | universal_credit | 109.8 | 308.4 | 198.6 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2028 | source_row | obr_pmd_nov2025:22857:92bf18d3bd843235 | 417.6 | 226.9 | -190.7 | numerical |
| autumn_budget_2024 | winter_fuel_means_test | 2028 | measure_year | total | 417.6 | 226.9 | -190.7 | numerical |

## Years supported on one side only

These rows have no packet; the population of one release cannot supply the year.

| Event | CY | Level | Rows |
|---|---:|---|---:|
| autumn_statement_2023 | 2023 | measure_year | 4 |
| autumn_statement_2023 | 2023 | source_row | 14 |
| spring_budget_2023 | 2023 | measure_year | 2 |
| spring_budget_2023 | 2023 | source_row | 3 |
| spring_budget_2024 | 2023 | measure_year | 3 |
| spring_budget_2024 | 2023 | source_row | 8 |

## PE/OBR ratio-bin transitions (source rows on both sides)

### autumn_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1101 |
| opposite_sign | opposite_sign | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 5 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | 5 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 13 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 5 |

### autumn_statement_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| both_zero | not_available | 7 |
| not_available | not_available | 1059 |
| pe_zero | pe_zero | 13 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | 9 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_at_least_2 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | 2 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 9 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 3 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | 7 |
| same_sign_ratio_at_least_2 | same_sign_ratio_1.25_to_2 | 2 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 1 |

### spring_budget_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| not_available | not_available | 1005 |
| pe_zero | not_available | 1 |
| pe_zero | pe_zero | 4 |
| same_sign_ratio_at_least_2 | not_available | 1 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 4 |
| same_sign_ratio_below_0.5 | not_available | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_at_least_2 | 4 |

### spring_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| both_zero | not_available | 8 |
| not_available | not_available | 768 |
| pe_zero | pe_zero | 8 |
| pe_zero | same_sign_ratio_0.5_to_0.8 | 4 |
| pe_zero | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | 4 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_at_least_2 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | 3 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 8 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | 2 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 5 |

### spring_statement_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 4 |
| not_available | not_available | 486 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_0.5_to_0.8 | 3 |
| same_sign_ratio_below_0.5 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 3 |

## Investigation packets

* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029.md)
* [autumn_budget_2024__employer_nics_package__2025](packets/autumn_budget_2024__employer_nics_package__2025.md)
* [autumn_budget_2024__employer_nics_package__2026](packets/autumn_budget_2024__employer_nics_package__2026.md)
* [autumn_budget_2024__employer_nics_package__2027](packets/autumn_budget_2024__employer_nics_package__2027.md)
* [autumn_budget_2024__employer_nics_package__2028](packets/autumn_budget_2024__employer_nics_package__2028.md)
* [autumn_budget_2024__employer_nics_package__2029](packets/autumn_budget_2024__employer_nics_package__2029.md)
* [autumn_budget_2024__private_school_vat_20pct__2025](packets/autumn_budget_2024__private_school_vat_20pct__2025.md)
* [autumn_budget_2024__private_school_vat_20pct__2026](packets/autumn_budget_2024__private_school_vat_20pct__2026.md)
* [autumn_budget_2024__private_school_vat_20pct__2027](packets/autumn_budget_2024__private_school_vat_20pct__2027.md)
* [autumn_budget_2024__private_school_vat_20pct__2028](packets/autumn_budget_2024__private_school_vat_20pct__2028.md)
* [autumn_budget_2024__private_school_vat_20pct__2029](packets/autumn_budget_2024__private_school_vat_20pct__2029.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2025](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2025.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2026](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2026.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2027](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2027.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2028](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2028.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2029](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2029.md)
* [autumn_budget_2024__winter_fuel_means_test__2024](packets/autumn_budget_2024__winter_fuel_means_test__2024.md)
* [autumn_budget_2024__winter_fuel_means_test__2025](packets/autumn_budget_2024__winter_fuel_means_test__2025.md)
* [autumn_budget_2024__winter_fuel_means_test__2026](packets/autumn_budget_2024__winter_fuel_means_test__2026.md)
* [autumn_budget_2024__winter_fuel_means_test__2027](packets/autumn_budget_2024__winter_fuel_means_test__2027.md)
* [autumn_budget_2024__winter_fuel_means_test__2028](packets/autumn_budget_2024__winter_fuel_means_test__2028.md)
* [autumn_budget_2024__winter_fuel_means_test__2029](packets/autumn_budget_2024__winter_fuel_means_test__2029.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2024](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2024.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2025](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2025.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2026](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2026.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2027](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2027.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2028](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2028.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2024](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2024.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2025](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2025.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2026](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2026.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2027](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2027.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2028](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2028.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2024](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2024.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2025](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2025.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2026](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2026.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2027](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2027.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2028](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2028.md)
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
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2024](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2024.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2025](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2025.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2026](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2026.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2027](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2027.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2028](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2028.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2024](packets/spring_budget_2024__hicbc_threshold_and_taper__2024.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2025](packets/spring_budget_2024__hicbc_threshold_and_taper__2025.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2026](packets/spring_budget_2024__hicbc_threshold_and_taper__2026.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2027](packets/spring_budget_2024__hicbc_threshold_and_taper__2027.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2028](packets/spring_budget_2024__hicbc_threshold_and_taper__2028.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2026](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2026.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2027](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2027.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2028](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2028.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2026](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2026.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2027](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2027.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2028](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2028.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2029](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2029.md)
