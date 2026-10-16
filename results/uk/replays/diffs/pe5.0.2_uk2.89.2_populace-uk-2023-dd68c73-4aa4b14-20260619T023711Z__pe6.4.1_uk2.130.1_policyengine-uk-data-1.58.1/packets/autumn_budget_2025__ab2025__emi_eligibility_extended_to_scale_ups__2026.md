# Investigation packet: autumn_budget_2025 / ab2025__emi_eligibility_extended_to_scale_ups / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Enterprise Management Incentives (EMI): Increase eligibility to allow scale-ups, as well as start-ups, to access the scheme from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12163:a68d35b2f07b7808 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12169:d0eacebc60e9793b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12175:b31dad0160244cd7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12181:6022aeb141db9c53 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23682:104054802f03392d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23688:57c282d7ffddb30c | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12163:a68d35b2f07b7808 (row 12163) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12169:d0eacebc60e9793b (row 12169) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -34.0 | — | — |
| head | obr_pmd_nov2025:12175:b31dad0160244cd7 (row 12175) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -18.0 | — | — |
| head | obr_pmd_nov2025:12181:6022aeb141db9c53 (row 12181) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -17.0 | — | — |
| head | obr_pmd_nov2025:23682:104054802f03392d (row 23682) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23688:57c282d7ffddb30c (row 23688) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -2.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__emi_eligibility_extended_to_scale_ups --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__emi_eligibility_extended_to_scale_ups_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
