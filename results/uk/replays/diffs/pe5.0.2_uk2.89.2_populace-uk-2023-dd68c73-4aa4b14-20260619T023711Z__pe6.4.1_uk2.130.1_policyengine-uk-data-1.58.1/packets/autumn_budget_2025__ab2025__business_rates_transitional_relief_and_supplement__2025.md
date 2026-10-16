# Investigation packet: autumn_budget_2025 / ab2025__business_rates_transitional_relief_and_supplement / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce both a three year Transitional Relief scheme, partially funded by a 1p Transitional Relief Supplement in 2026/27, and a Supporting Small Business scheme from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12114:b297e77c2623274b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12120:e3db573a8a005731 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12126:23c1bcefc917b39c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12132:fa9d58c81917a6b4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23645:d8d2c193e950efd5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23651:b6e0135f5c59f4ba | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23657:7f197afda64059d5 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12114:b297e77c2623274b (row 12114) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Business rates | 0.0 | — | — |
| head | obr_pmd_nov2025:12120:e3db573a8a005731 (row 12120) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12126:23c1bcefc917b39c (row 12126) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 0.0 | — | — |
| head | obr_pmd_nov2025:12132:fa9d58c81917a6b4 (row 12132) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 39.9 | — | — |
| head | obr_pmd_nov2025:23645:d8d2c193e950efd5 (row 23645) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23651:b6e0135f5c59f4ba (row 23651) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23657:7f197afda64059d5 (row 23657) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other AME (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_transitional_relief_and_supplement --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_transitional_relief_and_supplement_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
