# Investigation packet: autumn_budget_2025 / ab2025__kernow_industrial_growth_fund / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Kernow Industrial Growth Fund: Provide funding to support growth in Cornwall
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23778:d0d97c36dbb531b6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23784:c384010d3c640d1e | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23778:d0d97c36dbb531b6 (row 23778) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -3.8 | — | — |
| head | obr_pmd_nov2025:23784:c384010d3c640d1e (row 23784) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSGI in CDEL | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__kernow_industrial_growth_fund --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__kernow_industrial_growth_fund_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
