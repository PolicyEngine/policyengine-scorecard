# Investigation packet: autumn_budget_2025 / ab2025__loan_charge_review_response / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Loan Charge: Government response to the independent review
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12723:127abac63edfdc08 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12729:1dbe465ee4e985be | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12735:05659e5a8e910c7e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24176:24c3be9fb1793722 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24182:9bd5ca147b14da22 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12723:127abac63edfdc08 (row 12723) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 31.3 | — | — |
| head | obr_pmd_nov2025:12729:1dbe465ee4e985be (row 12729) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | 1.0 | — | — |
| head | obr_pmd_nov2025:12735:05659e5a8e910c7e (row 12735) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 0.2 | — | — |
| head | obr_pmd_nov2025:24176:24c3be9fb1793722 (row 24176) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.4 | — | — |
| head | obr_pmd_nov2025:24182:9bd5ca147b14da22 (row 24182) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 2.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__loan_charge_review_response --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__loan_charge_review_response_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
