# Investigation packet: autumn_budget_2025 / ab2025__carers_allowance_overpayments_review / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Carer’s Allowance Review: Reassess overpayments from 2015 to 2025 caused by incorrect operational guidance
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23554:86904a2977990d0c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23560:9cd21dd8eda495b4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23566:2559d0cd19719b74 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23554:86904a2977990d0c (row 23554) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23560:9cd21dd8eda495b4 (row 23560) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:23566:2559d0cd19719b74 (row 23566) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__carers_allowance_overpayments_review --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__carers_allowance_overpayments_review_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
