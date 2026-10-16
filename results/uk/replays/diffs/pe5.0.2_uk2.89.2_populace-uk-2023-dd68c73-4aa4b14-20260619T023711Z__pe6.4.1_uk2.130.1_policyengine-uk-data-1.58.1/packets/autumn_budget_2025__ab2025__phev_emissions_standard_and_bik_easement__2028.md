# Investigation packet: autumn_budget_2025 / ab2025__phev_emissions_standard_and_bik_easement / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Plug-in hybrid electric vehicle (PHEV) emissions regulatory standard changes and Benefit in Kind easement
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12645:76e8b6e6b1db72b7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12651:c7e0c6d4bfffd6aa | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12657:e850496f492b53f1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12663:f7b0c91c5f93a1de | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24104:47becb83a93e802a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24110:93665ea93098d22c | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12645:76e8b6e6b1db72b7 (row 12645) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 0.2 | — | — |
| head | obr_pmd_nov2025:12651:c7e0c6d4bfffd6aa (row 12651) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -1.4 | — | — |
| head | obr_pmd_nov2025:12657:e850496f492b53f1 (row 12657) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 47.1 | — | — |
| head | obr_pmd_nov2025:12663:f7b0c91c5f93a1de (row 12663) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Vehicle excise duty | 29.5 | — | — |
| head | obr_pmd_nov2025:24104:47becb83a93e802a (row 24104) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24110:93665ea93098d22c (row 24110) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 0.2 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__phev_emissions_standard_and_bik_easement --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__phev_emissions_standard_and_bik_easement_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
