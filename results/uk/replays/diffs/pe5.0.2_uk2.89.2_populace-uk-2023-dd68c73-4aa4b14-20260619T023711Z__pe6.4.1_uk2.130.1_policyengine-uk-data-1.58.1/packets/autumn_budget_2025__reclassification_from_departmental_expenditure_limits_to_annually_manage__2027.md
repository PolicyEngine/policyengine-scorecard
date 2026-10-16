# Investigation packet: autumn_budget_2025 / autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Reclassification from departmental expenditure limits to annually managed expenditure for Scottish government police & fire pensions
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:24235:8061428ea5da42f5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24241:0ee2e9ee8ab80ba4 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:24235:8061428ea5da42f5 (row 24235) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 350.0 | — | — |
| head | obr_pmd_nov2025:24241:0ee2e9ee8ab80ba4 (row 24241) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Net public service pension payments | -350.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
