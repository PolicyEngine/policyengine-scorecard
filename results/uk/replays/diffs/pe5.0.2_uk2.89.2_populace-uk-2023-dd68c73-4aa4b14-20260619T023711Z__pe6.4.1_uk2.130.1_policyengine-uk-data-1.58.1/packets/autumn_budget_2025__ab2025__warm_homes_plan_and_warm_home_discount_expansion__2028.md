# Investigation packet: autumn_budget_2025 / ab2025__warm_homes_plan_and_warm_home_discount_expansion / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Warm Homes Plan: Increase funding for the Warm Homes Plan and expand the Warm Home Discount Scheme
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12075:bdd1068c03670d0f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23504:c5cb0826e6cf9bc1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23510:2633963a159944bd | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12075:bdd1068c03670d0f (row 12075) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Environmental levies | 626.0 | — | — |
| head | obr_pmd_nov2025:23504:c5cb0826e6cf9bc1 (row 23504) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Environmental levies | -626.0 | — | — |
| head | obr_pmd_nov2025:23510:2633963a159944bd (row 23510) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSGI in CDEL | -535.9 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__warm_homes_plan_and_warm_home_discount_expansion --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__warm_homes_plan_and_warm_home_discount_expansion_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
