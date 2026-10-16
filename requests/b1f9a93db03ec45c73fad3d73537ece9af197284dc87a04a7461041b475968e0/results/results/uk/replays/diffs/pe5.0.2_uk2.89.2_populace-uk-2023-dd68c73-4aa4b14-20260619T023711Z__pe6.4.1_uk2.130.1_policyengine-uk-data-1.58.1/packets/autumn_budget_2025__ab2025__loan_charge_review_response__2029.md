# Investigation packet: autumn_budget_2025 / ab2025__loan_charge_review_response / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Loan Charge: Government response to the independent review
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12724:535ee8926005c114 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12730:8e393ff62a64c460 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12736:13bec85584b29f4a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24177:4e426405f1ebd0c2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24183:533c92befedf79e8 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12724:535ee8926005c114 (row 12724) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -131.2 | — | — |
| head | obr_pmd_nov2025:12730:8e393ff62a64c460 (row 12730) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -3.1 | — | — |
| head | obr_pmd_nov2025:12736:13bec85584b29f4a (row 12736) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | -10.1 | — | — |
| head | obr_pmd_nov2025:24177:4e426405f1ebd0c2 (row 24177) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -1.5 | — | — |
| head | obr_pmd_nov2025:24183:533c92befedf79e8 (row 24183) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -10.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__loan_charge_review_response --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__loan_charge_review_response_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
