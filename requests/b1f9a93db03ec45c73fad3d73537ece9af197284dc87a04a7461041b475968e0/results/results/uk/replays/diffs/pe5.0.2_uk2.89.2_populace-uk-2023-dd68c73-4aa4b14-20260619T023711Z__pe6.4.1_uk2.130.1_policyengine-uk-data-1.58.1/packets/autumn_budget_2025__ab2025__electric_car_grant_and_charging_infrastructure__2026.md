# Investigation packet: autumn_budget_2025 / ab2025__electric_car_grant_and_charging_infrastructure / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Provide additional Electric Car Grant funding & extend to 2029-30 and invest in EV charging infrastructure
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:24048:8a8ee65fc69a3b1a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24054:2b7365c3e24fcfa3 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:24048:8a8ee65fc69a3b1a (row 24048) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -13.7 | — | — |
| head | obr_pmd_nov2025:24054:2b7365c3e24fcfa3 (row 24054) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSGI in CDEL | -200.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__electric_car_grant_and_charging_infrastructure --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__electric_car_grant_and_charging_infrastructure_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
