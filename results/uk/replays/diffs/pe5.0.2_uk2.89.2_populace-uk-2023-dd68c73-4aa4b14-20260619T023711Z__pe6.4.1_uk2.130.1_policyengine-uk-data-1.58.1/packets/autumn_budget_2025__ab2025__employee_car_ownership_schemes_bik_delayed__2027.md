# Investigation packet: autumn_budget_2025 / ab2025__employee_car_ownership_schemes_bik_delayed / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Delay bringing Employee Car Ownership schemes within the Benefit in Kind rules from 6 April 2026 to 6 April 2030, with a two year transition period
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12614:7f3bd6943cb18350 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12620:194d75f373956344 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24061:d873e59f78d5fda4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24067:9d0d37d5ecc833bd | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12614:7f3bd6943cb18350 (row 12614) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -106.0 | — | — |
| head | obr_pmd_nov2025:12620:194d75f373956344 (row 12620) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -43.3 | — | — |
| head | obr_pmd_nov2025:24061:d873e59f78d5fda4 (row 24061) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24067:9d0d37d5ecc833bd (row 24067) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employee_car_ownership_schemes_bik_delayed --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employee_car_ownership_schemes_bik_delayed_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
