# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10591:06c2501422284995 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10597:37b420855b7005a0 | -512.2 | -444.4 | 67.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10603:f988dfb34cc38104 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10609:0bf03e9f919bfbae | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21498:3fa4108a7eac0a15 | 9.7 | 39.3 | 29.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21504:11aac6da7a06d654 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21510:f7365b6a93fbe4c8 | — | — | — | — | — |
| measure_year | total | -502.5 | -405.1 | 97.4 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -512.1 | -444.4 | 67.7 | numerical | move_above_threshold |
| head | ni_class_4 | -0.1 | 0.0 | 0.1 | structural | zero_crossing |
| head | universal_credit | 9.7 | 39.3 | 29.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10591:06c2501422284995 (row 10591) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10597:37b420855b7005a0 (row 10597) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -348.7 | -512.2 | -444.4 |
| base | obr_pmd_nov2025:10603:f988dfb34cc38104 (row 10603) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -36.8 | — | — |
| base | obr_pmd_nov2025:10609:0bf03e9f919bfbae (row 10609) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21498:3fa4108a7eac0a15 (row 21498) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 9.7 | 39.3 |
| base | obr_pmd_nov2025:21504:11aac6da7a06d654 (row 21504) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:21510:f7365b6a93fbe4c8 (row 21510) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10591:06c2501422284995 (row 10591) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10597:37b420855b7005a0 (row 10597) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -348.7 | -512.2 | -444.4 |
| head | obr_pmd_nov2025:10603:f988dfb34cc38104 (row 10603) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -36.8 | — | — |
| head | obr_pmd_nov2025:10609:0bf03e9f919bfbae (row 10609) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21498:3fa4108a7eac0a15 (row 21498) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 9.7 | 39.3 |
| head | obr_pmd_nov2025:21504:11aac6da7a06d654 (row 21504) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:21510:f7365b6a93fbe4c8 (row 21510) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024.json` (sha256 `14eefc6220de65b37bc5cc85ce99871336a44dea94de7bf4cf603598a581e2c2`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024.json` (sha256 `2a0bd017b40139229f84ca199f4dcd545b8ee306d850ba6f14d0f9567d102b07`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
