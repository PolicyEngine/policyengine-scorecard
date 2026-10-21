# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10953:5e4605a850c3f718 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10959:424db47edb88e339 | -11,791.7 | -12,220.7 | -429.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22172:8c021f0cf80fe71b | 282.0 | 301.0 | 19.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22178:7e29523685e665e3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22184:cdeff505e05e7e8d | — | — | — | — | — |
| measure_year | total | -11,509.7 | -11,919.7 | -410.0 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,795.8 | -12,226.8 | -431.0 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 4.1 | 6.1 | 2.0 | numerical | move_above_threshold |
| head | universal_credit | 282.0 | 301.0 | 19.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10953:5e4605a850c3f718 (row 10953) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 318.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10959:424db47edb88e339 (row 10959) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,619.3 | -11,791.7 | -12,220.7 |
| base | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 (row 10965) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -394.6 | — | — |
| base | obr_pmd_nov2025:22172:8c021f0cf80fe71b (row 22172) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.9 | 282.0 | 301.0 |
| base | obr_pmd_nov2025:22178:7e29523685e665e3 (row 22178) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 3.7 | — | — |
| base | obr_pmd_nov2025:22184:cdeff505e05e7e8d (row 22184) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 30.2 | — | — |
| head | obr_pmd_nov2025:10953:5e4605a850c3f718 (row 10953) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 318.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10959:424db47edb88e339 (row 10959) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,619.3 | -11,791.7 | -12,220.7 |
| head | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 (row 10965) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -394.6 | — | — |
| head | obr_pmd_nov2025:22172:8c021f0cf80fe71b (row 22172) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.9 | 282.0 | 301.0 |
| head | obr_pmd_nov2025:22178:7e29523685e665e3 (row 22178) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 3.7 | — | — |
| head | obr_pmd_nov2025:22184:cdeff505e05e7e8d (row 22184) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 30.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026.json` (sha256 `5ff7aecbc6afdfb3078e1a26d9dbc6359f08e9a20ac50b1d775a775876380a70`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026.json` (sha256 `70a159504fe7b66a60670ab2b1b8d61f949fa16059b9a7868354d0184ab4a4bd`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
