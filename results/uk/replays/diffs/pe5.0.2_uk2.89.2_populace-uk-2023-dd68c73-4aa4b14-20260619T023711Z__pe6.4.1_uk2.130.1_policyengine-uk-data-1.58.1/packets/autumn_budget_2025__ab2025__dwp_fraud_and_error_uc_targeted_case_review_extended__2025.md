# Investigation packet: autumn_budget_2025 / ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP Fraud and Error: Extend Targeted Case Review of Universal Credit to 2030-31
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23573:bdc36113c022666a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23579:81d6d53acae294df | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23585:b5f7b29320e6b183 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23573:bdc36113c022666a (row 23573) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23579:81d6d53acae294df (row 23579) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:23585:b5f7b29320e6b183 (row 23585) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
