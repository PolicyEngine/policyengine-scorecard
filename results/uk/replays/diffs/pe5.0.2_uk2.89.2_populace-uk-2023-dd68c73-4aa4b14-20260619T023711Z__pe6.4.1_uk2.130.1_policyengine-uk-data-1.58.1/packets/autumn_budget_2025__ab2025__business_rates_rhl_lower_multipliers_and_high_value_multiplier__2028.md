# Investigation packet: autumn_budget_2025 / ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce two new lower multipliers for eligible retail, hospitality and leisure properties funded by a new high-value multiplier from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12141:20ff4a4e84d4354f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12147:61698b7debaf0a15 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12153:01a3574b35124ea7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12159:3b975ad45201533e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23666:a3b10dc4e33de161 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23672:523114267babffd1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23678:c94c3ed3310bd3e9 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12141:20ff4a4e84d4354f (row 12141) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Business rates | 31.5 | — | — |
| head | obr_pmd_nov2025:12147:61698b7debaf0a15 (row 12147) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 16.2 | — | — |
| head | obr_pmd_nov2025:12153:01a3574b35124ea7 (row 12153) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 3.1 | — | — |
| head | obr_pmd_nov2025:12159:3b975ad45201533e (row 12159) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -22.4 | — | — |
| head | obr_pmd_nov2025:23666:a3b10dc4e33de161 (row 23666) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 6.0 | — | — |
| head | obr_pmd_nov2025:23672:523114267babffd1 (row 23672) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Locally-financed current expenditure | -19.5 | — | — |
| head | obr_pmd_nov2025:23678:c94c3ed3310bd3e9 (row 23678) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Other AME (current) | 19.5 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
