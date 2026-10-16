# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11665:72598886f546ef8c | -8,163.5 | -7,061.7 | 1,101.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11671:291070a94715062c | 24,174.8 | 23,874.6 | -300.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11677:38177db5dd288931 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22818:aeea2c28b98a2cfa | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22824:43a72c43eb1bd902 | — | — | — | — | — |
| measure_year | total | 16,011.3 | 16,812.9 | 801.6 | numerical | move_above_threshold |
| head | income_tax | -8,163.5 | -7,061.7 | 1,101.7 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,251.6 | -1,429.3 | -177.7 | numerical | move_above_threshold |
| head | ni_class_1_employer | 25,425.5 | 25,303.5 | -122.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.9 | 0.5 | -0.4 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11665:72598886f546ef8c (row 11665) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.1 | -8,163.5 | -7,061.7 |
| base | obr_pmd_nov2025:11671:291070a94715062c (row 11671) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 23,737.5 | 24,174.8 | 23,874.6 |
| base | obr_pmd_nov2025:11677:38177db5dd288931 (row 11677) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 32.3 | — | — |
| base | obr_pmd_nov2025:22818:aeea2c28b98a2cfa (row 22818) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |
| base | obr_pmd_nov2025:22824:43a72c43eb1bd902 (row 22824) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:11665:72598886f546ef8c (row 11665) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.1 | -8,163.5 | -7,061.7 |
| head | obr_pmd_nov2025:11671:291070a94715062c (row 11671) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 23,737.5 | 24,174.8 | 23,874.6 |
| head | obr_pmd_nov2025:11677:38177db5dd288931 (row 11677) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 32.3 | — | — |
| head | obr_pmd_nov2025:22818:aeea2c28b98a2cfa (row 22818) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:22824:43a72c43eb1bd902 (row 22824) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025.json` (sha256 `a3cdecdf9670362c81e7b5566da0f52ed6db157da496091c6226e429488c8716`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025.json` (sha256 `8fbcabccac5bcc82aae3a7c188223454728f04c630ff6371a158186788e53cfb`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
