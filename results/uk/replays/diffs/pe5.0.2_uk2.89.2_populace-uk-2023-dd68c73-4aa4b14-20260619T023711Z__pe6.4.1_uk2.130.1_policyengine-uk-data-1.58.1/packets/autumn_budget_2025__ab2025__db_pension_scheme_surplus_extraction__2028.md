# Investigation packet: autumn_budget_2025 / ab2025__db_pension_scheme_surplus_extraction / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Defined Benefit (DB) Pension Scheme Surplus Extraction: Introduce flexibilities for employers and direct payments to members from April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12555:6c2f520c780a16d1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12561:7a3ae504f4432d6c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24026:c21c4afa2b3ad489 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24032:17c7e89ee944f4bf | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12555:6c2f520c780a16d1 (row 12555) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 34.6 | — | — |
| head | obr_pmd_nov2025:12561:7a3ae504f4432d6c (row 12561) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 89.2 | — | — |
| head | obr_pmd_nov2025:24026:c21c4afa2b3ad489 (row 24026) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.4 | — | — |
| head | obr_pmd_nov2025:24032:17c7e89ee944f4bf (row 24032) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 2.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__db_pension_scheme_surplus_extraction --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__db_pension_scheme_surplus_extraction_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
