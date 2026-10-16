# Investigation packet: autumn_budget_2025 / ab2025__writing_down_allowances_14pct_and_40pct_fya / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Writing-down Allowances: Reduce the main rate writing-down allowance to 14% from April 2026 and introduce a new 40% first-year allowance from 1 January 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12412:d244a6c873324e6e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12418:33f8ea583865ba15 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12424:122fcc008070f143 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24003:cc2ce3fa9145aaa8 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12412:d244a6c873324e6e (row 12412) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Bank surcharge | 3.0 | — | — |
| head | obr_pmd_nov2025:12418:33f8ea583865ba15 (row 12418) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 9.0 | — | — |
| head | obr_pmd_nov2025:12424:122fcc008070f143 (row 12424) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 1,458.0 | — | — |
| head | obr_pmd_nov2025:24003:cc2ce3fa9145aaa8 (row 24003) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 1.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__writing_down_allowances_14pct_and_40pct_fya --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__writing_down_allowances_14pct_and_40pct_fya_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
