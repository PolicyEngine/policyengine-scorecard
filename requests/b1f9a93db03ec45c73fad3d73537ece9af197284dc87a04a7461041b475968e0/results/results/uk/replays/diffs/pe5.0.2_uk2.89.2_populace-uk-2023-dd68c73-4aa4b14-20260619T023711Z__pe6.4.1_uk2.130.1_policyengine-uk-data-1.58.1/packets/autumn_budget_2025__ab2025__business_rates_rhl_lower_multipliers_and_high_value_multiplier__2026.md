# Investigation packet: autumn_budget_2025 / ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce two new lower multipliers for eligible retail, hospitality and leisure properties funded by a new high-value multiplier from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12139:d6efa97ddf121464 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12145:c5150d3f922204ea | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12151:032a6e2e551de9e9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12157:598b098a7db201ba | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23664:7d0cd59ed5ffd23f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23670:320d01eb5696465c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23676:96495bb03656997b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12139:d6efa97ddf121464 (row 12139) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Business rates | 36.6 | — | — |
| head | obr_pmd_nov2025:12145:c5150d3f922204ea (row 12145) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12151:032a6e2e551de9e9 (row 12151) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 0.0 | — | — |
| head | obr_pmd_nov2025:12157:598b098a7db201ba (row 12157) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -22.9 | — | — |
| head | obr_pmd_nov2025:23664:7d0cd59ed5ffd23f (row 23664) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -64.5 | — | — |
| head | obr_pmd_nov2025:23670:320d01eb5696465c (row 23670) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Locally-financed current expenditure | -19.5 | — | — |
| head | obr_pmd_nov2025:23676:96495bb03656997b (row 23676) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other AME (current) | 19.5 | — | — |

## Executed worlds

* base: no artifact
* head: no artifact

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
