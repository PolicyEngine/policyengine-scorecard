# Investigation packet: autumn_budget_2025 / ab2025__business_rates_transitional_relief_and_supplement / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce both a three year Transitional Relief scheme, partially funded by a 1p Transitional Relief Supplement in 2026/27, and a Supporting Small Business scheme from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12115:95603c4f9037eebd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12121:309e53b8ea3096a5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12127:a89ba82f3c58a77f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12133:d339e47869edd070 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23646:75d57b1fb9860038 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23652:2df21f5069f27f96 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23658:529f4f8acd07fe72 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12115:95603c4f9037eebd (row 12115) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Business rates | -2,026.0 | — | — |
| head | obr_pmd_nov2025:12121:309e53b8ea3096a5 (row 12121) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12127:a89ba82f3c58a77f (row 12127) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 0.0 | — | — |
| head | obr_pmd_nov2025:12133:d339e47869edd070 (row 12133) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 272.1 | — | — |
| head | obr_pmd_nov2025:23646:75d57b1fb9860038 (row 23646) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -387.9 | — | — |
| head | obr_pmd_nov2025:23652:2df21f5069f27f96 (row 23652) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Locally-financed current expenditure | 1,236.0 | — | — |
| head | obr_pmd_nov2025:23658:529f4f8acd07fe72 (row 23658) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other AME (current) | -1,236.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_transitional_relief_and_supplement --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_transitional_relief_and_supplement_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
