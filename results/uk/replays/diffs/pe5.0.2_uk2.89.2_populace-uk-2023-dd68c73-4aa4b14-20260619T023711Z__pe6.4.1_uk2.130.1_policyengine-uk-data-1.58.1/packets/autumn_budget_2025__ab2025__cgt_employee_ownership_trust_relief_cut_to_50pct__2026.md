# Investigation packet: autumn_budget_2025 / ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Reduce Capital Gains Tax relief on qualifying disposals to employee ownership trusts from 100% to 50% from 26 November 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12355:f39321421b5c5146 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12361:3d3cb7cb3acd2fef | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23976:7ebded74e51c2efa | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23982:5d3375c84812c7b8 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12355:f39321421b5c5146 (row 12355) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 162.7 | — | — |
| head | obr_pmd_nov2025:12361:3d3cb7cb3acd2fef (row 12361) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 19.1 | — | — |
| head | obr_pmd_nov2025:23976:7ebded74e51c2efa (row 23976) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.3 | — | — |
| head | obr_pmd_nov2025:23982:5d3375c84812c7b8 (row 23982) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 1.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
