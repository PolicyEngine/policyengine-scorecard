# Investigation packet: autumn_budget_2025 / ab2025__health_and_disability_benefits_operations / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Health and Disability Benefits: Improve operations by increasing face-to-face assessments, increasing WCA reassessment capability, and PIP award review changes, starting from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23606:fcd53df4e36de0e3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23612:63827cc9efa731f1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23618:153bd55ebb4df1d3 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23606:fcd53df4e36de0e3 (row 23606) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 609.3 | — | — |
| head | obr_pmd_nov2025:23612:63827cc9efa731f1 (row 23612) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -125.0 | — | — |
| head | obr_pmd_nov2025:23618:153bd55ebb4df1d3 (row 23618) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 37.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__health_and_disability_benefits_operations --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__health_and_disability_benefits_operations_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
