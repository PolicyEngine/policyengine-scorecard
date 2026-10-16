# Investigation packet: autumn_budget_2025 / ab2025__business_rates_transitional_relief_and_supplement / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce both a three year Transitional Relief scheme, partially funded by a 1p Transitional Relief Supplement in 2026/27, and a Supporting Small Business scheme from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12119:2d69b7e021ca5ae4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12125:2afa3e3fe885ef9c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12131:0e62ed9994f5c298 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12137:e7f7bb04e629cbb9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23650:af0fce7fbea68d8d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23656:0b489bfb45a4742a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23662:3f0ef3bf25c1f8d5 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12119:2d69b7e021ca5ae4 (row 12119) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Business rates | 0.0 | — | — |
| head | obr_pmd_nov2025:12125:2afa3e3fe885ef9c (row 12125) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -7.0 | — | — |
| head | obr_pmd_nov2025:12131:0e62ed9994f5c298 (row 12131) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | -1.0 | — | — |
| head | obr_pmd_nov2025:12137:e7f7bb04e629cbb9 (row 12137) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:23650:af0fce7fbea68d8d (row 23650) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23656:0b489bfb45a4742a (row 23656) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23662:3f0ef3bf25c1f8d5 (row 23662) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Other AME (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_transitional_relief_and_supplement --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_transitional_relief_and_supplement_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
