# Investigation packet: autumn_budget_2025 / ab2025__writing_down_allowances_14pct_and_40pct_fya / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Writing-down Allowances: Reduce the main rate writing-down allowance to 14% from April 2026 and introduce a new 40% first-year allowance from 1 January 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12408:c2a8ee041a5298f5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12414:15d1cbca84d98995 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12420:f4006c6836d91b4b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23999:8b2fdb6fc3c7e0ba | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12408:c2a8ee041a5298f5 (row 12408) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Bank surcharge | 0.0 | — | — |
| head | obr_pmd_nov2025:12414:15d1cbca84d98995 (row 12414) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12420:f4006c6836d91b4b (row 12420) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 33.0 | — | — |
| head | obr_pmd_nov2025:23999:8b2fdb6fc3c7e0ba (row 23999) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__writing_down_allowances_14pct_and_40pct_fya --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__writing_down_allowances_14pct_and_40pct_fya_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
