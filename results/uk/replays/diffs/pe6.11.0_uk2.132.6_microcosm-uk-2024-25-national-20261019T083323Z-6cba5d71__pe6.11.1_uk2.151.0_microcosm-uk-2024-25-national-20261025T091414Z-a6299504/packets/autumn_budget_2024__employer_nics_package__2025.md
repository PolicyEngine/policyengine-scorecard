# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11665:72598886f546ef8c | -7,386.0 | -7,205.9 | 180.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11671:291070a94715062c | 24,149.9 | 23,715.6 | -434.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11677:38177db5dd288931 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22818:aeea2c28b98a2cfa | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22824:43a72c43eb1bd902 | — | — | — | — | — |
| measure_year | total | 16,763.9 | 16,509.6 | -254.2 | numerical | move_above_threshold |
| head | income_tax | -7,386.0 | -7,205.9 | 180.1 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,368.0 | -1,335.6 | 32.5 | numerical | move_above_threshold |
| head | ni_class_1_employer | 25,516.8 | 25,050.2 | -466.6 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.1 | 1.0 | -0.2 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11665:72598886f546ef8c (row 11665) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.1 | -7,386.0 | -7,205.9 |
| base | obr_pmd_nov2025:11671:291070a94715062c (row 11671) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 23,737.5 | 24,149.9 | 23,715.6 |
| base | obr_pmd_nov2025:11677:38177db5dd288931 (row 11677) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 32.3 | — | — |
| base | obr_pmd_nov2025:22818:aeea2c28b98a2cfa (row 22818) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |
| base | obr_pmd_nov2025:22824:43a72c43eb1bd902 (row 22824) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:11665:72598886f546ef8c (row 11665) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.1 | -7,386.0 | -7,205.9 |
| head | obr_pmd_nov2025:11671:291070a94715062c (row 11671) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 23,737.5 | 24,149.9 | 23,715.6 |
| head | obr_pmd_nov2025:11677:38177db5dd288931 (row 11677) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 32.3 | — | — |
| head | obr_pmd_nov2025:22818:aeea2c28b98a2cfa (row 22818) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:22824:43a72c43eb1bd902 (row 22824) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025.json` (sha256 `6675f7fce3af35cbc659e9cdeaa8170ac4c7f930c1d41edd04b3f6a1133ea03d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025.json` (sha256 `216a2390a42a5cf3d71b9157d3a5a517620c175687514b68f27d5d64c192f3f3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
