# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10568:d8e11163b163dc62 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10574:46d6b72964d38975 | -343.9 | -355.2 | -11.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10580:3a44cba01461f1ab | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10586:bec769ce8acdb975 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 | 14.6 | 16.0 | 1.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21487:6667d528cfbcc389 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21493:6c678a2f414c3792 | — | — | — | — | — |
| measure_year | total | -329.3 | -339.2 | -9.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -343.9 | -355.2 | -11.2 | numerical | move_above_threshold |
| head | universal_credit | 14.6 | 16.0 | 1.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10568:d8e11163b163dc62 (row 10568) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 18.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10574:46d6b72964d38975 (row 10574) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -323.5 | -343.9 | -355.2 |
| base | obr_pmd_nov2025:10580:3a44cba01461f1ab (row 10580) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -84.8 | — | — |
| base | obr_pmd_nov2025:10586:bec769ce8acdb975 (row 10586) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 (row 21481) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 14.6 | 16.0 |
| base | obr_pmd_nov2025:21487:6667d528cfbcc389 (row 21487) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.1 | — | — |
| base | obr_pmd_nov2025:21493:6c678a2f414c3792 (row 21493) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 1.4 | — | — |
| head | obr_pmd_nov2025:10568:d8e11163b163dc62 (row 10568) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 18.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10574:46d6b72964d38975 (row 10574) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -323.5 | -343.9 | -355.2 |
| head | obr_pmd_nov2025:10580:3a44cba01461f1ab (row 10580) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -84.8 | — | — |
| head | obr_pmd_nov2025:10586:bec769ce8acdb975 (row 10586) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21481:2b2973b0ac23d6e9 (row 21481) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 5.4 | 14.6 | 16.0 |
| head | obr_pmd_nov2025:21487:6667d528cfbcc389 (row 21487) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:21493:6c678a2f414c3792 (row 21493) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 1.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025.json` (sha256 `8238ef5bff034f190523bb2995b995d9b481b05d718c1d6dc851cf61a6ac5ba1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025.json` (sha256 `b694bd4d6e65d7e013ae927d9641aa61e09ae82df799883d9ca34feddb6fd740`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
