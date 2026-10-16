# Investigation packet: autumn_budget_2025 / ab2025__business_rates_transitional_relief_and_supplement / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce both a three year Transitional Relief scheme, partially funded by a 1p Transitional Relief Supplement in 2026/27, and a Supporting Small Business scheme from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12118:e7dbf792e8878d27 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12124:993d9a1548bf2980 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12130:780e154153fc8637 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12136:a44a56692b7ca514 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23649:ced124f81fc9443c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23655:7e0aaa355393f716 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23661:b6193921058bc57e | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12118:e7dbf792e8878d27 (row 12118) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Business rates | 0.0 | — | — |
| head | obr_pmd_nov2025:12124:993d9a1548bf2980 (row 12124) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 13.0 | — | — |
| head | obr_pmd_nov2025:12130:780e154153fc8637 (row 12130) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 2.0 | — | — |
| head | obr_pmd_nov2025:12136:a44a56692b7ca514 (row 12136) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:23649:ced124f81fc9443c (row 23649) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23655:7e0aaa355393f716 (row 23655) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23661:b6193921058bc57e (row 23661) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other AME (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_transitional_relief_and_supplement --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_transitional_relief_and_supplement_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
