# Investigation packet: autumn_budget_2025 / ab2025__health_and_disability_benefits_operations / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Health and Disability Benefits: Improve operations by increasing face-to-face assessments, increasing WCA reassessment capability, and PIP award review changes, starting from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23603:84c256ec61b86be4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23609:9a68d10cd41266fc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23615:b47fd78d3b45e22d | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23603:84c256ec61b86be4 (row 23603) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:23609:9a68d10cd41266fc (row 23609) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:23615:b47fd78d3b45e22d (row 23615) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__health_and_disability_benefits_operations --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__health_and_disability_benefits_operations_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
