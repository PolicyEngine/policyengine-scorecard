# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10590:9fb656d369cf6c02 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10596:482eac698ab9c181 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10602:10fba5ede62ec9a5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10608:8d76207d856fc00c | — | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21497:197a81ed0459bc7d | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21503:210e9e8bada76134 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21509:c5123f714ee54ff9 | — | — | — | — | — |
| measure_year | total | 0.0 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10590:9fb656d369cf6c02 (row 10590) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10596:482eac698ab9c181 (row 10596) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10602:10fba5ede62ec9a5 (row 10602) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| base | obr_pmd_nov2025:10608:8d76207d856fc00c (row 10608) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21497:197a81ed0459bc7d (row 21497) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:21503:210e9e8bada76134 (row 21503) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:21509:c5123f714ee54ff9 (row 21509) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10590:9fb656d369cf6c02 (row 10590) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10596:482eac698ab9c181 (row 10596) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10602:10fba5ede62ec9a5 (row 10602) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:10608:8d76207d856fc00c (row 10608) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21497:197a81ed0459bc7d (row 21497) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:21503:210e9e8bada76134 (row 21503) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:21509:c5123f714ee54ff9 (row 21509) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2023.json` (sha256 `3e4a62564a5dcfe270f748c3922b225362aac7d4960c7e793589a1abfba604ce`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2023
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
