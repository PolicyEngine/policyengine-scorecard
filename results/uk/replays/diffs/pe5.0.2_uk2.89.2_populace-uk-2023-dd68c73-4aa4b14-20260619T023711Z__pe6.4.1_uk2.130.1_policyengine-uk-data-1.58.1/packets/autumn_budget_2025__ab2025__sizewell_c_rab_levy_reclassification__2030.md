# Investigation packet: autumn_budget_2025 / ab2025__sizewell_c_rab_levy_reclassification / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Sizewell C: Reclassify construction costs and recognise income generated through the Regulated Asset Base levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12641:82b2b813f2253f2c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24088:c086e56fd1f5c1d0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24094:575eed2e0198e142 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24100:be86542b4199b393 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12641:82b2b813f2253f2c (row 12641) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Environmental levies | 1,396.0 | — | — |
| head | obr_pmd_nov2025:24088:c086e56fd1f5c1d0 (row 24088) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Other AME (current) | -412.0 | — | — |
| head | obr_pmd_nov2025:24094:575eed2e0198e142 (row 24094) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSGI in CDEL | 3,671.0 | — | — |
| head | obr_pmd_nov2025:24100:be86542b4199b393 (row 24100) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Other departmental expenditure (capital) | -3,687.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__sizewell_c_rab_levy_reclassification --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__sizewell_c_rab_levy_reclassification_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
