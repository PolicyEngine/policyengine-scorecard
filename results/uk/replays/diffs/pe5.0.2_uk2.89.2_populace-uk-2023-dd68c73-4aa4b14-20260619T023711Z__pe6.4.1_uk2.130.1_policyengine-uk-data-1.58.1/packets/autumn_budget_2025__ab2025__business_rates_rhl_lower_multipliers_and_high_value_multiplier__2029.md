# Investigation packet: autumn_budget_2025 / ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce two new lower multipliers for eligible retail, hospitality and leisure properties funded by a new high-value multiplier from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12142:b040aec451138a46 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12148:de078921d50bc912 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12154:b49b9ec252821534 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12160:28604b116a593dc1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23667:9603969948beddca | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23673:7429908588fa3a50 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23679:2fde307c7ecea996 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12142:b040aec451138a46 (row 12142) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Business rates | 31.4 | — | — |
| head | obr_pmd_nov2025:12148:de078921d50bc912 (row 12148) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 16.2 | — | — |
| head | obr_pmd_nov2025:12154:b49b9ec252821534 (row 12154) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3.1 | — | — |
| head | obr_pmd_nov2025:12160:28604b116a593dc1 (row 12160) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -22.9 | — | — |
| head | obr_pmd_nov2025:23667:9603969948beddca (row 23667) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 6.0 | — | — |
| head | obr_pmd_nov2025:23673:7429908588fa3a50 (row 23673) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Locally-financed current expenditure | -17.2 | — | — |
| head | obr_pmd_nov2025:23679:2fde307c7ecea996 (row 23679) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other AME (current) | 17.2 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
