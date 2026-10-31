# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10547:ac4c90edc3f68a4a | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10553:39c2cf71f48d4440 | -12,417.4 | -12,198.4 | 218.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10559:25df56e9c429d3de | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10565:b5bfc5a7ff82833c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21466:43674024394e1bc0 | 237.5 | 223.7 | -13.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21472:b09d4425f46fcb57 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21478:88af641dd7a06883 | — | — | — | — | — |
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
| base | obr_pmd_nov2025:10547:ac4c90edc3f68a4a (row 10547) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 870.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10553:39c2cf71f48d4440 (row 10553) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -9,840.0 | -12,417.4 | -12,198.4 |
| base | obr_pmd_nov2025:10559:25df56e9c429d3de (row 10559) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -622.5 | — | — |
| base | obr_pmd_nov2025:10565:b5bfc5a7ff82833c (row 10565) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21466:43674024394e1bc0 (row 21466) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 180.1 | 237.5 | 223.7 |
| base | obr_pmd_nov2025:21472:b09d4425f46fcb57 (row 21472) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 8.0 | — | — |
| base | obr_pmd_nov2025:21478:88af641dd7a06883 (row 21478) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 78.4 | — | — |
| head | obr_pmd_nov2025:10547:ac4c90edc3f68a4a (row 10547) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 870.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10553:39c2cf71f48d4440 (row 10553) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -9,840.0 | -12,417.4 | -12,198.4 |
| head | obr_pmd_nov2025:10559:25df56e9c429d3de (row 10559) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -622.5 | — | — |
| head | obr_pmd_nov2025:10565:b5bfc5a7ff82833c (row 10565) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21466:43674024394e1bc0 (row 21466) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 180.1 | 237.5 | 223.7 |
| head | obr_pmd_nov2025:21472:b09d4425f46fcb57 (row 21472) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 8.0 | — | — |
| head | obr_pmd_nov2025:21478:88af641dd7a06883 (row 21478) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 78.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028.json` (sha256 `1a35bf2cbc42baa260c2565e9fc0025132c9e2bb243ae513493849021700a3c3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028.json` (sha256 `793b696cf382964e871c3c90f89e0d5873b9f7e71d31658bdb30acd6b0c1ec94`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
