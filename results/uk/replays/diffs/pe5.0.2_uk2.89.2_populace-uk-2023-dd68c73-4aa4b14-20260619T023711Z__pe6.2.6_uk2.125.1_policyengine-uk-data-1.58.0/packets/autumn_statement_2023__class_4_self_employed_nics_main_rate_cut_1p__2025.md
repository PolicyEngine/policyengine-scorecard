# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10568:d8e11163b163dc62 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10574:46d6b72964d38975 | -564.7 | -310.6 | 254.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10580:3a44cba01461f1ab | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10586:bec769ce8acdb975 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 | 6.3 | 20.2 | 13.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21487:6667d528cfbcc389 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21493:6c678a2f414c3792 | — | — | — | — | — |
| measure_year | total | -558.3 | -290.5 | 267.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -564.7 | -310.6 | 254.1 | numerical | move_above_threshold |
| head | universal_credit | 6.3 | 20.2 | 13.8 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10568:d8e11163b163dc62 (row 10568) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 18.9 | 0.0 | 0.0 |
| obr_pmd_nov2025:10574:46d6b72964d38975 (row 10574) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -323.5 | -564.7 | -310.6 |
| obr_pmd_nov2025:10580:3a44cba01461f1ab (row 10580) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -84.8 | — | — |
| obr_pmd_nov2025:10586:bec769ce8acdb975 (row 10586) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21481:2b2973b0ac23d6e9 (row 21481) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 6.3 | 20.2 |
| obr_pmd_nov2025:21487:6667d528cfbcc389 (row 21487) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.1 | — | — |
| obr_pmd_nov2025:21493:6c678a2f414c3792 (row 21493) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 1.4 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025.json` (sha256 `fab7fbd151a2ec9da57c5ba3f1083cbd2001d2c9a1418821cf99aa727258bb9d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025.json` (sha256 `8b2e20fb5be5de219b87fd9f6796c942d28d9786511b4eed82a3177ac9b4c98d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
