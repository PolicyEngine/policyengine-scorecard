# Investigation packet: autumn_budget_2025 / ab2025__gambling_duties_rgd_40_remote_betting_25 / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Gambling Duty: Increase Remote Gaming Duty to 40% from 1 April 2026, introduce a new Remote Betting Rate at 25% (excluding Self-Service Betting Terminals, spread betting, pool betting & UK horseracing) from 1 April 2027, and abolish Bingo Duty from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12517:6c19482a569f8a56 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12523:54a2d28ddcb27d26 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12517:6c19482a569f8a56 (row 12517) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Betting | 841.0 | — | — |
| head | obr_pmd_nov2025:12523:54a2d28ddcb27d26 (row 12523) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -29.3 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__gambling_duties_rgd_40_remote_betting_25 --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__gambling_duties_rgd_40_remote_betting_25_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
