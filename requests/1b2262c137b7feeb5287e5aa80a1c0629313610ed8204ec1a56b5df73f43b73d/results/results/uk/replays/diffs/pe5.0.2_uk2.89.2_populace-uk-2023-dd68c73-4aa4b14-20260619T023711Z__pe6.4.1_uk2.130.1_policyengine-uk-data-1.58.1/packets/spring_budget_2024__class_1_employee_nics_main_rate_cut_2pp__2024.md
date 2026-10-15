# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10951:49c3da315ada632b | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10957:34718787787f7089 | -11,082.5 | -10,630.4 | 452.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10963:90e1bf4e6455e6ed | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22170:45627d3976bd492a | 86.2 | 241.1 | 154.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22176:91b90277f32ee81d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22182:0407f81829b783d3 | — | — | — | — | — |
| measure_year | total | -10,996.3 | -10,389.3 | 607.0 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,086.5 | -10,632.8 | 453.7 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.9 | 2.4 | -1.5 | numerical | move_above_threshold |
| head | universal_credit | 86.2 | 241.1 | 154.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10951:49c3da315ada632b (row 10951) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10957:34718787787f7089 (row 10957) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,398.5 | -11,082.5 | -10,630.4 |
| base | obr_pmd_nov2025:10963:90e1bf4e6455e6ed (row 10963) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -79.2 | — | — |
| base | obr_pmd_nov2025:22170:45627d3976bd492a (row 22170) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.8 | 86.2 | 241.1 |
| base | obr_pmd_nov2025:22176:91b90277f32ee81d (row 22176) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22182:0407f81829b783d3 (row 22182) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10951:49c3da315ada632b (row 10951) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10957:34718787787f7089 (row 10957) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,398.5 | -11,082.5 | -10,630.4 |
| head | obr_pmd_nov2025:10963:90e1bf4e6455e6ed (row 10963) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -79.2 | — | — |
| head | obr_pmd_nov2025:22170:45627d3976bd492a (row 22170) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.8 | 86.2 | 241.1 |
| head | obr_pmd_nov2025:22176:91b90277f32ee81d (row 22176) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22182:0407f81829b783d3 (row 22182) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024.json` (sha256 `c211dee279061b6f57d7c003626a33ad97db84e5f3e3e1f1b992df6a45ef27f4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024.json` (sha256 `98dc848365f0027cd0330c515609d67a6a5618d4963a0e94254a3a66a3bd3063`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
