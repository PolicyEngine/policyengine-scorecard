# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10953:5e4605a850c3f718 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10959:424db47edb88e339 | -12,070.1 | -11,919.3 | 150.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22172:8c021f0cf80fe71b | 104.7 | 274.9 | 170.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22178:7e29523685e665e3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22184:cdeff505e05e7e8d | — | — | — | — | — |
| measure_year | total | -11,965.4 | -11,644.5 | 320.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,073.5 | -11,923.0 | 150.5 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.4 | 3.7 | 0.3 | — | — |
| head | universal_credit | 104.7 | 274.9 | 170.2 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10953:5e4605a850c3f718 (row 10953) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 318.8 | 0.0 | 0.0 |
| obr_pmd_nov2025:10959:424db47edb88e339 (row 10959) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,619.3 | -12,070.1 | -11,919.3 |
| obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 (row 10965) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -394.6 | — | — |
| obr_pmd_nov2025:22172:8c021f0cf80fe71b (row 22172) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.9 | 104.7 | 274.9 |
| obr_pmd_nov2025:22178:7e29523685e665e3 (row 22178) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 3.7 | — | — |
| obr_pmd_nov2025:22184:cdeff505e05e7e8d (row 22184) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 30.2 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026.json` (sha256 `5d382a5c9c226fdc759a41d0ca1351bfd72a4ad27118f73fb022b50827cf26d7`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026.json` (sha256 `ac186e0bd737597b3a739c179a07419dfa51b14fcc0363d1afc8edc635e02dd9`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
