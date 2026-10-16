# Investigation packet: autumn_budget_2025 / ab2025__fya_zero_emission_cars_and_charge_points_extended / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Extend 100% first-year allowances for zero-emission cars and electric vehicle charge points to 31 March 2027 for Corporation Tax and 5 April 2027 for Income Tax
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12626:0f0ccb80c9800320 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12632:4f2d0e9bff6cc0db | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24073:35283f4106e8c037 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24079:687366ac07cbf4ba | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12626:0f0ccb80c9800320 (row 12626) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -28.1 | — | — |
| head | obr_pmd_nov2025:12632:4f2d0e9bff6cc0db (row 12632) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -67.3 | — | — |
| head | obr_pmd_nov2025:24073:35283f4106e8c037 (row 24073) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -0.3 | — | — |
| head | obr_pmd_nov2025:24079:687366ac07cbf4ba (row 24079) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -1.9 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__fya_zero_emission_cars_and_charge_points_extended --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__fya_zero_emission_cars_and_charge_points_extended_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
