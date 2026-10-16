# Investigation packet: autumn_budget_2025 / ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP Fraud and Error: Extend Targeted Case Review of Universal Credit to 2030-31
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23575:a4365dd38dea17f3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23581:4509744fdf37720e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23587:bacea64db3db565b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23575:a4365dd38dea17f3 (row 23575) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23581:4509744fdf37720e (row 23581) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:23587:bacea64db3db565b (row 23587) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
