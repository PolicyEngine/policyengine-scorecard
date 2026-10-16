# Investigation packet: autumn_budget_2025 / ab2025__rebuilding_britain_capital_investment / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Rebuilding Britain: Accelerate delivery of growth-enhancing capital investment, including the Lower Thames Crossing
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12108:94a0eff38f3a0bb7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23633:c51669c4a0793c2f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23639:e9f41e4cce132032 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12108:94a0eff38f3a0bb7 (row 12108) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23633:c51669c4a0793c2f (row 23633) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other AME (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23639:e9f41e4cce132032 (row 23639) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSGI in CDEL | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__rebuilding_britain_capital_investment --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__rebuilding_britain_capital_investment_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
