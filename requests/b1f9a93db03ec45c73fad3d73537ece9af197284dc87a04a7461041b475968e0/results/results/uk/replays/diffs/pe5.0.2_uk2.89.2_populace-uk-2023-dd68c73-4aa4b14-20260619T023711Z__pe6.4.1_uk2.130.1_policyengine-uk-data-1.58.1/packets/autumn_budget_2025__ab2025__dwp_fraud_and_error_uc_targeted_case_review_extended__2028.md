# Investigation packet: autumn_budget_2025 / ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP Fraud and Error: Extend Targeted Case Review of Universal Credit to 2030-31
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23576:128be2798e30ced8 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23582:13d5fa469d6f7caa | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23588:e9169e5d4c26c3ae | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23576:128be2798e30ced8 (row 23576) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23582:13d5fa469d6f7caa (row 23582) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:23588:e9169e5d4c26c3ae (row 23588) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
