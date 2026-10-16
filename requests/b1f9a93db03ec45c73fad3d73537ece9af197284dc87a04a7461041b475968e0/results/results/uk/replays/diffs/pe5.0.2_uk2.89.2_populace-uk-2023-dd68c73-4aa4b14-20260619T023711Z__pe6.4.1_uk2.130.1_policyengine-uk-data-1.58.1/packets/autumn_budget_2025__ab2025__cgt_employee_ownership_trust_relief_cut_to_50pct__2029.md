# Investigation packet: autumn_budget_2025 / ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Reduce Capital Gains Tax relief on qualifying disposals to employee ownership trusts from 100% to 50% from 26 November 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12358:ce6fdd9d63a1a298 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12364:bbca31c1a19d30f6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23979:0c734ca0f23be250 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23985:15867da2ece3e944 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12358:ce6fdd9d63a1a298 (row 12358) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 729.4 | — | — |
| head | obr_pmd_nov2025:12364:bbca31c1a19d30f6 (row 12364) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 163.1 | — | — |
| head | obr_pmd_nov2025:23979:0c734ca0f23be250 (row 23979) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 1.2 | — | — |
| head | obr_pmd_nov2025:23985:15867da2ece3e944 (row 23985) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 9.8 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
