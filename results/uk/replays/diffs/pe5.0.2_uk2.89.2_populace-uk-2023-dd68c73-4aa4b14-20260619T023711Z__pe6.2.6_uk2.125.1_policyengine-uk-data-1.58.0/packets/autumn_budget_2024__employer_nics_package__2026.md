# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -8,507.7 | -7,456.0 | 1,051.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11672:0b55202125025854 | 24,754.4 | 24,534.0 | -220.5 | — | — |
| source_row | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22825:edacdcc46eb06fe4 | — | — | — | — | — |
| measure_year | total | 16,246.7 | 17,077.9 | 831.2 | numerical | move_above_threshold |
| head | income_tax | -8,507.7 | -7,456.0 | 1,051.7 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,260.5 | -1,428.1 | -167.6 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,014.0 | 25,961.6 | -52.4 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.9 | 0.5 | -0.5 | — | — |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -8,507.7 | -7,456.0 |
| obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,754.4 | 24,534.0 |
| obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `6e42825fd8a34899580c52fef565374a05406652556e75d8ae04b89edaefd322`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `85b474fc000ee82371908d8e3a0626a3e6f76deda52a12740c9c75cbad8108fa`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
