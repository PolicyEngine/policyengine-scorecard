# Investigation packet: autumn_budget_2025 / ab2025__student_finance_lle_launch_and_loan_outlay / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Student Finance: Confirm policy detail for the Lifelong Learning Entitlement launch on 1 January 2027 and increase spending on student loans due to a new means-tested maintenance grant offer for students studying certain courses from academic year 2028/29
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12668:23254dbb55bcc67c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24115:8fe2efde9b2c0ec0 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12668:23254dbb55bcc67c (row 12668) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Interest and dividend receipts | 0.0 | — | — |
| head | obr_pmd_nov2025:24115:8fe2efde9b2c0ec0 (row 24115) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Student loans | 6.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__student_finance_lle_launch_and_loan_outlay --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__student_finance_lle_launch_and_loan_outlay_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
