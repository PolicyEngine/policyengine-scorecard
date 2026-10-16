# Investigation packet: autumn_budget_2025 / ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce two new lower multipliers for eligible retail, hospitality and leisure properties funded by a new high-value multiplier from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12138:29edd34b16460548 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12144:2cd41ec9f17ba80a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12150:a04cf0f76a09ce06 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12156:1636bb1429a3e00a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23663:e6ff42b91f753547 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23669:12f6f13c23b9cfc2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23675:517450fa7a3a4792 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12138:29edd34b16460548 (row 12138) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Business rates | -2.9 | — | — |
| head | obr_pmd_nov2025:12144:2cd41ec9f17ba80a (row 12144) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12150:a04cf0f76a09ce06 (row 12150) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 0.0 | — | — |
| head | obr_pmd_nov2025:12156:1636bb1429a3e00a (row 12156) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 1.6 | — | — |
| head | obr_pmd_nov2025:23663:e6ff42b91f753547 (row 23663) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.6 | — | — |
| head | obr_pmd_nov2025:23669:12f6f13c23b9cfc2 (row 23669) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23675:517450fa7a3a4792 (row 23675) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other AME (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
