# Investigation packet: autumn_budget_2025 / ab2025__phev_emissions_standard_and_bik_easement / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Plug-in hybrid electric vehicle (PHEV) emissions regulatory standard changes and Benefit in Kind easement
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12646:bdbb712f9fc83597 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12652:46dd8a12848069bb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12658:292f1e5afa23e5d1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12664:d3fbd278181dc4c1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24105:1b4e97effee924e6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24111:444d03ffaa0262a6 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12646:bdbb712f9fc83597 (row 12646) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 21.2 | — | — |
| head | obr_pmd_nov2025:12652:46dd8a12848069bb (row 12652) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | -1.0 | — | — |
| head | obr_pmd_nov2025:12658:292f1e5afa23e5d1 (row 12658) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 49.6 | — | — |
| head | obr_pmd_nov2025:12664:d3fbd278181dc4c1 (row 12664) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Vehicle excise duty | 8.0 | — | — |
| head | obr_pmd_nov2025:24105:1b4e97effee924e6 (row 24105) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:24111:444d03ffaa0262a6 (row 24111) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 0.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__phev_emissions_standard_and_bik_easement --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__phev_emissions_standard_and_bik_easement_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
