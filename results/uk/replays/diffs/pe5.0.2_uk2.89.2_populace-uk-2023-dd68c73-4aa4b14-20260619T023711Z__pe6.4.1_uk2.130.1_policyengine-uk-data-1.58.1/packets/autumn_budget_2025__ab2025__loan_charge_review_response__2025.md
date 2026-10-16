# Investigation packet: autumn_budget_2025 / ab2025__loan_charge_review_response / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Loan Charge: Government response to the independent review
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12720:104d9332a4b1cebb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12726:b4e6922b97abb2f9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12732:f97f95b05c599ed2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24173:4a184ecf1a129900 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24179:5a7b90b72c3b3875 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12720:104d9332a4b1cebb (row 12720) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -17.4 | — | — |
| head | obr_pmd_nov2025:12726:b4e6922b97abb2f9 (row 12726) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -0.4 | — | — |
| head | obr_pmd_nov2025:12732:f97f95b05c599ed2 (row 12732) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -4.9 | — | — |
| head | obr_pmd_nov2025:24173:4a184ecf1a129900 (row 24173) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.2 | — | — |
| head | obr_pmd_nov2025:24179:5a7b90b72c3b3875 (row 24179) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -1.3 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__loan_charge_review_response --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__loan_charge_review_response_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
