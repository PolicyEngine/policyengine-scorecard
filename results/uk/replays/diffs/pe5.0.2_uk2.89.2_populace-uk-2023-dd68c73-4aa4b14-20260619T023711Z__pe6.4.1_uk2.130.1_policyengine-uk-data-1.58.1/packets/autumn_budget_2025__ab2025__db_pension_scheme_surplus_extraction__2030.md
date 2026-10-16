# Investigation packet: autumn_budget_2025 / ab2025__db_pension_scheme_surplus_extraction / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Defined Benefit (DB) Pension Scheme Surplus Extraction: Introduce flexibilities for employers and direct payments to members from April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12557:49a5d8276e32bcbd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12563:549303e75a81b90d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24028:8f9773ba350c0081 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24034:e9c22a86d55cd5ab | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12557:49a5d8276e32bcbd (row 12557) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 41.9 | — | — |
| head | obr_pmd_nov2025:12563:549303e75a81b90d (row 12563) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | 98.2 | — | — |
| head | obr_pmd_nov2025:24028:8f9773ba350c0081 (row 24028) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.4 | — | — |
| head | obr_pmd_nov2025:24034:e9c22a86d55cd5ab (row 24034) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 2.8 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__db_pension_scheme_surplus_extraction --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__db_pension_scheme_surplus_extraction_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
