# Investigation packet: autumn_budget_2025 / ab2025__employee_car_ownership_schemes_bik_delayed / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Delay bringing Employee Car Ownership schemes within the Benefit in Kind rules from 6 April 2026 to 6 April 2030, with a two year transition period
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12617:5217121c28d8ad8e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12623:378a3c9b5d69df7e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24064:9b810763ae4a73c1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24070:04d5d7ce9d019b18 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12617:5217121c28d8ad8e (row 12617) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -99.8 | — | — |
| head | obr_pmd_nov2025:12623:378a3c9b5d69df7e (row 12623) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | -40.7 | — | — |
| head | obr_pmd_nov2025:24064:9b810763ae4a73c1 (row 24064) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24070:04d5d7ce9d019b18 (row 24070) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.1 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employee_car_ownership_schemes_bik_delayed --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employee_car_ownership_schemes_bik_delayed_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
