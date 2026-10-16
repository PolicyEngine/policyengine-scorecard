# Investigation packet: autumn_budget_2025 / ab2025__eved_mileage_supplement_electric_and_phev / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Electric Vehicle Excise Duty (eVED): Introduce a new mileage supplement for electric and plug-in hybrid cars from 1 April 2028
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12595:f7030f74d5533c3c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12601:8453e071a5475197 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12595:f7030f74d5533c3c (row 12595) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Fuel Duty | -10.0 | — | — |
| head | obr_pmd_nov2025:12601:8453e071a5475197 (row 12601) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Vehicle excise duty | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__eved_mileage_supplement_electric_and_phev --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__eved_mileage_supplement_electric_and_phev_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
