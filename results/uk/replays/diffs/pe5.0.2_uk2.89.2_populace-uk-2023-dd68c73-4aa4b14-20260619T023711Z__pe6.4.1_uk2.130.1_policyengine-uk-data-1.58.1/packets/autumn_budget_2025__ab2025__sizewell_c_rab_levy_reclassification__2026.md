# Investigation packet: autumn_budget_2025 / ab2025__sizewell_c_rab_levy_reclassification / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Sizewell C: Reclassify construction costs and recognise income generated through the Regulated Asset Base levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12637:5c68cba5ba8693e7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24084:4d89d10ff37a4a3a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24090:64b0a1414506fec1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24096:719ff529f1498cb1 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12637:5c68cba5ba8693e7 (row 12637) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Environmental levies | 704.0 | — | — |
| head | obr_pmd_nov2025:24084:4d89d10ff37a4a3a (row 24084) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other AME (current) | -227.0 | — | — |
| head | obr_pmd_nov2025:24090:64b0a1414506fec1 (row 24090) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSGI in CDEL | 2,774.0 | — | — |
| head | obr_pmd_nov2025:24096:719ff529f1498cb1 (row 24096) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other departmental expenditure (capital) | -2,742.7 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__sizewell_c_rab_levy_reclassification --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__sizewell_c_rab_levy_reclassification_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
