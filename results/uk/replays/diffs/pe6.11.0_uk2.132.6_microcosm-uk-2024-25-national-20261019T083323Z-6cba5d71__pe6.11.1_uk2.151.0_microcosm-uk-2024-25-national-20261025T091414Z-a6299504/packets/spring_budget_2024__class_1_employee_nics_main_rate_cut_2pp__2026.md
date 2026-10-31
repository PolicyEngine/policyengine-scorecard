# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10953:5e4605a850c3f718 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10959:424db47edb88e339 | -11,770.0 | -11,564.0 | 206.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22172:8c021f0cf80fe71b | 218.5 | 201.4 | -17.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22178:7e29523685e665e3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22184:cdeff505e05e7e8d | — | — | — | — | — |
| measure_year | total | -11,551.5 | -11,362.6 | 188.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,779.3 | -11,569.4 | 209.9 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 9.3 | 5.4 | -3.9 | numerical | move_above_threshold |
| head | universal_credit | 218.5 | 201.4 | -17.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10953:5e4605a850c3f718 (row 10953) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 318.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10959:424db47edb88e339 (row 10959) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,619.3 | -11,770.0 | -11,564.0 |
| base | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 (row 10965) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -394.6 | — | — |
| base | obr_pmd_nov2025:22172:8c021f0cf80fe71b (row 22172) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.9 | 218.5 | 201.4 |
| base | obr_pmd_nov2025:22178:7e29523685e665e3 (row 22178) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 3.7 | — | — |
| base | obr_pmd_nov2025:22184:cdeff505e05e7e8d (row 22184) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 30.2 | — | — |
| head | obr_pmd_nov2025:10953:5e4605a850c3f718 (row 10953) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 318.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10959:424db47edb88e339 (row 10959) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,619.3 | -11,770.0 | -11,564.0 |
| head | obr_pmd_nov2025:10965:9b5a5f5dd80b8bd2 (row 10965) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -394.6 | — | — |
| head | obr_pmd_nov2025:22172:8c021f0cf80fe71b (row 22172) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.9 | 218.5 | 201.4 |
| head | obr_pmd_nov2025:22178:7e29523685e665e3 (row 22178) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 3.7 | — | — |
| head | obr_pmd_nov2025:22184:cdeff505e05e7e8d (row 22184) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 30.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026.json` (sha256 `bd8181336d6c15a1d5763aa809ccb61d9823378e546621acb75f273c914962b0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026.json` (sha256 `29b604f629bbe20c078957dd1c9719f495985859453759ff4ec977653d3a91d6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
