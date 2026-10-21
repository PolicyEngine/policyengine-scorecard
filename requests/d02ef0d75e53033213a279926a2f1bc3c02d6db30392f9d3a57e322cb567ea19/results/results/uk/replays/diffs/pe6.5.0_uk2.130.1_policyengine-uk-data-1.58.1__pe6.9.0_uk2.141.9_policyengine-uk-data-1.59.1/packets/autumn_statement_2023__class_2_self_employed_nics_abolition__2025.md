# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10592:e5c257a04708cde7 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10598:28f9366b82391330 | -459.3 | -473.9 | -14.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10604:2e41723e31096d04 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10610:e82a65922591db12 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21499:909bf2ab3554e230 | 39.5 | 38.4 | -1.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21505:374cb2da46d104d4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21511:69ca865721717cf1 | — | — | — | — | — |
| measure_year | total | -419.8 | -435.5 | -15.7 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -459.3 | -473.9 | -14.6 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 39.5 | 38.4 | -1.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10592:e5c257a04708cde7 (row 10592) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 1.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10598:28f9366b82391330 (row 10598) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -350.1 | -459.3 | -473.9 |
| base | obr_pmd_nov2025:10604:2e41723e31096d04 (row 10604) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -120.3 | — | — |
| base | obr_pmd_nov2025:10610:e82a65922591db12 (row 10610) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21499:909bf2ab3554e230 (row 21499) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 39.5 | 38.4 |
| base | obr_pmd_nov2025:21505:374cb2da46d104d4 (row 21505) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.1 | — | — |
| base | obr_pmd_nov2025:21511:69ca865721717cf1 (row 21511) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -0.1 | — | — |
| head | obr_pmd_nov2025:10592:e5c257a04708cde7 (row 10592) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 1.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10598:28f9366b82391330 (row 10598) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -350.1 | -459.3 | -473.9 |
| head | obr_pmd_nov2025:10604:2e41723e31096d04 (row 10604) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -120.3 | — | — |
| head | obr_pmd_nov2025:10610:e82a65922591db12 (row 10610) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21499:909bf2ab3554e230 (row 21499) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 39.5 | 38.4 |
| head | obr_pmd_nov2025:21505:374cb2da46d104d4 (row 21505) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.1 | — | — |
| head | obr_pmd_nov2025:21511:69ca865721717cf1 (row 21511) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -0.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2025.json` (sha256 `838b15e73296ba7aeac986a1126219e2bd95bba1bcafe23095134c028ccb3888`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2025.json` (sha256 `639893d57a0ea24ae262cf25abe77bac41e3a73bf5f5ad44562de109b9377c12`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2025
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
