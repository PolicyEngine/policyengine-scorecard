# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23319:c6ce8500db20415e | 1,172.0 | 1,186.7 | 14.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23325:2a220260e99cd7fb | — | — | — | — | — |
| measure_year | total | 1,172.0 | 1,186.7 | 14.6 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | 1,172.0 | 1,186.7 | 14.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23319:c6ce8500db20415e (row 23319) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 2,328.4 | 1,172.0 | 1,186.7 |
| base | obr_pmd_nov2025:23325:2a220260e99cd7fb (row 23325) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -33.9 | — | — |
| head | obr_pmd_nov2025:23319:c6ce8500db20415e (row 23319) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 2,328.4 | 1,172.0 | 1,186.7 |
| head | obr_pmd_nov2025:23325:2a220260e99cd7fb (row 23325) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -33.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028.json` (sha256 `5bddef450bd92eb78bf536fc36a046299cebad964961f03c434070651001a607`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028.json` (sha256 `d728221ff79ba23785cb472dffaab1487df1a4fc5a2f5cb7aca5725f0b70c83e`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
