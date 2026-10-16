# Investigation packet: autumn_budget_2025 / ab2025__emi_eligibility_extended_to_scale_ups / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Enterprise Management Incentives (EMI): Increase eligibility to allow scale-ups, as well as start-ups, to access the scheme from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12162:5184fd647356d18d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12168:a705b253d68c0652 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12174:19877519c69beb4f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12180:4e53787b396b58b9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23681:d01d2c20d97f3e8f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23687:74d4355e43338a61 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12162:5184fd647356d18d (row 12162) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12168:a705b253d68c0652 (row 12168) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12174:19877519c69beb4f (row 12174) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 0.0 | — | — |
| head | obr_pmd_nov2025:12180:4e53787b396b58b9 (row 12180) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:23681:d01d2c20d97f3e8f (row 23681) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23687:74d4355e43338a61 (row 23687) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__emi_eligibility_extended_to_scale_ups --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__emi_eligibility_extended_to_scale_ups_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
