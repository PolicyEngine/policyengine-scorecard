# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10547:ac4c90edc3f68a4a | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10553:39c2cf71f48d4440 | -12,442.4 | -12,477.1 | -34.6 | — | — |
| source_row | obr_pmd_nov2025:10559:25df56e9c429d3de | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10565:b5bfc5a7ff82833c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21466:43674024394e1bc0 | 303.4 | 309.2 | 5.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21472:b09d4425f46fcb57 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21478:88af641dd7a06883 | — | — | — | — | — |
| measure_year | total | -12,139.0 | -12,167.8 | -28.8 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,449.9 | -12,484.7 | -34.8 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 7.4 | 7.6 | 0.2 | — | — |
| head | universal_credit | 303.4 | 309.2 | 5.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10547:ac4c90edc3f68a4a (row 10547) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 870.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10553:39c2cf71f48d4440 (row 10553) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -9,840.0 | -12,442.4 | -12,477.1 |
| base | obr_pmd_nov2025:10559:25df56e9c429d3de (row 10559) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -622.5 | — | — |
| base | obr_pmd_nov2025:10565:b5bfc5a7ff82833c (row 10565) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21466:43674024394e1bc0 (row 21466) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 180.1 | 303.4 | 309.2 |
| base | obr_pmd_nov2025:21472:b09d4425f46fcb57 (row 21472) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 8.0 | — | — |
| base | obr_pmd_nov2025:21478:88af641dd7a06883 (row 21478) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 78.4 | — | — |
| head | obr_pmd_nov2025:10547:ac4c90edc3f68a4a (row 10547) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 870.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10553:39c2cf71f48d4440 (row 10553) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -9,840.0 | -12,442.4 | -12,477.1 |
| head | obr_pmd_nov2025:10559:25df56e9c429d3de (row 10559) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -622.5 | — | — |
| head | obr_pmd_nov2025:10565:b5bfc5a7ff82833c (row 10565) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21466:43674024394e1bc0 (row 21466) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 180.1 | 303.4 | 309.2 |
| head | obr_pmd_nov2025:21472:b09d4425f46fcb57 (row 21472) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 8.0 | — | — |
| head | obr_pmd_nov2025:21478:88af641dd7a06883 (row 21478) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 78.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028.json` (sha256 `d9b8fcb518a3d197926ff376b4b263d3339be55ebba4f0f818dcd2d2bedc5d27`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028.json` (sha256 `44157ecae4c71242dda873e4d73100ca9e73c048587ee518996de52714a16fc3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
