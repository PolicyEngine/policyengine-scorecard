# Investigation packet: autumn_budget_2025 / ab2025__business_rates_transitional_relief_and_supplement / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce both a three year Transitional Relief scheme, partially funded by a 1p Transitional Relief Supplement in 2026/27, and a Supporting Small Business scheme from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12117:5fa20f19609e9a7a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12123:0632257ef9dc5665 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12129:d1d0161097d93127 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12135:21a38d3223adbf61 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23648:ee6c74c0cca1d898 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23654:75d5fe4848618fbc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23660:de167f73c73604c0 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12117:5fa20f19609e9a7a (row 12117) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Business rates | -843.0 | — | — |
| head | obr_pmd_nov2025:12123:0632257ef9dc5665 (row 12123) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 23.8 | — | — |
| head | obr_pmd_nov2025:12129:d1d0161097d93127 (row 12129) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 5.1 | — | — |
| head | obr_pmd_nov2025:12135:21a38d3223adbf61 (row 12135) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 93.0 | — | — |
| head | obr_pmd_nov2025:23648:ee6c74c0cca1d898 (row 23648) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -161.4 | — | — |
| head | obr_pmd_nov2025:23654:75d5fe4848618fbc (row 23654) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Locally-financed current expenditure | 514.0 | — | — |
| head | obr_pmd_nov2025:23660:de167f73c73604c0 (row 23660) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Other AME (current) | -514.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_transitional_relief_and_supplement --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_transitional_relief_and_supplement_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
