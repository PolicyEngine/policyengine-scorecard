# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10547:ac4c90edc3f68a4a | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10553:39c2cf71f48d4440 | -12,663.9 | -12,566.1 | 97.7 | — | — |
| source_row | obr_pmd_nov2025:10559:25df56e9c429d3de | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10565:b5bfc5a7ff82833c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21466:43674024394e1bc0 | 109.8 | 308.4 | 198.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21472:b09d4425f46fcb57 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21478:88af641dd7a06883 | — | — | — | — | — |
| measure_year | total | -12,554.1 | -12,257.7 | 296.4 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,667.3 | -12,573.3 | 94.1 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.5 | 7.1 | 3.7 | numerical | move_above_threshold |
| head | universal_credit | 109.8 | 308.4 | 198.6 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10547:ac4c90edc3f68a4a (row 10547) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 870.8 | 0.0 | 0.0 |
| obr_pmd_nov2025:10553:39c2cf71f48d4440 (row 10553) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -9,840.0 | -12,663.9 | -12,566.1 |
| obr_pmd_nov2025:10559:25df56e9c429d3de (row 10559) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -622.5 | — | — |
| obr_pmd_nov2025:10565:b5bfc5a7ff82833c (row 10565) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21466:43674024394e1bc0 (row 21466) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 180.1 | 109.8 | 308.4 |
| obr_pmd_nov2025:21472:b09d4425f46fcb57 (row 21472) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 8.0 | — | — |
| obr_pmd_nov2025:21478:88af641dd7a06883 (row 21478) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 78.4 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028.json` (sha256 `dbba07087b94a010171734d05d12b7fa4b4fa455889ac999140ba4d014a80ed5`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028.json` (sha256 `d8f4627d8e1d102d8cf7503cd4391495464512b6d1980a461ce84863ea2f0a4b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
