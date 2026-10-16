# Investigation packet: autumn_budget_2025 / ab2025__eved_mileage_supplement_electric_and_phev / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Electric Vehicle Excise Duty (eVED): Introduce a new mileage supplement for electric and plug-in hybrid cars from 1 April 2028
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12597:754e32c16ab051e1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12603:16309c752eed5573 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12597:754e32c16ab051e1 (row 12597) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Fuel Duty | -25.0 | — | — |
| head | obr_pmd_nov2025:12603:16309c752eed5573 (row 12603) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Vehicle excise duty | 1,123.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__eved_mileage_supplement_electric_and_phev --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__eved_mileage_supplement_electric_and_phev_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
