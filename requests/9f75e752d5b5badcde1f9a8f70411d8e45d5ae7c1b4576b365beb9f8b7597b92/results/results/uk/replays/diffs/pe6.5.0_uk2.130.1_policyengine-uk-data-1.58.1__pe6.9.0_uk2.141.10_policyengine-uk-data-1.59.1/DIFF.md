# Release diff: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1` → `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

Movements of the event replay between two certified releases. Flags are investigation prompts, not verdicts; ratio bins are descriptive.

A numerical flag means the move exceeds max(£1m, 1% of the larger magnitude). Structural, coverage, mapping, support, inertness and construction flags are raised regardless of size. A year supported on one side only is a support flag, not coverage.

## Executions

| Field | Base | Head |
|---|---|---|
| certified_dataset_sha256 | `056e80fd8e9151d78f432a25cde863340baee81304c6216a37fb575ce8563784` | `e8483bd8453b468212efe7fe064575a60dfec988fb56a066534e0c43b1142367` |
| data_bundle | `policyengine-uk-data-1.58.1` | `policyengine-uk-data-1.59.1` |
| policyengine_core_version | `3.33.0` | `3.33.0` |
| policyengine_uk_version | `2.130.1` | `2.141.10` |
| policyengine_version | `6.5.0` | `6.9.0` |
| variant_id | `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1` | `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1` |

Construction premises compared: base `cb587ba5f065d00e191bf3c51883bf07a9c101b59b5a6419c1a3760c3170857e`, head `45bd1e6cdd0aee9f608e4ef9a886617394fd4dee1eab41dc5721764a074895e7`.

## Flags by event

| Event | Supported years (base → head) | numerical | structural | coverage | mapping | support | inertness | construction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| autumn_budget_2024 | 2024–2029 → 2024–2029 | 91 | 10 | 0 | 0 | 0 | 10 | 6 |
| autumn_budget_2025 | 2025–2030 → 2025–2030 | 113 | 6 | 0 | 0 | 0 | 0 | 0 |
| autumn_statement_2023 | 2024–2028 → 2024–2028 | 81 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_budget_2023 | 2024–2027 → 2024–2027 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_budget_2024 | 2024–2028 → 2024–2028 | 79 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_statement_2025 | 2024–2029 → 2024–2029 | 18 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | | 406 | 16 | 0 | 0 | 0 | 10 | 6 |

## Flagged movements

Showing 200 of 414 rows with a flag other than support, rows without a numerical change first, then by absolute change. £m, positive = gain to the Exchequer.

