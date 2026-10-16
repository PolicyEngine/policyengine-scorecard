# Investigation packet: autumn_budget_2025 / ab2025__employee_car_ownership_schemes_bik_delayed / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Support for British automotive industry: Delay bringing Employee Car Ownership schemes within the Benefit in Kind rules from 6 April 2026 to 6 April 2030, with a two year transition period
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12615:a171bb72cc229a02 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12621:ee2b6407e84acc2d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24062:b8374e057b817305 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24068:5f0674ac6309f9c8 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12615:a171bb72cc229a02 (row 12615) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -106.8 | — | — |
| head | obr_pmd_nov2025:12621:ee2b6407e84acc2d (row 12621) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -43.6 | — | — |
| head | obr_pmd_nov2025:24062:b8374e057b817305 (row 24062) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.0 | — | — |
| head | obr_pmd_nov2025:24068:5f0674ac6309f9c8 (row 24068) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employee_car_ownership_schemes_bik_delayed --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employee_car_ownership_schemes_bik_delayed_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
