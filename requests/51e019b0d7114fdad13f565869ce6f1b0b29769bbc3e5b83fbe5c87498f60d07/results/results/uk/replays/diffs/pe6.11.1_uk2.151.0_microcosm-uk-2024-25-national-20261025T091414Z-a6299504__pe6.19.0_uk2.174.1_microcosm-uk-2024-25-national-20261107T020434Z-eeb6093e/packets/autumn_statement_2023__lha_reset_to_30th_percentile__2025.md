# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21631:75b9415771e2e20c | -1,328.6 | -1,436.8 | -108.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21637:973f5a064b8352ab | — | — | — | — | — |
| measure_year | total | -1,328.6 | -1,436.8 | -108.2 | numerical | move_above_threshold |
| head | housing_benefit | -178.7 | -141.8 | 36.9 | numerical | move_above_threshold |
| head | universal_credit | -1,149.8 | -1,295.0 | -145.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -1,328.6 | -1,436.8 |
| base | obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |
| head | obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -1,328.6 | -1,436.8 |
| head | obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `96e624b5f771f711652384f5aaa8a91e514a348e5c605fc13da597b97fde0a77`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `8967c95b6264a5442a5efc5327819fe8c9b2cba2c15dbfa1a2556fe1b3935b84`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
