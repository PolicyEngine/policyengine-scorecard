# Investigation packet: autumn_budget_2025 / ab2025__supporting_savers_help_to_save_and_cash_isa_limit / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Supporting Savers: Make the Help to Save scheme permanent, maintain total ISA annual subscription limit at £20,000 with cash limit reduced to £12,000 for under-65s from April 2027, delay ISA digitalisation until April 2028 and maintain the ISA subscription limits until 2030/31
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12673:90dca08858b65415 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12679:555d9557796ca252 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24120:761a073847bd881a | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12673:90dca08858b65415 (row 12673) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12679:555d9557796ca252 (row 12679) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -6.0 | — | — |
| head | obr_pmd_nov2025:24120:761a073847bd881a (row 24120) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other AME (capital) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__supporting_savers_help_to_save_and_cash_isa_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__supporting_savers_help_to_save_and_cash_isa_limit_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
