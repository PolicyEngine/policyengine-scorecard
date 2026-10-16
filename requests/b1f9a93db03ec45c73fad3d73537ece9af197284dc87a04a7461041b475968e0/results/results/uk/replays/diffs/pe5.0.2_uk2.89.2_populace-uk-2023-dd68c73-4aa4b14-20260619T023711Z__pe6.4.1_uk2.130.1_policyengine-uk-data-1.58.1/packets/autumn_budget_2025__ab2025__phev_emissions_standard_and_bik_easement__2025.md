# Investigation packet: autumn_budget_2025 / ab2025__phev_emissions_standard_and_bik_easement / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Plug-in hybrid electric vehicle (PHEV) emissions regulatory standard changes and Benefit in Kind easement
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12642:e15cdac6a0cd8e25 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12648:a68bca528ccdbffe | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12654:e41ec9b2f0610230 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12660:8780d30ef7c1b91a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24101:a89209138a8be2a0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24107:61872e3e66ce4133 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12642:e15cdac6a0cd8e25 (row 12642) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -0.5 | — | — |
| head | obr_pmd_nov2025:12648:a68bca528ccdbffe (row 12648) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -0.2 | — | — |
| head | obr_pmd_nov2025:12654:e41ec9b2f0610230 (row 12654) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.4 | — | — |
| head | obr_pmd_nov2025:12660:8780d30ef7c1b91a (row 12660) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Vehicle excise duty | -1.8 | — | — |
| head | obr_pmd_nov2025:24101:a89209138a8be2a0 (row 24101) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.0 | — | — |
| head | obr_pmd_nov2025:24107:61872e3e66ce4133 (row 24107) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__phev_emissions_standard_and_bik_easement --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__phev_emissions_standard_and_bik_easement_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