| Event | Measure | CY | Level | Key | Base | Head | Change | Flags |
|---|---|---:|---|---|---:|---:|---:|---|
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2025 | source_row | obr_pmd_nov2025:11647:b269082735adb83b | 2,182.3 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2026 | source_row | obr_pmd_nov2025:11648:48bd77ddd06dec27 | 2,254.5 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2027 | source_row | obr_pmd_nov2025:11649:910077d14a180f90 | 2,336.0 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2028 | source_row | obr_pmd_nov2025:11650:068acce8b0873200 | 2,418.1 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2029 | source_row | obr_pmd_nov2025:11651:9a7327566a66890c | 2,500.6 | — | — | inertness |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2029 | measure_year | total | 2,500.6 | 0.0 | -2,500.6 | numerical, structural, inertness, construction |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2029 | head | stamp_duty_land_tax | 2,500.6 | 0.0 | -2,500.6 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2028 | measure_year | total | 2,418.1 | 0.0 | -2,418.1 | numerical, structural, inertness, construction |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2028 | head | stamp_duty_land_tax | 2,418.1 | 0.0 | -2,418.1 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2027 | measure_year | total | 2,336.0 | 0.0 | -2,336.0 | numerical, structural, inertness, construction |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2027 | head | stamp_duty_land_tax | 2,336.0 | 0.0 | -2,336.0 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2026 | measure_year | total | 2,254.5 | 0.0 | -2,254.5 | numerical, structural, inertness, construction |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2026 | head | stamp_duty_land_tax | 2,254.5 | 0.0 | -2,254.5 | numerical, structural |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2025 | measure_year | total | 2,182.3 | 0.0 | -2,182.3 | numerical, structural, inertness, construction |
| autumn_budget_2024 | sdlt_additional_dwelling_surcharge_2pp | 2025 | head | stamp_duty_land_tax | 2,182.3 | 0.0 | -2,182.3 | numerical, structural |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | source_row | obr_pmd_nov2025:11687:f738e039412d9872 | 2,660.3 | 3,815.0 | 1,154.7 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | measure_year | total | 2,660.3 | 3,815.0 | 1,154.7 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | head | capital_gains_tax | 2,660.3 | 3,815.0 | 1,154.7 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | source_row | obr_pmd_nov2025:11686:9ceb140875d859b8 | 2,572.4 | 3,693.3 | 1,120.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | measure_year | total | 2,572.4 | 3,693.3 | 1,120.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | head | capital_gains_tax | 2,572.4 | 3,693.3 | 1,120.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | source_row | obr_pmd_nov2025:11685:440412b0fb8c6e2d | 2,484.7 | 3,572.2 | 1,087.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | measure_year | total | 2,484.7 | 3,572.2 | 1,087.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | head | capital_gains_tax | 2,484.7 | 3,572.2 | 1,087.5 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | source_row | obr_pmd_nov2025:11684:0d39628e9b763f67 | 2,397.9 | 3,452.7 | 1,054.8 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | measure_year | total | 2,397.9 | 3,452.7 | 1,054.8 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | head | capital_gains_tax | 2,397.9 | 3,452.7 | 1,054.8 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | head | ni_class_1_employer | 27,241.7 | 28,268.7 | 1,027.0 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | source_row | obr_pmd_nov2025:11683:b9096ecd110093bf | 2,321.6 | 3,347.6 | 1,026.0 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | measure_year | total | 2,321.6 | 3,347.6 | 1,026.0 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | head | capital_gains_tax | 2,321.6 | 3,347.6 | 1,026.0 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | source_row | obr_pmd_nov2025:11675:286359ea5a53fc94 | 25,792.5 | 26,780.3 | 987.8 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | head | ni_class_1_employer | 26,662.9 | 27,634.4 | 971.5 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | source_row | obr_pmd_nov2025:12341:ce174c39c117892d | 213.1 | -750.0 | -963.1 | numerical, structural |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | head | income_tax | 213.1 | -750.0 | -963.1 | numerical, structural |
| autumn_budget_2024 | employer_nics_package | 2027 | head | ni_class_1_employer | 26,265.5 | 27,222.6 | 957.1 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | head | ni_class_1_employer | 25,844.5 | 26,786.4 | 941.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | source_row | obr_pmd_nov2025:11674:6dd4d473c559cbea | 25,217.9 | 26,145.6 | 927.8 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | head | ni_class_1_employer | 25,303.5 | 26,226.0 | 922.5 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | source_row | obr_pmd_nov2025:11673:94b8906a8929f113 | 24,832.1 | 25,743.0 | 911.0 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | source_row | obr_pmd_nov2025:11672:0b55202125025854 | 24,413.3 | 25,306.6 | 893.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | source_row | obr_pmd_nov2025:11671:291070a94715062c | 23,874.6 | 24,749.5 | 874.8 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | source_row | obr_pmd_nov2025:12340:56a6872c6215ff54 | 119.2 | -715.2 | -834.4 | numerical, structural |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | head | income_tax | 119.2 | -715.2 | -834.4 | numerical, structural |
| autumn_budget_2024 | employer_nics_package | 2029 | measure_year | total | 17,699.6 | 18,439.5 | 739.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | measure_year | total | 17,319.6 | 18,042.1 | 722.4 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | source_row | obr_pmd_nov2025:12347:687b6f32b91450d1 | 2,129.2 | 2,833.2 | 704.0 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | measure_year | total | 17,268.0 | 17,871.6 | 603.6 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | source_row | obr_pmd_nov2025:23338:27e34c93a163b4f0 | -753.2 | -1,355.9 | -602.7 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | measure_year | total | -753.2 | -1,355.9 | -602.7 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2029 | head | universal_credit | -753.2 | -1,355.9 | -602.7 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | measure_year | total | 17,036.4 | 17,631.3 | 594.9 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | head | ni_class_1_employer | 1,868.2 | 2,459.2 | 591.0 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | source_row | obr_pmd_nov2025:12346:3b87f6a01f129a2e | 2,131.3 | 2,718.6 | 587.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | measure_year | total | 16,812.9 | 17,366.4 | 553.5 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | head | ni_class_1_employer | 1,867.4 | 2,360.6 | 493.2 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | head | ni_class_1_employee | -12,449.9 | -12,905.2 | -455.3 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | head | ni_class_1_employee | -12,449.9 | -12,905.2 | -455.3 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | source_row | obr_pmd_nov2025:10553:39c2cf71f48d4440 | -12,442.4 | -12,895.2 | -452.8 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | source_row | obr_pmd_nov2025:10961:cc058843879051af | -12,442.4 | -12,895.2 | -452.8 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2027 | head | ni_class_1_employee | -12,132.3 | -12,574.6 | -442.2 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2027 | head | ni_class_1_employee | -12,132.3 | -12,574.6 | -442.2 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2027 | source_row | obr_pmd_nov2025:10552:16a41c96f88267ae | -12,126.5 | -12,566.4 | -439.9 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2027 | source_row | obr_pmd_nov2025:10960:fa02958b7f130d94 | -12,126.5 | -12,566.4 | -439.9 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | source_row | obr_pmd_nov2025:11682:73295721bdfdb9e8 | 956.3 | 1,395.7 | 439.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | measure_year | total | 956.3 | 1,395.7 | 439.4 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | head | capital_gains_tax | 956.3 | 1,395.7 | 439.4 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2028 | measure_year | total | -12,139.0 | -12,570.7 | -431.7 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2028 | measure_year | total | -12,139.0 | -12,570.7 | -431.7 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2026 | head | ni_class_1_employee | -11,795.8 | -12,226.8 | -431.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2026 | head | ni_class_1_employee | -11,795.8 | -12,226.8 | -431.0 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2026 | source_row | obr_pmd_nov2025:10551:67fe35e4947b995a | -11,791.7 | -12,220.7 | -429.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2026 | source_row | obr_pmd_nov2025:10959:424db47edb88e339 | -11,791.7 | -12,220.7 | -429.0 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2027 | measure_year | total | -11,834.1 | -12,254.3 | -420.2 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2027 | measure_year | total | -11,834.1 | -12,254.3 | -420.2 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | head | ni_class_1_employee | -11,332.9 | -11,746.8 | -413.9 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | head | ni_class_1_employee | -11,332.9 | -11,746.8 | -413.9 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | source_row | obr_pmd_nov2025:10550:68081ae97974ee1e | -11,330.0 | -11,742.1 | -412.1 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | source_row | obr_pmd_nov2025:10958:c7a912de7a1a9114 | -11,330.0 | -11,742.1 | -412.1 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2026 | measure_year | total | -11,509.7 | -11,919.7 | -410.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2026 | measure_year | total | -11,509.7 | -11,919.7 | -410.0 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | source_row | obr_pmd_nov2025:23337:31f0f1693e3bba3c | -746.6 | -1,147.8 | -401.2 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | measure_year | total | -746.6 | -1,147.8 | -401.2 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2028 | head | universal_credit | -746.6 | -1,147.8 | -401.2 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2025 | measure_year | total | -11,063.8 | -11,460.8 | -397.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2025 | measure_year | total | -11,063.8 | -11,460.8 | -397.0 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | head | ni_class_1_employee | -10,632.8 | -11,027.9 | -395.1 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | head | ni_class_1_employee | -10,632.8 | -11,027.9 | -395.1 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | source_row | obr_pmd_nov2025:10549:7322b894d39fa3ec | -10,630.4 | -11,024.0 | -393.7 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | source_row | obr_pmd_nov2025:10957:34718787787f7089 | -10,630.4 | -11,024.0 | -393.7 | numerical |
| autumn_statement_2023 | class_1_employee_nics_main_rate_cut_2p | 2024 | measure_year | total | -10,389.3 | -10,769.3 | -380.0 | numerical |
| spring_budget_2024 | class_1_employee_nics_main_rate_cut_2pp | 2024 | measure_year | total | -10,389.3 | -10,769.3 | -380.0 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2030 | source_row | obr_pmd_nov2025:12239:11eea01fb370a818 | 12,482.3 | 12,848.0 | 365.8 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2030 | head | income_tax | 12,482.3 | 12,848.0 | 365.8 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2030 | measure_year | total | 12,256.7 | 12,604.2 | 347.5 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | source_row | obr_pmd_nov2025:11665:72598886f546ef8c | -7,061.7 | -7,383.1 | -321.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | head | income_tax | -7,061.7 | -7,383.1 | -321.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | source_row | obr_pmd_nov2025:11667:35345df3785dfdea | -7,564.0 | -7,871.4 | -307.4 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | head | income_tax | -7,564.0 | -7,871.4 | -307.4 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -7,376.9 | -7,675.4 | -298.4 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | head | income_tax | -7,376.9 | -7,675.4 | -298.4 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | measure_year | total | 2,342.3 | 2,083.2 | -259.1 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | source_row | obr_pmd_nov2025:11669:1cedd72c387ad84b | -8,092.9 | -8,340.8 | -247.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2029 | head | income_tax | -8,092.9 | -8,340.8 | -247.9 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | measure_year | total | 2,250.5 | 2,003.3 | -247.1 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | source_row | obr_pmd_nov2025:11668:a076a7d6b3992e7c | -7,898.2 | -8,103.5 | -205.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | head | income_tax | -7,898.2 | -8,103.5 | -205.3 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2029 | source_row | obr_pmd_nov2025:12238:ed7d488b306dcf83 | 8,079.0 | 8,274.9 | 195.9 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2029 | head | income_tax | 8,079.0 | 8,274.9 | 195.9 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | source_row | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 | -732.7 | -923.3 | -190.6 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | measure_year | total | -732.7 | -923.3 | -190.6 | numerical |
| spring_statement_2025 | uc_standard_allowance_above_inflation | 2027 | head | universal_credit | -732.7 | -923.3 | -190.6 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | source_row | obr_pmd_nov2025:10234:7fb22cdd33e49932 | -3,540.3 | -3,351.4 | 188.9 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | measure_year | total | -3,540.3 | -3,351.4 | 188.9 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2026 | head | income_tax | -3,540.3 | -3,351.4 | 188.9 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2029 | measure_year | total | 7,928.6 | 8,115.1 | 186.6 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2028 | source_row | obr_pmd_nov2025:12237:0c8c820d59cc8062 | 3,859.5 | 4,015.0 | 155.5 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2028 | head | income_tax | 3,859.5 | 4,015.0 | 155.5 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | source_row | obr_pmd_nov2025:10235:fbb8ccda250b78e9 | -3,725.2 | -3,573.2 | 152.0 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | measure_year | total | -3,725.2 | -3,573.2 | 152.0 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2027 | head | income_tax | -3,725.2 | -3,573.2 | 152.0 | numerical |
| autumn_budget_2025 | ab2025__personal_tax_thresholds_freeze_to_2031 | 2028 | measure_year | total | 3,784.1 | 3,935.3 | 151.3 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | source_row | obr_pmd_nov2025:22206:49a0caec037600d2 | -336.2 | -189.6 | 146.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | head | child_benefit | -336.2 | -189.6 | 146.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | source_row | obr_pmd_nov2025:10987:0f254c98c34bc660 | -779.6 | -914.2 | -134.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2024 | head | income_tax | -779.6 | -914.2 | -134.6 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | source_row | obr_pmd_nov2025:11620:5446e6157f4ef4ec | 2,138.1 | 2,018.2 | -119.9 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | measure_year | total | 2,138.1 | 2,018.2 | -119.9 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2028 | head | private_school_vat | 2,138.1 | 2,018.2 | -119.9 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | source_row | obr_pmd_nov2025:10991:11a476b01436c0db | -1,394.7 | -1,276.3 | 118.4 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | head | income_tax | -1,394.7 | -1,276.3 | 118.4 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2030 | head | ni_class_1_employee | 260.9 | 373.9 | 113.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | source_row | obr_pmd_nov2025:11621:8bf103a18fecf781 | 2,163.0 | 2,053.0 | -110.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | measure_year | total | 2,163.0 | 2,053.0 | -110.0 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2029 | head | private_school_vat | 2,163.0 | 2,053.0 | -110.0 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2030 | source_row | obr_pmd_nov2025:12311:9143a3313d158e51 | 1,034.8 | 1,132.7 | 98.0 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2030 | measure_year | total | 1,034.8 | 1,132.7 | 98.0 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2030 | head | income_tax | 1,034.8 | 1,132.7 | 98.0 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,131.6 | -1,036.0 | 95.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | head | income_tax | -1,131.6 | -1,036.0 | 95.6 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2029 | source_row | obr_pmd_nov2025:12310:28dedd8eb897f229 | 1,006.6 | 1,101.5 | 94.9 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2029 | measure_year | total | 1,006.6 | 1,101.5 | 94.9 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2029 | head | income_tax | 1,006.6 | 1,101.5 | 94.9 | numerical |
| autumn_budget_2025 | ab2025__salary_sacrifice_pension_nics_cap_2000 | 2029 | head | ni_class_1_employee | 263.9 | 358.0 | 94.1 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2028 | source_row | obr_pmd_nov2025:12309:0fbcc0c4dc21227c | 980.2 | 1,072.4 | 92.2 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2028 | measure_year | total | 980.2 | 1,072.4 | 92.2 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2028 | head | income_tax | 980.2 | 1,072.4 | 92.2 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2027 | source_row | obr_pmd_nov2025:12308:5c1e45be5eff2e8d | 954.3 | 1,042.3 | 88.0 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2027 | measure_year | total | 954.3 | 1,042.3 | 88.0 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2027 | head | income_tax | 954.3 | 1,042.3 | 88.0 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2026 | source_row | obr_pmd_nov2025:12307:90ac5224d0623421 | 926.7 | 1,011.0 | 84.3 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2026 | measure_year | total | 926.7 | 1,011.0 | 84.3 | numerical |
| autumn_budget_2025 | ab2025__dividend_rates_plus_2pp | 2026 | head | income_tax | 926.7 | 1,011.0 | 84.3 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2027 | source_row | obr_pmd_nov2025:11619:8726edda9aa7b020 | 2,044.4 | 1,960.2 | -84.2 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2027 | measure_year | total | 2,044.4 | 1,960.2 | -84.2 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2027 | head | private_school_vat | 2,044.4 | 1,960.2 | -84.2 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2028 | measure_year | total | -1,757.8 | -1,676.4 | 81.3 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | source_row | obr_pmd_nov2025:11617:414a87b10621e433 | 1,940.3 | 1,862.0 | -78.2 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | measure_year | total | 1,940.3 | 1,862.0 | -78.2 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2025 | head | private_school_vat | 1,940.3 | 1,862.0 | -78.2 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | source_row | obr_pmd_nov2025:10233:f9cad5be5ec138c8 | -3,300.7 | -3,224.4 | 76.4 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | measure_year | total | -3,300.7 | -3,224.4 | 76.4 | numerical |
| spring_budget_2023 | pension_annual_allowance_package | 2025 | head | income_tax | -3,300.7 | -3,224.4 | 76.4 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2030 | source_row | obr_pmd_nov2025:12287:19f9ac9e5f5eff97 | 1,025.5 | 1,097.0 | 71.6 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2030 | measure_year | total | 1,025.5 | 1,097.0 | 71.6 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2030 | head | income_tax | 1,025.5 | 1,097.0 | 71.6 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,274.7 | -1,203.5 | 71.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | head | income_tax | -1,274.7 | -1,203.5 | 71.1 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | -307.8 | -377.1 | -69.3 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2026 | head | child_benefit | -307.8 | -377.1 | -69.3 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2029 | source_row | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc | 976.2 | 1,044.3 | 68.1 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2029 | measure_year | total | 976.2 | 1,044.3 | 68.1 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2029 | head | income_tax | 976.2 | 1,044.3 | 68.1 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2028 | source_row | obr_pmd_nov2025:12285:75dff87b1a3e5f53 | 931.5 | 996.5 | 65.0 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2028 | measure_year | total | 931.5 | 996.5 | 65.0 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2028 | head | income_tax | 931.5 | 996.5 | 65.0 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2027 | source_row | obr_pmd_nov2025:12284:4b5e915d45bc4a6b | 889.6 | 951.4 | 61.8 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2027 | measure_year | total | 889.6 | 951.4 | 61.8 | numerical |
| autumn_budget_2025 | ab2025__property_income_separate_rates | 2027 | head | income_tax | 889.6 | 951.4 | 61.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2027 | measure_year | total | -1,598.2 | -1,541.4 | 56.8 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | -282.5 | -337.0 | -54.5 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | head | child_benefit | -282.5 | -337.0 | -54.5 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,966.5 | 1,915.8 | -50.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | measure_year | total | 1,966.5 | 1,915.8 | -50.8 | numerical |
| autumn_budget_2024 | private_school_vat_20pct | 2026 | head | private_school_vat | 1,966.5 | 1,915.8 | -50.8 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2029 | source_row | obr_pmd_nov2025:23529:1e1a237caba88918 | -3,259.2 | -3,309.7 | -50.5 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2029 | measure_year | total | -3,259.2 | -3,309.7 | -50.5 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2029 | head | universal_credit | -3,259.2 | -3,309.7 | -50.5 | numerical |
| autumn_budget_2024 | employer_nics_package | 2026 | head | ni_class_1_employee | -1,431.6 | -1,480.5 | -48.9 | numerical |
| autumn_budget_2024 | employer_nics_package | 2025 | head | ni_class_1_employee | -1,429.3 | -1,477.3 | -48.0 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2028 | source_row | obr_pmd_nov2025:23528:35553a766a3ad3d3 | -3,154.8 | -3,201.8 | -47.0 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2028 | measure_year | total | -3,154.8 | -3,201.8 | -47.0 | numerical |
| autumn_budget_2025 | ab2025__uc_child_element_remove_two_child_limit | 2028 | head | universal_credit | -3,154.8 | -3,201.8 | -47.0 | numerical |
| autumn_budget_2024 | employer_nics_package | 2027 | head | ni_class_1_employee | -1,433.9 | -1,480.3 | -46.4 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -980.5 | -934.9 | 45.5 | numerical |
| spring_budget_2024 | hicbc_threshold_and_taper | 2025 | head | income_tax | -980.5 | -934.9 | 45.5 | numerical |
| autumn_budget_2025 | ab2025__savings_rates_plus_2pp_and_starter_limit_held | 2030 | source_row | obr_pmd_nov2025:12335:4ff6459d9e873238 | 1,155.8 | 1,200.1 | 44.3 | numerical |
| autumn_budget_2025 | ab2025__savings_rates_plus_2pp_and_starter_limit_held | 2030 | measure_year | total | 1,155.8 | 1,200.1 | 44.3 | numerical |
| autumn_budget_2025 | ab2025__savings_rates_plus_2pp_and_starter_limit_held | 2030 | head | income_tax | 1,155.8 | 1,200.1 | 44.3 | numerical |
| autumn_budget_2024 | employer_nics_package | 2028 | head | ni_class_1_employee | -1,446.3 | -1,490.4 | -44.1 | numerical |

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
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 5 |
| same_sign_ratio_at_least_2 | not_available | 5 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 8 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 5 |

