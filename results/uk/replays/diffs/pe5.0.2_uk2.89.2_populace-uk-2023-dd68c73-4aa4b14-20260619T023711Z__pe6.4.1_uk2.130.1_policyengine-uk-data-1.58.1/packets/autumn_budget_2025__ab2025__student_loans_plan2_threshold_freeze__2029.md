# Investigation packet: autumn_budget_2025 / ab2025__student_loans_plan2_threshold_freeze / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Student Loans: Freeze Plan 2 repayment threshold for three years from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12274:e5de6d75ca9d0e40 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23943:f77e9b8d21c3a0a8 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12274:e5de6d75ca9d0e40 (row 12274) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Interest and dividend receipts | 420.0 | — | — |
| head | obr_pmd_nov2025:23943:f77e9b8d21c3a0a8 (row 23943) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Student loans | -63.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__student_loans_plan2_threshold_freeze --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__student_loans_plan2_threshold_freeze_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
