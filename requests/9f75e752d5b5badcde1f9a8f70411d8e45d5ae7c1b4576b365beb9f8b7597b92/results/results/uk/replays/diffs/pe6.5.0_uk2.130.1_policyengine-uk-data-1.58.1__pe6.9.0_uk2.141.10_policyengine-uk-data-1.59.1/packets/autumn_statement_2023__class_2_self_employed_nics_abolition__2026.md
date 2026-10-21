# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10593:f37c77d805ce9401 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10599:0cdd3c6417e28a14 | -455.0 | -469.6 | -14.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10605:e8520c5b5437234d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10611:c9463e33b6dd399f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21500:3cd35347ee5fc266 | 37.5 | 36.4 | -1.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21506:b8ab58b536a1ad7f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21512:54f73d621c17378e | — | — | — | — | — |
| measure_year | total | -417.5 | -433.3 | -15.8 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -455.0 | -469.6 | -14.6 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 37.5 | 36.4 | -1.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10593:f37c77d805ce9401 (row 10593) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 141.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10599:0cdd3c6417e28a14 (row 10599) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -358.4 | -455.0 | -469.6 |
| base | obr_pmd_nov2025:10605:e8520c5b5437234d (row 10605) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -186.7 | — | — |
| base | obr_pmd_nov2025:10611:c9463e33b6dd399f (row 10611) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21500:3cd35347ee5fc266 (row 21500) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 37.5 | 36.4 |
| base | obr_pmd_nov2025:21506:b8ab58b536a1ad7f (row 21506) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.5 | — | — |
| base | obr_pmd_nov2025:21512:54f73d621c17378e (row 21512) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 13.4 | — | — |
| head | obr_pmd_nov2025:10593:f37c77d805ce9401 (row 10593) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 141.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10599:0cdd3c6417e28a14 (row 10599) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -358.4 | -455.0 | -469.6 |
| head | obr_pmd_nov2025:10605:e8520c5b5437234d (row 10605) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -186.7 | — | — |
| head | obr_pmd_nov2025:10611:c9463e33b6dd399f (row 10611) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21500:3cd35347ee5fc266 (row 21500) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 37.5 | 36.4 |
| head | obr_pmd_nov2025:21506:b8ab58b536a1ad7f (row 21506) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.5 | — | — |
| head | obr_pmd_nov2025:21512:54f73d621c17378e (row 21512) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 13.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026.json` (sha256 `cf0efe3888ba8891a15f2d2b3b7103063e493888c8b13942cef2cbdf5cd71230`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026.json` (sha256 `f3e5b0c7aabcba61f9416d8abbf4052f579a17773ec508d58812604511b6b7f8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2026
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
