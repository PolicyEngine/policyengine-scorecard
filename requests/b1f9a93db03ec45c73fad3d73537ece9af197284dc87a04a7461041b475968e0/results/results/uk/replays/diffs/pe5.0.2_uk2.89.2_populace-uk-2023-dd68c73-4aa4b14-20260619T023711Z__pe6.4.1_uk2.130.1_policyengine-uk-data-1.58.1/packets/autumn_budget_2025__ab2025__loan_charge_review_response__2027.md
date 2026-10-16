# Investigation packet: autumn_budget_2025 / ab2025__loan_charge_review_response / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Loan Charge: Government response to the independent review
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12722:d18dc9a1ebc7567d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12728:d5d58119bed237eb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12734:feb6a69c0711501d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24175:772fd98bee3a52c4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24181:13082bfaf4615084 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12722:d18dc9a1ebc7567d (row 12722) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -22.3 | — | — |
| head | obr_pmd_nov2025:12728:d5d58119bed237eb (row 12728) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -0.2 | — | — |
| head | obr_pmd_nov2025:12734:feb6a69c0711501d (row 12734) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -3.9 | — | — |
| head | obr_pmd_nov2025:24175:772fd98bee3a52c4 (row 24175) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -0.3 | — | — |
| head | obr_pmd_nov2025:24181:13082bfaf4615084 (row 24181) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -1.7 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__loan_charge_review_response --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__loan_charge_review_response_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
