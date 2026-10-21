# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10951:49c3da315ada632b | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10957:34718787787f7089 | -10,630.4 | -11,024.0 | -393.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10963:90e1bf4e6455e6ed | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22170:45627d3976bd492a | 241.1 | 254.7 | 13.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22176:91b90277f32ee81d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22182:0407f81829b783d3 | — | — | — | — | — |
| measure_year | total | -10,389.3 | -10,769.3 | -380.0 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -10,632.8 | -11,027.9 | -395.1 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 2.4 | 3.9 | 1.5 | numerical | move_above_threshold |
| head | universal_credit | 241.1 | 254.7 | 13.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10951:49c3da315ada632b (row 10951) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10957:34718787787f7089 (row 10957) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,398.5 | -10,630.4 | -11,024.0 |
| base | obr_pmd_nov2025:10963:90e1bf4e6455e6ed (row 10963) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -79.2 | — | — |
| base | obr_pmd_nov2025:22170:45627d3976bd492a (row 22170) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.8 | 241.1 | 254.7 |
| base | obr_pmd_nov2025:22176:91b90277f32ee81d (row 22176) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22182:0407f81829b783d3 (row 22182) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10951:49c3da315ada632b (row 10951) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10957:34718787787f7089 (row 10957) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,398.5 | -10,630.4 | -11,024.0 |
| head | obr_pmd_nov2025:10963:90e1bf4e6455e6ed (row 10963) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -79.2 | — | — |
| head | obr_pmd_nov2025:22170:45627d3976bd492a (row 22170) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.8 | 241.1 | 254.7 |
| head | obr_pmd_nov2025:22176:91b90277f32ee81d (row 22176) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22182:0407f81829b783d3 (row 22182) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024.json` (sha256 `460eb875484fb9fd0dcb621b7e78cbd54d5e860e21e8f78b8d983bdf3c697849`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024.json` (sha256 `ece802bdb5f3c5c858db485a90e91ef41e26055e9e983b35249c0b0c5df4a485`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
