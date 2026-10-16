# Investigation packet: autumn_budget_2025 / ab2025__db_pension_scheme_surplus_extraction / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Defined Benefit (DB) Pension Scheme Surplus Extraction: Introduce flexibilities for employers and direct payments to members from April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12552:3abef6d91a75f829 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12558:276cacc6c4b49bda | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24023:ff86dfad7d99dd94 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24029:58669e72025929cc | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12552:3abef6d91a75f829 (row 12552) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12558:276cacc6c4b49bda (row 12558) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:24023:ff86dfad7d99dd94 (row 24023) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24029:58669e72025929cc (row 24029) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__db_pension_scheme_surplus_extraction --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__db_pension_scheme_surplus_extraction_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
