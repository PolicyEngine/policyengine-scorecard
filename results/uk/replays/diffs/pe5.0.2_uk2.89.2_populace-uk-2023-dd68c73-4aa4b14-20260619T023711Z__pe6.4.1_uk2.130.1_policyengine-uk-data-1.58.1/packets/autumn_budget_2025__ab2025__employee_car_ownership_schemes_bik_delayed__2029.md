# Investigation packet: autumn_budget_2025 / ab2025__employee_car_ownership_schemes_bik_delayed / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Delay bringing Employee Car Ownership schemes within the Benefit in Kind rules from 6 April 2026 to 6 April 2030, with a two year transition period
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12616:7a30d0ab18fa7c72 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12622:810e574a64f5fc60 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24063:5ff85f2fefe70c3b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24069:baac88ffe630a41a | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12616:7a30d0ab18fa7c72 (row 12616) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -108.5 | — | — |
| head | obr_pmd_nov2025:12622:810e574a64f5fc60 (row 12622) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | -44.3 | — | — |
| head | obr_pmd_nov2025:24063:5ff85f2fefe70c3b (row 24063) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -0.0 | — | — |
| head | obr_pmd_nov2025:24069:baac88ffe630a41a (row 24069) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employee_car_ownership_schemes_bik_delayed --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employee_car_ownership_schemes_bik_delayed_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
