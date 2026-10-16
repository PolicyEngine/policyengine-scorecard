# Investigation packet: autumn_budget_2025 / ab2025__environmental_regeneration_grant_scheme / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Environmental Regeneration: Launch a new grant scheme for public bodies to support land remediation and reinvest water company fines in projects to clean up rivers, lakes and seas
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12222:05026bea520775b4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23891:f534b0e401ca9b1e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23897:5202a047fb1690c3 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12222:05026bea520775b4 (row 12222) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Landfill tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23891:f534b0e401ca9b1e (row 23891) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23897:5202a047fb1690c3 (row 23897) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSGI in CDEL | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__environmental_regeneration_grant_scheme --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__environmental_regeneration_grant_scheme_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
