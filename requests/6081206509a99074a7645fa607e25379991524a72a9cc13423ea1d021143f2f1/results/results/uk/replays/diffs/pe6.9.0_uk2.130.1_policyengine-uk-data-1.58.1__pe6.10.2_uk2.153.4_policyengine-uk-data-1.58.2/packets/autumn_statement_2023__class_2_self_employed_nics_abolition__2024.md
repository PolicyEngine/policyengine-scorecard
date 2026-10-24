# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10591:06c2501422284995 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10597:37b420855b7005a0 | -444.4 | -442.9 | 1.5 | — | — |
| source_row | obr_pmd_nov2025:10603:f988dfb34cc38104 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10609:0bf03e9f919bfbae | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21498:3fa4108a7eac0a15 | 39.3 | 38.1 | -1.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21504:11aac6da7a06d654 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21510:f7365b6a93fbe4c8 | — | — | — | — | — |
| measure_year | total | -405.1 | -404.8 | 0.3 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -444.4 | -442.9 | 1.5 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 39.3 | 38.1 | -1.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10591:06c2501422284995 (row 10591) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10597:37b420855b7005a0 (row 10597) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -348.7 | -444.4 | -442.9 |
| base | obr_pmd_nov2025:10603:f988dfb34cc38104 (row 10603) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -36.8 | — | — |
| base | obr_pmd_nov2025:10609:0bf03e9f919bfbae (row 10609) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21498:3fa4108a7eac0a15 (row 21498) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 39.3 | 38.1 |
| base | obr_pmd_nov2025:21504:11aac6da7a06d654 (row 21504) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:21510:f7365b6a93fbe4c8 (row 21510) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10591:06c2501422284995 (row 10591) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10597:37b420855b7005a0 (row 10597) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -348.7 | -444.4 | -442.9 |
| head | obr_pmd_nov2025:10603:f988dfb34cc38104 (row 10603) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -36.8 | — | — |
| head | obr_pmd_nov2025:10609:0bf03e9f919bfbae (row 10609) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21498:3fa4108a7eac0a15 (row 21498) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 39.3 | 38.1 |
| head | obr_pmd_nov2025:21504:11aac6da7a06d654 (row 21504) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:21510:f7365b6a93fbe4c8 (row 21510) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024.json` (sha256 `e0390cd253e1f336ccb8d7e7af7f3ac205e209000426f1f28dfa0115de3f9d4e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024.json` (sha256 `fc4baa353750be8c3ab6009f1e683346e6197ee0227baa551babf79d3adfe699`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2024
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
