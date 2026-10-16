# Investigation packet: autumn_budget_2025 / ab2025__sizewell_c_rab_levy_reclassification / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Sizewell C: Reclassify construction costs and recognise income generated through the Regulated Asset Base levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12640:9e5b45cf605f9160 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24087:60a5e2889b0bc2de | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24093:bb79608095d782af | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24099:fa2b0e30f35e5c6a | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12640:9e5b45cf605f9160 (row 12640) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Environmental levies | 1,158.0 | — | — |
| head | obr_pmd_nov2025:24087:60a5e2889b0bc2de (row 24087) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other AME (current) | -356.0 | — | — |
| head | obr_pmd_nov2025:24093:bb79608095d782af (row 24093) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSGI in CDEL | 2,710.0 | — | — |
| head | obr_pmd_nov2025:24099:fa2b0e30f35e5c6a (row 24099) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other departmental expenditure (capital) | -2,717.8 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__sizewell_c_rab_levy_reclassification --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__sizewell_c_rab_levy_reclassification_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
