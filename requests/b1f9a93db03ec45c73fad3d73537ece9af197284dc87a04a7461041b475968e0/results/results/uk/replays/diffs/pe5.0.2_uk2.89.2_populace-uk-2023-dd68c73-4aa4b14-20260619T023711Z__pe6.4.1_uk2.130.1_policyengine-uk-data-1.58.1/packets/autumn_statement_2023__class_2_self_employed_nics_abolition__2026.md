# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10593:f37c77d805ce9401 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10599:0cdd3c6417e28a14 | -542.5 | -455.0 | 87.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10605:e8520c5b5437234d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10611:c9463e33b6dd399f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21500:3cd35347ee5fc266 | 11.4 | 37.5 | 26.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21506:b8ab58b536a1ad7f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21512:54f73d621c17378e | — | — | — | — | — |
| measure_year | total | -531.1 | -417.5 | 113.6 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -542.5 | -455.0 | 87.5 | numerical | move_above_threshold |
| head | ni_class_4 | -0.0 | 0.0 | 0.0 | structural | zero_crossing |
| head | universal_credit | 11.4 | 37.5 | 26.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10593:f37c77d805ce9401 (row 10593) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 141.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10599:0cdd3c6417e28a14 (row 10599) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -358.4 | -542.5 | -455.0 |
| base | obr_pmd_nov2025:10605:e8520c5b5437234d (row 10605) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -186.7 | — | — |
| base | obr_pmd_nov2025:10611:c9463e33b6dd399f (row 10611) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21500:3cd35347ee5fc266 (row 21500) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 11.4 | 37.5 |
| base | obr_pmd_nov2025:21506:b8ab58b536a1ad7f (row 21506) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.5 | — | — |
| base | obr_pmd_nov2025:21512:54f73d621c17378e (row 21512) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 13.4 | — | — |
| head | obr_pmd_nov2025:10593:f37c77d805ce9401 (row 10593) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 141.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10599:0cdd3c6417e28a14 (row 10599) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -358.4 | -542.5 | -455.0 |
| head | obr_pmd_nov2025:10605:e8520c5b5437234d (row 10605) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -186.7 | — | — |
| head | obr_pmd_nov2025:10611:c9463e33b6dd399f (row 10611) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21500:3cd35347ee5fc266 (row 21500) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 11.4 | 37.5 |
| head | obr_pmd_nov2025:21506:b8ab58b536a1ad7f (row 21506) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.5 | — | — |
| head | obr_pmd_nov2025:21512:54f73d621c17378e (row 21512) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 13.4 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026.json` (sha256 `5848a23c568097954f5aa4d814fea0101c088492cfc483782b1e580f5823f587`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026.json` (sha256 `1fdf846383ce3a93441598a5d0d00c38d7ae9ff2f052a81351b46138d523697f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
