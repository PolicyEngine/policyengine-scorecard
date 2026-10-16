# Investigation packet: autumn_budget_2025 / ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Independence Payment: Not proceeding with Spring Statement 2025 reforms to eligibility
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:24141:91e1a5fe79a27a63 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24147:195f07d22097a901 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:24141:91e1a5fe79a27a63 (row 24141) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -4,017.0 | — | — |
| head | obr_pmd_nov2025:24147:195f07d22097a901 (row 24147) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -476.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
