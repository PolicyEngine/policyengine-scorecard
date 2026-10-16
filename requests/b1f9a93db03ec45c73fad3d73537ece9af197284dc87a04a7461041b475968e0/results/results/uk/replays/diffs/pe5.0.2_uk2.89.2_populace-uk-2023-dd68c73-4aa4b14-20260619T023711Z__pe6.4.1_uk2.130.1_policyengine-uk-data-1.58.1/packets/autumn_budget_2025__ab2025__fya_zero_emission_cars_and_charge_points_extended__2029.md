# Investigation packet: autumn_budget_2025 / ab2025__fya_zero_emission_cars_and_charge_points_extended / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Extend 100% first-year allowances for zero-emission cars and electric vehicle charge points to 31 March 2027 for Corporation Tax and 5 April 2027 for Income Tax
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12628:b14116974b97329f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12634:38b734e118ddd810 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24075:dfbe5f6dc2664eb9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24081:160559ff913f96f0 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12628:b14116974b97329f (row 12628) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1.7 | — | — |
| head | obr_pmd_nov2025:12634:38b734e118ddd810 (row 12634) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 17.6 | — | — |
| head | obr_pmd_nov2025:24075:dfbe5f6dc2664eb9 (row 24075) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24081:160559ff913f96f0 (row 24081) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 0.1 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__fya_zero_emission_cars_and_charge_points_extended --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__fya_zero_emission_cars_and_charge_points_extended_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
