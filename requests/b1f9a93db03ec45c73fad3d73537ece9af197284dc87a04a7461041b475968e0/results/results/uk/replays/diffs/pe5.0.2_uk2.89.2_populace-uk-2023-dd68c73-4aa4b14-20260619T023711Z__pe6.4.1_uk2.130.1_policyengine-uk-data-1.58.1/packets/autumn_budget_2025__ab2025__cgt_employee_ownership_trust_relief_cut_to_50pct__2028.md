# Investigation packet: autumn_budget_2025 / ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Reduce Capital Gains Tax relief on qualifying disposals to employee ownership trusts from 100% to 50% from 26 November 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12357:acd3d501bfb4a697 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12363:24dcbfcc373c36d6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23978:22bc0ae1ef3eb798 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23984:c4902bcad0852cee | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12357:acd3d501bfb4a697 (row 12357) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 658.4 | — | — |
| head | obr_pmd_nov2025:12363:24dcbfcc373c36d6 (row 12363) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 155.8 | — | — |
| head | obr_pmd_nov2025:23978:22bc0ae1ef3eb798 (row 23978) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 1.1 | — | — |
| head | obr_pmd_nov2025:23984:c4902bcad0852cee (row 23984) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 9.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
