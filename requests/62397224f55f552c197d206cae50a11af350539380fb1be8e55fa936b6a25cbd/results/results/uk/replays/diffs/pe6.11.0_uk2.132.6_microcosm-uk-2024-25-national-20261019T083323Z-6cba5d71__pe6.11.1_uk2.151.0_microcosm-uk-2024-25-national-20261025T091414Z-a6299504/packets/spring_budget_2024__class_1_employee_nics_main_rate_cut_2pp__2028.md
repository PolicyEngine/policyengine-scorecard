# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10955:f6669fdf7dfdb034 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10961:cc058843879051af | -12,417.4 | -12,198.4 | 218.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10967:74cca71eaf790883 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22174:b9088212717e5ab4 | 237.5 | 223.7 | -13.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22180:d3ab9da8189aac68 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22186:471c557dcd62c5e3 | — | — | — | — | — |
| measure_year | total | -12,179.8 | -11,974.7 | 205.1 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,428.5 | -12,205.5 | 222.9 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 11.1 | 7.1 | -4.0 | numerical | move_above_threshold |
| head | universal_credit | 237.5 | 223.7 | -13.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10955:f6669fdf7dfdb034 (row 10955) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 472.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10961:cc058843879051af (row 10961) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -10,088.4 | -12,417.4 | -12,198.4 |
| base | obr_pmd_nov2025:10967:74cca71eaf790883 (row 10967) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -606.3 | — | — |
| base | obr_pmd_nov2025:22174:b9088212717e5ab4 (row 22174) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 179.6 | 237.5 | 223.7 |
| base | obr_pmd_nov2025:22180:d3ab9da8189aac68 (row 22180) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 5.9 | — | — |
| base | obr_pmd_nov2025:22186:471c557dcd62c5e3 (row 22186) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 49.0 | — | — |
| head | obr_pmd_nov2025:10955:f6669fdf7dfdb034 (row 10955) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 472.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10961:cc058843879051af (row 10961) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -10,088.4 | -12,417.4 | -12,198.4 |
| head | obr_pmd_nov2025:10967:74cca71eaf790883 (row 10967) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -606.3 | — | — |
| head | obr_pmd_nov2025:22174:b9088212717e5ab4 (row 22174) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 179.6 | 237.5 | 223.7 |
| head | obr_pmd_nov2025:22180:d3ab9da8189aac68 (row 22180) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 5.9 | — | — |
| head | obr_pmd_nov2025:22186:471c557dcd62c5e3 (row 22186) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 49.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028.json` (sha256 `997f19daa536d08543d0148dc6c3158ca44e82ad4756ae5dad84e38f597d5377`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028.json` (sha256 `18e94e7203422fe39a1375ebc259509d0e350f94a540d77c1e2c637110bc504d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
