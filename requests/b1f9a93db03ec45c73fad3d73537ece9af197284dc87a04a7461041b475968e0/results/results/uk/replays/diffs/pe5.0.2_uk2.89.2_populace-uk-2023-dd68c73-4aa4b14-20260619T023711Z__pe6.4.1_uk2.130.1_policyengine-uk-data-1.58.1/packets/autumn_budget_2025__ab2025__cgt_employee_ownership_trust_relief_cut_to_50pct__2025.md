# Investigation packet: autumn_budget_2025 / ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Reduce Capital Gains Tax relief on qualifying disposals to employee ownership trusts from 100% to 50% from 26 November 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12354:a243dd3fbba60585 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12360:22e0ccdc5a9d581a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23975:18ad4b3b872bfb44 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23981:53c85bfa84f289e3 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12354:a243dd3fbba60585 (row 12354) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12360:22e0ccdc5a9d581a (row 12360) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23975:18ad4b3b872bfb44 (row 23975) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23981:53c85bfa84f289e3 (row 23981) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
