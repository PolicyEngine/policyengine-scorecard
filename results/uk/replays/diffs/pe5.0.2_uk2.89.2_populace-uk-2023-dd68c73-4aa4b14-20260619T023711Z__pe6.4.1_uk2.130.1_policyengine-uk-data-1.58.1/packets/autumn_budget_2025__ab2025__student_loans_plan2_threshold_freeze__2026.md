# Investigation packet: autumn_budget_2025 / ab2025__student_loans_plan2_threshold_freeze / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Student Loans: Freeze Plan 2 repayment threshold for three years from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12271:2c2d8ba3bd19be94 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23940:041012f7de44ed80 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12271:2c2d8ba3bd19be94 (row 12271) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Interest and dividend receipts | 275.0 | — | — |
| head | obr_pmd_nov2025:23940:041012f7de44ed80 (row 23940) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Student loans | 5,640.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__student_loans_plan2_threshold_freeze --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__student_loans_plan2_threshold_freeze_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
