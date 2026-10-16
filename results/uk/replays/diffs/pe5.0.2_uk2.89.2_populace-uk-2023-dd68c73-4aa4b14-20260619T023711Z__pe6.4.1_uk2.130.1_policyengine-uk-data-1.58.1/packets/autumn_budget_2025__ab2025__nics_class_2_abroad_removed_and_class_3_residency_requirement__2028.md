# Investigation packet: autumn_budget_2025 / ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Remove access to Class 2 National Insurance contributions (NICs) and increase the initial residency and contributions history requirements for Class 3 NICs for individuals abroad from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12105:1f3960d778c8fa16 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23630:1f846fd4e347a8d6 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12105:1f3960d778c8fa16 (row 12105) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -2.0 | — | — |
| head | obr_pmd_nov2025:23630:1f846fd4e347a8d6 (row 23630) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | 10.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
