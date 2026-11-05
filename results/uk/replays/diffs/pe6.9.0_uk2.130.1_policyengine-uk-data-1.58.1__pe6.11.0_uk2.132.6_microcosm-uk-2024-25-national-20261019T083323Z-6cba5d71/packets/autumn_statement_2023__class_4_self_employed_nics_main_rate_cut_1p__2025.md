# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10568:d8e11163b163dc62 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10574:46d6b72964d38975 | -330.7 | -346.4 | -15.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10580:3a44cba01461f1ab | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10586:bec769ce8acdb975 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 | 20.9 | 14.2 | -6.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21487:6667d528cfbcc389 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21493:6c678a2f414c3792 | — | — | — | — | — |
| measure_year | total | -309.7 | -332.2 | -22.5 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -330.7 | -346.4 | -15.8 | numerical | move_above_threshold |
| head | universal_credit | 20.9 | 14.2 | -6.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10568:d8e11163b163dc62 (row 10568) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 18.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10574:46d6b72964d38975 (row 10574) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -323.5 | -330.7 | -346.4 |
| base | obr_pmd_nov2025:10580:3a44cba01461f1ab (row 10580) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -84.8 | — | — |
| base | obr_pmd_nov2025:10586:bec769ce8acdb975 (row 10586) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 (row 21481) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 20.9 | 14.2 |
| base | obr_pmd_nov2025:21487:6667d528cfbcc389 (row 21487) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.1 | — | — |
| base | obr_pmd_nov2025:21493:6c678a2f414c3792 (row 21493) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 1.4 | — | — |
| head | obr_pmd_nov2025:10568:d8e11163b163dc62 (row 10568) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 18.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10574:46d6b72964d38975 (row 10574) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -323.5 | -330.7 | -346.4 |
| head | obr_pmd_nov2025:10580:3a44cba01461f1ab (row 10580) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -84.8 | — | — |
| head | obr_pmd_nov2025:10586:bec769ce8acdb975 (row 10586) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 (row 21481) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 20.9 | 14.2 |
| head | obr_pmd_nov2025:21487:6667d528cfbcc389 (row 21487) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:21493:6c678a2f414c3792 (row 21493) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 1.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025.json` (sha256 `7e49b92df4520c98c569f745b9f0493af2c18ec5f2554d4722baa3bc83cadb6c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025.json` (sha256 `9301cfc48880be31806236eb2f074ea63a68bded07913978b5f38633c7c8613d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
