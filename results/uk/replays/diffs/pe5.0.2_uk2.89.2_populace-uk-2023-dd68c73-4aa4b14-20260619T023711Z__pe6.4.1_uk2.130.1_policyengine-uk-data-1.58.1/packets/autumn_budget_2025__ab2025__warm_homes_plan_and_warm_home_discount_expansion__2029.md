# Investigation packet: autumn_budget_2025 / ab2025__warm_homes_plan_and_warm_home_discount_expansion / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Warm Homes Plan: Increase funding for the Warm Homes Plan and expand the Warm Home Discount Scheme
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12076:901b37f669e2218f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23505:cf135c1dce1a6215 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23511:03123dfd176d6aa0 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12076:901b37f669e2218f (row 12076) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Environmental levies | 640.0 | — | — |
| head | obr_pmd_nov2025:23505:cf135c1dce1a6215 (row 23505) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Environmental levies | -640.0 | — | — |
| head | obr_pmd_nov2025:23511:03123dfd176d6aa0 (row 23511) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSGI in CDEL | -357.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__warm_homes_plan_and_warm_home_discount_expansion --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__warm_homes_plan_and_warm_home_discount_expansion_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
