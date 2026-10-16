# Investigation packet: autumn_budget_2025 / ab2025__carers_allowance_overpayments_review / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Carer’s Allowance Review: Reassess overpayments from 2015 to 2025 caused by incorrect operational guidance
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23551:58a4336802093431 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23557:b4013104476436a7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23563:2e13daff8edafd6d | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23551:58a4336802093431 (row 23551) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -20.0 | — | — |
| head | obr_pmd_nov2025:23557:b4013104476436a7 (row 23557) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -14.0 | — | — |
| head | obr_pmd_nov2025:23563:2e13daff8edafd6d (row 23563) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -1.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__carers_allowance_overpayments_review --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__carers_allowance_overpayments_review_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
