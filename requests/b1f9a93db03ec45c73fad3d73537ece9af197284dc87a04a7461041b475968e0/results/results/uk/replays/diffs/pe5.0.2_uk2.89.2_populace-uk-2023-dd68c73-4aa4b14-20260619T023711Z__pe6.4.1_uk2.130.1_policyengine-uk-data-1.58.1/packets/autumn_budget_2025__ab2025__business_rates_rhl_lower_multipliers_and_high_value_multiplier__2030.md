# Investigation packet: autumn_budget_2025 / ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce two new lower multipliers for eligible retail, hospitality and leisure properties funded by a new high-value multiplier from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12143:d35d40c4b97b2944 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12149:3076e2aea9d6a237 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12155:87fc96014f9a8ce1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12161:560c0e5e5d795172 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23668:ca598a45756bff3a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23674:502419d2560889ad | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23680:06bcf16e369a3578 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12143:d35d40c4b97b2944 (row 12143) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Business rates | 31.4 | — | — |
| head | obr_pmd_nov2025:12149:3076e2aea9d6a237 (row 12149) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 16.2 | — | — |
| head | obr_pmd_nov2025:12155:87fc96014f9a8ce1 (row 12155) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 3.1 | — | — |
| head | obr_pmd_nov2025:12161:560c0e5e5d795172 (row 12161) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -22.5 | — | — |
| head | obr_pmd_nov2025:23668:ca598a45756bff3a (row 23668) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 6.0 | — | — |
| head | obr_pmd_nov2025:23674:502419d2560889ad (row 23674) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Locally-financed current expenditure | -17.2 | — | — |
| head | obr_pmd_nov2025:23680:06bcf16e369a3578 (row 23680) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Other AME (current) | 17.2 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
