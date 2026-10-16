# Investigation packet: autumn_budget_2025 / ab2025__sizewell_c_rab_levy_reclassification / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Sizewell C: Reclassify construction costs and recognise income generated through the Regulated Asset Base levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12636:55c54b2bb1401354 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24083:d3f3cc0bf285bb22 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24089:896f323485d71932 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24095:0feb318ce0e40190 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12636:55c54b2bb1401354 (row 12636) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Environmental levies | 270.0 | — | — |
| head | obr_pmd_nov2025:24083:d3f3cc0bf285bb22 (row 24083) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other AME (current) | -219.0 | — | — |
| head | obr_pmd_nov2025:24089:896f323485d71932 (row 24089) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSGI in CDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24095:0feb318ce0e40190 (row 24095) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other departmental expenditure (capital) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__sizewell_c_rab_levy_reclassification --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__sizewell_c_rab_levy_reclassification_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
