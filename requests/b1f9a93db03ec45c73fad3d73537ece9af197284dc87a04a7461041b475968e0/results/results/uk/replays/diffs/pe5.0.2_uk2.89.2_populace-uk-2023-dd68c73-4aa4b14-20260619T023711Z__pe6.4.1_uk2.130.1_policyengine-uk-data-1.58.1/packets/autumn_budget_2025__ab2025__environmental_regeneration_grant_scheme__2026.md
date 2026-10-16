# Investigation packet: autumn_budget_2025 / ab2025__environmental_regeneration_grant_scheme / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Environmental Regeneration: Launch a new grant scheme for public bodies to support land remediation and reinvest water company fines in projects to clean up rivers, lakes and seas
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12223:25cfbb4975e6c23b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23892:e852cce098a141dc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23898:7a0aa582269b8cfe | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12223:25cfbb4975e6c23b (row 12223) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Landfill tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23892:e852cce098a141dc (row 23892) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -13.1 | — | — |
| head | obr_pmd_nov2025:23898:7a0aa582269b8cfe (row 23898) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSGI in CDEL | -4.8 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__environmental_regeneration_grant_scheme --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__environmental_regeneration_grant_scheme_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
