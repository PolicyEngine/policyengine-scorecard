# Investigation packet: autumn_budget_2025 / ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Independence Payment: Not proceeding with Spring Statement 2025 reforms to eligibility
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:24138:04c8ebfcf07de049 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24144:47d6a1ecedd242bd | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:24138:04c8ebfcf07de049 (row 24138) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -183.0 | — | — |
| head | obr_pmd_nov2025:24144:47d6a1ecedd242bd (row 24144) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -54.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
