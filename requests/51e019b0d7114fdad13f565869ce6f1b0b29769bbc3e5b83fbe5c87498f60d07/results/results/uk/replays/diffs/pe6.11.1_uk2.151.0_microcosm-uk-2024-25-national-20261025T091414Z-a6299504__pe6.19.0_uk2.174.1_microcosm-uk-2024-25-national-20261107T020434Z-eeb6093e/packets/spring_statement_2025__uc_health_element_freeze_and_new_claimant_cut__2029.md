# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23320:4c41d84635ed82ad | 1,603.1 | 1,424.4 | -178.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23326:9e0a9cbad29c3f53 | — | — | — | — | — |
| measure_year | total | 1,603.1 | 1,424.4 | -178.7 | numerical | move_above_threshold |
| head | universal_credit | 1,603.1 | 1,424.4 | -178.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23320:4c41d84635ed82ad (row 23320) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 3,053.5 | 1,603.1 | 1,424.4 |
| base | obr_pmd_nov2025:23326:9e0a9cbad29c3f53 (row 23326) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -46.0 | — | — |
| head | obr_pmd_nov2025:23320:4c41d84635ed82ad (row 23320) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 3,053.5 | 1,603.1 | 1,424.4 |
| head | obr_pmd_nov2025:23326:9e0a9cbad29c3f53 (row 23326) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -46.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2029.json` (sha256 `14198167173d7bc36d34c7888b8b18b34188d909210c7cf54fef7b3a435f7c39`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2029.json` (sha256 `3226f4f82ee2642976a43948fe27347291d09cf35d4fa322bb750ece03d4e9af`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
