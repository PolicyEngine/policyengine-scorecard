# Investigation packet: autumn_budget_2025 / ab2025__phev_emissions_standard_and_bik_easement / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Plug-in hybrid electric vehicle (PHEV) emissions regulatory standard changes and Benefit in Kind easement
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12647:b6033905ed8e7d49 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12653:c4257a6d6fe8c2b6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12659:c0ff5290fac1d227 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12665:faf22cdd7094ca03 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24106:06bd2691002ce775 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24112:3feed75812871080 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12647:b6033905ed8e7d49 (row 12647) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 35.9 | — | — |
| head | obr_pmd_nov2025:12653:c4257a6d6fe8c2b6 (row 12653) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 7.1 | — | — |
| head | obr_pmd_nov2025:12659:c0ff5290fac1d227 (row 12659) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | 48.5 | — | — |
| head | obr_pmd_nov2025:12665:faf22cdd7094ca03 (row 12665) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Vehicle excise duty | -6.9 | — | — |
| head | obr_pmd_nov2025:24106:06bd2691002ce775 (row 24106) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:24112:3feed75812871080 (row 24112) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.5 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__phev_emissions_standard_and_bik_easement --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__phev_emissions_standard_and_bik_easement_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
