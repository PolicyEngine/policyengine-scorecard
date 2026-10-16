# Investigation packet: autumn_budget_2025 / ab2025__supporting_savers_help_to_save_and_cash_isa_limit / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Supporting Savers: Make the Help to Save scheme permanent, maintain total ISA annual subscription limit at £20,000 with cash limit reduced to £12,000 for under-65s from April 2027, delay ISA digitalisation until April 2028 and maintain the ISA subscription limits until 2030/31
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12674:a5d517681108adc7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12680:9c068badb9bb6d21 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24121:619e66a48270eaef | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12674:a5d517681108adc7 (row 12674) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -1.0 | — | — |
| head | obr_pmd_nov2025:12680:9c068badb9bb6d21 (row 12680) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -8.9 | — | — |
| head | obr_pmd_nov2025:24121:619e66a48270eaef (row 24121) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (capital) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__supporting_savers_help_to_save_and_cash_isa_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__supporting_savers_help_to_save_and_cash_isa_limit_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