### autumn_budget_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 28 |
| not_available | not_available | 1422 |
| obr_zero | obr_zero | 1 |
| opposite_sign | same_sign_ratio_0.8_to_1.25 | 1 |
| pe_zero | pe_zero | 19 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 9 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 15 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | 1 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 7 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | 1 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 6 |
| same_sign_ratio_below_0.5 | opposite_sign | 1 |

### autumn_statement_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1066 |
| pe_zero | pe_zero | 13 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 6 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | 1 |
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
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 1 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | 3 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.5_to_0.8 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 7 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | 3 |
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
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2024](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2024.md)
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
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2026](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2026.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2027](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2027.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2028](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2028.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2029](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2029.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2030](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2030.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2028](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2028.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2029](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2029.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2030](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2030.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2028](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2028.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2029](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2029.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2030](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2030.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2028](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2028.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2029](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2029.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2030](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2030.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2027](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2027.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2028](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2028.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2029](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2029.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2030](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2030.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2029](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2029.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2030](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2030.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2027](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2027.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2028](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2028.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2029](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2029.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2030](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2030.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2026](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2026.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2027](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2027.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2028](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2028.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2029](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2029.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2030](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2030.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2025](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2025.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2030](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2030.md)
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
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2027](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2027.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2028](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2028.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2029](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2029.md)
