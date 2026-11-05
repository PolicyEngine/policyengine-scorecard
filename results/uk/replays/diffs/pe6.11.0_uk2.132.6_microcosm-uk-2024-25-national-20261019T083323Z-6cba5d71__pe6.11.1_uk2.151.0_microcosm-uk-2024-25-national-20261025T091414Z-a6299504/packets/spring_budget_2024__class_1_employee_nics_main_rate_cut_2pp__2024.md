# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10951:49c3da315ada632b | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10957:34718787787f7089 | -10,656.0 | -10,469.2 | 186.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10963:90e1bf4e6455e6ed | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22170:45627d3976bd492a | 181.4 | 163.0 | -18.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22176:91b90277f32ee81d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22182:0407f81829b783d3 | — | — | — | — | — |
| measure_year | total | -10,474.5 | -10,306.2 | 168.3 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -10,662.6 | -10,474.8 | 187.8 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 6.6 | 5.6 | -1.0 | numerical | move_above_threshold |
| head | universal_credit | 181.4 | 163.0 | -18.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10951:49c3da315ada632b (row 10951) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10957:34718787787f7089 (row 10957) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,398.5 | -10,656.0 | -10,469.2 |
| base | obr_pmd_nov2025:10963:90e1bf4e6455e6ed (row 10963) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -79.2 | — | — |
| base | obr_pmd_nov2025:22170:45627d3976bd492a (row 22170) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.8 | 181.4 | 163.0 |
| base | obr_pmd_nov2025:22176:91b90277f32ee81d (row 22176) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22182:0407f81829b783d3 (row 22182) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10951:49c3da315ada632b (row 10951) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10957:34718787787f7089 (row 10957) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,398.5 | -10,656.0 | -10,469.2 |
| head | obr_pmd_nov2025:10963:90e1bf4e6455e6ed (row 10963) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -79.2 | — | — |
| head | obr_pmd_nov2025:22170:45627d3976bd492a (row 22170) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.8 | 181.4 | 163.0 |
| head | obr_pmd_nov2025:22176:91b90277f32ee81d (row 22176) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22182:0407f81829b783d3 (row 22182) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024.json` (sha256 `e488312cfcfee4b2429ffd4af99ca5cf28a83c8a9ede481e4b9485432cf66353`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024.json` (sha256 `5f19780086c6d9546bbe107354c4262bcdc126d81fa17429b660f42c16e8cd42`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
