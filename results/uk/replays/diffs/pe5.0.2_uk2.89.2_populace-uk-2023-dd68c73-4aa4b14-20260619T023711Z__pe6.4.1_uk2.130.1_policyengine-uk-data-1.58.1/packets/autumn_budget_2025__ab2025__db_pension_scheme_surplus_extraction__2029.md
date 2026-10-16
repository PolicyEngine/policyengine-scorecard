# Investigation packet: autumn_budget_2025 / ab2025__db_pension_scheme_surplus_extraction / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Defined Benefit (DB) Pension Scheme Surplus Extraction: Introduce flexibilities for employers and direct payments to members from April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12556:0afe8c4329cc65fd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12562:9c366f9c29994f23 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24027:c8b1c2694513392c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24033:059619d8f4f91ba3 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12556:0afe8c4329cc65fd (row 12556) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 38.0 | — | — |
| head | obr_pmd_nov2025:12562:9c366f9c29994f23 (row 12562) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 95.8 | — | — |
| head | obr_pmd_nov2025:24027:c8b1c2694513392c (row 24027) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.4 | — | — |
| head | obr_pmd_nov2025:24033:059619d8f4f91ba3 (row 24033) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 2.6 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__db_pension_scheme_surplus_extraction --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__db_pension_scheme_surplus_extraction_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
