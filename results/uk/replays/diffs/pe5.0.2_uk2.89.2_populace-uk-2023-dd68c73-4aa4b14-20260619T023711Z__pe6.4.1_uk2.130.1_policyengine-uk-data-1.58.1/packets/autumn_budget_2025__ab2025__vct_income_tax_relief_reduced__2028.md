# Investigation packet: autumn_budget_2025 / ab2025__vct_income_tax_relief_reduced / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Reduce the VCT scheme Income Tax relief from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12201:881693ed0faea105 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23708:c665bda6e0c3ccf7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23714:a1161de3029160de | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12201:881693ed0faea105 (row 12201) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 86.0 | — | — |
| head | obr_pmd_nov2025:23708:c665bda6e0c3ccf7 (row 23708) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 1.0 | — | — |
| head | obr_pmd_nov2025:23714:a1161de3029160de (row 23714) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 6.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_income_tax_relief_reduced --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_income_tax_relief_reduced_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
