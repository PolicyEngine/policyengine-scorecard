# Investigation packet: autumn_budget_2025 / ab2025__loan_charge_review_response / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Loan Charge: Government response to the independent review
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12721:e6aad7c7d71f867d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12727:9836667c894b8068 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12733:135fce3e5d6daa54 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24174:6caa8de1f5227ed1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24180:9e3d0c8ea4c2d62b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12721:e6aad7c7d71f867d (row 12721) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -78.1 | — | — |
| head | obr_pmd_nov2025:12727:9836667c894b8068 (row 12727) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | -2.4 | — | — |
| head | obr_pmd_nov2025:12733:135fce3e5d6daa54 (row 12733) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -5.8 | — | — |
| head | obr_pmd_nov2025:24174:6caa8de1f5227ed1 (row 24174) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -0.9 | — | — |
| head | obr_pmd_nov2025:24180:9e3d0c8ea4c2d62b (row 24180) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -5.9 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__loan_charge_review_response --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__loan_charge_review_response_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
