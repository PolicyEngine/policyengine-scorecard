# Investigation packet: autumn_budget_2025 / ab2025__phev_emissions_standard_and_bik_easement / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Plug-in hybrid electric vehicle (PHEV) emissions regulatory standard changes and Benefit in Kind easement
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12643:b2ee22d9e98b53f8 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12649:8da68d49ff49e27e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12655:8ebc69138623088e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12661:b49798dfebcfab09 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24102:47c7a5ae46efaa51 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24108:756e1534850c2b67 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12643:b2ee22d9e98b53f8 (row 12643) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -1.0 | — | — |
| head | obr_pmd_nov2025:12649:8da68d49ff49e27e (row 12649) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -0.2 | — | — |
| head | obr_pmd_nov2025:12655:8ebc69138623088e (row 12655) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 17.6 | — | — |
| head | obr_pmd_nov2025:12661:b49798dfebcfab09 (row 12661) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Vehicle excise duty | 18.0 | — | — |
| head | obr_pmd_nov2025:24102:47c7a5ae46efaa51 (row 24102) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24108:756e1534850c2b67 (row 24108) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__phev_emissions_standard_and_bik_easement --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__phev_emissions_standard_and_bik_easement_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
