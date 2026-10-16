# Investigation packet: autumn_budget_2025 / ab2025__writing_down_allowances_14pct_and_40pct_fya / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Writing-down Allowances: Reduce the main rate writing-down allowance to 14% from April 2026 and introduce a new 40% first-year allowance from 1 January 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12411:3927b3bd94825044 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12417:31be8ebba861163e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12423:cf671a85400eb603 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24002:4f26d15c00a9f190 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12411:3927b3bd94825044 (row 12411) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Bank surcharge | 3.0 | — | — |
| head | obr_pmd_nov2025:12417:31be8ebba861163e (row 12417) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 10.0 | — | — |
| head | obr_pmd_nov2025:12423:cf671a85400eb603 (row 12423) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 1,477.0 | — | — |
| head | obr_pmd_nov2025:24002:4f26d15c00a9f190 (row 24002) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 1.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__writing_down_allowances_14pct_and_40pct_fya --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__writing_down_allowances_14pct_and_40pct_fya_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
