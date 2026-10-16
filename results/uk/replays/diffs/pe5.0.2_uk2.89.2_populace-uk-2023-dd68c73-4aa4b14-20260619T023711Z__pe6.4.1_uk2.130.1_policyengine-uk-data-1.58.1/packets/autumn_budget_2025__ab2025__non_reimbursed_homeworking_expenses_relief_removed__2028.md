# Investigation packet: autumn_budget_2025 / ab2025__non_reimbursed_homeworking_expenses_relief_removed / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Non-reimbursed Homeworking Expenses: Remove the tax relief available from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12579:9cbd078a78670fa1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24038:72ad626d320bdc50 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24044:22770f50ab8ffbea | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12579:9cbd078a78670fa1 (row 12579) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 22.8 | — | — |
| head | obr_pmd_nov2025:24038:72ad626d320bdc50 (row 24038) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.2 | — | — |
| head | obr_pmd_nov2025:24044:22770f50ab8ffbea (row 24044) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 1.6 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__non_reimbursed_homeworking_expenses_relief_removed --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__non_reimbursed_homeworking_expenses_relief_removed_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
