# Investigation packet: autumn_budget_2025 / ab2025__warm_homes_plan_and_warm_home_discount_expansion / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Warm Homes Plan: Increase funding for the Warm Homes Plan and expand the Warm Home Discount Scheme
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12072:6fee17b43fe5fb32 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23501:74ff57b6e9706491 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23507:020d18a9392a9382 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12072:6fee17b43fe5fb32 (row 12072) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Environmental levies | 589.0 | — | — |
| head | obr_pmd_nov2025:23501:74ff57b6e9706491 (row 23501) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Environmental levies | -589.0 | — | — |
| head | obr_pmd_nov2025:23507:020d18a9392a9382 (row 23507) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSGI in CDEL | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__warm_homes_plan_and_warm_home_discount_expansion --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__warm_homes_plan_and_warm_home_discount_expansion_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
