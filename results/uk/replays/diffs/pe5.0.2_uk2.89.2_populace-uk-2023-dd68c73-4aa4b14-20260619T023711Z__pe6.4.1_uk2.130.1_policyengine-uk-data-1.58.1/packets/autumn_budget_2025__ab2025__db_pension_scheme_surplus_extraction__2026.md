# Investigation packet: autumn_budget_2025 / ab2025__db_pension_scheme_surplus_extraction / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Defined Benefit (DB) Pension Scheme Surplus Extraction: Introduce flexibilities for employers and direct payments to members from April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12553:a9a763a23955ec92 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12559:1027df24fe8711ef | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24024:c54b6dc31acfe34d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24030:2cc7838b5c4e1bba | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12553:a9a763a23955ec92 (row 12553) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12559:1027df24fe8711ef (row 12559) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 27.7 | — | — |
| head | obr_pmd_nov2025:24024:c54b6dc31acfe34d (row 24024) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24030:2cc7838b5c4e1bba (row 24030) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__db_pension_scheme_surplus_extraction --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__db_pension_scheme_surplus_extraction_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
