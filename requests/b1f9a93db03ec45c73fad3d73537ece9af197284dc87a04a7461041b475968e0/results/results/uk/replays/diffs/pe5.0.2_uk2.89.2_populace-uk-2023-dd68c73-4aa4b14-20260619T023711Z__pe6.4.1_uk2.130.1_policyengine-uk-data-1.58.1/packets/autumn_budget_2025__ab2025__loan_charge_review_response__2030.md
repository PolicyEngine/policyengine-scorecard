# Investigation packet: autumn_budget_2025 / ab2025__loan_charge_review_response / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Loan Charge: Government response to the independent review
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12725:912bd99eac6c54d4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12731:f0ecb4000a22fded | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12737:ca55886c4c5ddebb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24178:43d9bd1023d6bb97 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24184:45276911faf5e2eb | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12725:912bd99eac6c54d4 (row 12725) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -77.5 | — | — |
| head | obr_pmd_nov2025:12731:f0ecb4000a22fded (row 12731) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Inheritance tax | -2.1 | — | — |
| head | obr_pmd_nov2025:12737:ca55886c4c5ddebb (row 12737) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | -9.9 | — | — |
| head | obr_pmd_nov2025:24178:43d9bd1023d6bb97 (row 24178) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -0.9 | — | — |
| head | obr_pmd_nov2025:24184:45276911faf5e2eb (row 24184) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -5.9 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__loan_charge_review_response --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__loan_charge_review_response_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
