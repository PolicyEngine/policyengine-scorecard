# Investigation packet: autumn_budget_2025 / ab2025__fya_zero_emission_cars_and_charge_points_extended / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Extend 100% first-year allowances for zero-emission cars and electric vehicle charge points to 31 March 2027 for Corporation Tax and 5 April 2027 for Income Tax
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12627:b7b7e37787bd5038 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12633:9e44d2a5ee1e4fb7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24074:5ed11dcb88596087 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24080:da50c839abf55bb4 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12627:b7b7e37787bd5038 (row 12627) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 6.5 | — | — |
| head | obr_pmd_nov2025:12633:9e44d2a5ee1e4fb7 (row 12633) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 8.2 | — | — |
| head | obr_pmd_nov2025:24074:5ed11dcb88596087 (row 24074) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:24080:da50c839abf55bb4 (row 24080) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 0.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__fya_zero_emission_cars_and_charge_points_extended --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__fya_zero_emission_cars_and_charge_points_extended_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
