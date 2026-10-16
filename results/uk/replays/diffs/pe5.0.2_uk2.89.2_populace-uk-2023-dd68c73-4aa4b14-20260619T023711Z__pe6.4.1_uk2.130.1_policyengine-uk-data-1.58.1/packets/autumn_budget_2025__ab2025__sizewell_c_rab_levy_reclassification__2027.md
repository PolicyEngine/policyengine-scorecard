# Investigation packet: autumn_budget_2025 / ab2025__sizewell_c_rab_levy_reclassification / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Sizewell C: Reclassify construction costs and recognise income generated through the Regulated Asset Base levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12638:1c16ea966f385f86 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24085:b185c3194cff2a6d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24091:17466b9c49a015e0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24097:0351690030fda211 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12638:1c16ea966f385f86 (row 12638) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Environmental levies | 797.0 | — | — |
| head | obr_pmd_nov2025:24085:b185c3194cff2a6d (row 24085) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (current) | -267.0 | — | — |
| head | obr_pmd_nov2025:24091:17466b9c49a015e0 (row 24091) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSGI in CDEL | 3,032.0 | — | — |
| head | obr_pmd_nov2025:24097:0351690030fda211 (row 24097) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other departmental expenditure (capital) | -2,982.5 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__sizewell_c_rab_levy_reclassification --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__sizewell_c_rab_levy_reclassification_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
