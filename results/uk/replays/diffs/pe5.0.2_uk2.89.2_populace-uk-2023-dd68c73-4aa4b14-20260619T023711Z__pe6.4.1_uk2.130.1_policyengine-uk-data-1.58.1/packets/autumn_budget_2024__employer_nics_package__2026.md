# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -8,507.7 | -7,376.9 | 1,130.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11672:0b55202125025854 | 24,754.4 | 24,413.3 | -341.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22825:edacdcc46eb06fe4 | — | — | — | — | — |
| measure_year | total | 16,246.7 | 17,036.4 | 789.7 | numerical | move_above_threshold |
| head | income_tax | -8,507.7 | -7,376.9 | 1,130.8 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,260.5 | -1,431.6 | -171.1 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,014.0 | 25,844.5 | -169.5 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.9 | 0.5 | -0.5 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -8,507.7 | -7,376.9 |
| base | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,754.4 | 24,413.3 |
| base | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| base | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| base | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |
| head | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -8,507.7 | -7,376.9 |
| head | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,754.4 | 24,413.3 |
| head | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| head | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| head | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `6e42825fd8a34899580c52fef565374a05406652556e75d8ae04b89edaefd322`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `dc88811fcf3d7508a33eff55dc9785f1a52f481fe1c0664ad292ced2ac314bcc`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
