# Investigation packet: autumn_budget_2025 / ab2025__non_reimbursed_homeworking_expenses_relief_removed / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Non-reimbursed Homeworking Expenses: Remove the tax relief available from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12578:154aec15d933d774 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24037:d66e0fec9bbcadc0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24043:b8a52e14e8db5fb0 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12578:154aec15d933d774 (row 12578) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 28.6 | — | — |
| head | obr_pmd_nov2025:24037:d66e0fec9bbcadc0 (row 24037) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.3 | — | — |
| head | obr_pmd_nov2025:24043:b8a52e14e8db5fb0 (row 24043) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 2.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__non_reimbursed_homeworking_expenses_relief_removed --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__non_reimbursed_homeworking_expenses_relief_removed_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
