# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10955:f6669fdf7dfdb034 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10961:cc058843879051af | -12,198.4 | -12,552.1 | -353.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10967:74cca71eaf790883 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22174:b9088212717e5ab4 | 223.7 | 241.7 | 18.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22180:d3ab9da8189aac68 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22186:471c557dcd62c5e3 | — | — | — | — | — |
| measure_year | total | -11,974.7 | -12,310.4 | -335.6 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,205.5 | -12,556.0 | -350.4 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 7.1 | 3.9 | -3.2 | numerical | move_above_threshold |
| head | universal_credit | 223.7 | 241.7 | 18.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10955:f6669fdf7dfdb034 (row 10955) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 472.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10961:cc058843879051af (row 10961) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -10,088.4 | -12,198.4 | -12,552.1 |
| base | obr_pmd_nov2025:10967:74cca71eaf790883 (row 10967) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -606.3 | — | — |
| base | obr_pmd_nov2025:22174:b9088212717e5ab4 (row 22174) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 179.6 | 223.7 | 241.7 |
| base | obr_pmd_nov2025:22180:d3ab9da8189aac68 (row 22180) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 5.9 | — | — |
| base | obr_pmd_nov2025:22186:471c557dcd62c5e3 (row 22186) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 49.0 | — | — |
| head | obr_pmd_nov2025:10955:f6669fdf7dfdb034 (row 10955) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 472.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10961:cc058843879051af (row 10961) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -10,088.4 | -12,198.4 | -12,552.1 |
| head | obr_pmd_nov2025:10967:74cca71eaf790883 (row 10967) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -606.3 | — | — |
| head | obr_pmd_nov2025:22174:b9088212717e5ab4 (row 22174) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 179.6 | 223.7 | 241.7 |
| head | obr_pmd_nov2025:22180:d3ab9da8189aac68 (row 22180) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 5.9 | — | — |
| head | obr_pmd_nov2025:22186:471c557dcd62c5e3 (row 22186) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 49.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028.json` (sha256 `5aa155de647adcadc2f0d5ff7f501fe3371fdddb7f51a811e2091a48ded2c01f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028.json` (sha256 `7d13bb7ac73ba36889cd13381460da3ca88128b1cbcecc2d0a16ddd2d757767b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
