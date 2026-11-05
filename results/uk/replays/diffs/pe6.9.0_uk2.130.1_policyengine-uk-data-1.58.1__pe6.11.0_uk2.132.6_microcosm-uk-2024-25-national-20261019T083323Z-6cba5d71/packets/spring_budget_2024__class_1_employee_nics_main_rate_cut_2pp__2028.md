# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10955:f6669fdf7dfdb034 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10961:cc058843879051af | -12,442.4 | -12,417.4 | 25.1 | — | — |
| source_row | obr_pmd_nov2025:10967:74cca71eaf790883 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22174:b9088212717e5ab4 | 303.4 | 237.5 | -65.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22180:d3ab9da8189aac68 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22186:471c557dcd62c5e3 | — | — | — | — | — |
| measure_year | total | -12,139.0 | -12,179.8 | -40.8 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,449.9 | -12,428.5 | 21.4 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 7.4 | 11.1 | 3.7 | numerical | move_above_threshold |
| head | universal_credit | 303.4 | 237.5 | -65.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10955:f6669fdf7dfdb034 (row 10955) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 472.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10961:cc058843879051af (row 10961) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -10,088.4 | -12,442.4 | -12,417.4 |
| base | obr_pmd_nov2025:10967:74cca71eaf790883 (row 10967) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -606.3 | — | — |
| base | obr_pmd_nov2025:22174:b9088212717e5ab4 (row 22174) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 179.6 | 303.4 | 237.5 |
| base | obr_pmd_nov2025:22180:d3ab9da8189aac68 (row 22180) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 5.9 | — | — |
| base | obr_pmd_nov2025:22186:471c557dcd62c5e3 (row 22186) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 49.0 | — | — |
| head | obr_pmd_nov2025:10955:f6669fdf7dfdb034 (row 10955) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 472.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10961:cc058843879051af (row 10961) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -10,088.4 | -12,442.4 | -12,417.4 |
| head | obr_pmd_nov2025:10967:74cca71eaf790883 (row 10967) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -606.3 | — | — |
| head | obr_pmd_nov2025:22174:b9088212717e5ab4 (row 22174) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 179.6 | 303.4 | 237.5 |
| head | obr_pmd_nov2025:22180:d3ab9da8189aac68 (row 22180) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 5.9 | — | — |
| head | obr_pmd_nov2025:22186:471c557dcd62c5e3 (row 22186) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 49.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028.json` (sha256 `18c9634c7539dc77483ef42a7a125b604dd076cdc379f0a639cfe244f4580db4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028.json` (sha256 `997f19daa536d08543d0148dc6c3158ca44e82ad4756ae5dad84e38f597d5377`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
