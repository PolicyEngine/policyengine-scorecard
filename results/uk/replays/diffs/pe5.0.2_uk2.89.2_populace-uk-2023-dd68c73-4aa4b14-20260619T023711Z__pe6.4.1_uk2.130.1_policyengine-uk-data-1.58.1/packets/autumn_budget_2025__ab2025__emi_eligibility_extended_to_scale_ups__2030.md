# Investigation packet: autumn_budget_2025 / ab2025__emi_eligibility_extended_to_scale_ups / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Enterprise Management Incentives (EMI): Increase eligibility to allow scale-ups, as well as start-ups, to access the scheme from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12167:c8da8884460e5a7d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12173:8baa4b257bf95636 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12179:2e02e7e2f1fef92f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12185:a740034aabdf7c4c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23686:482215ec44d36abe | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23692:bd30a78d8c67f4ad | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12167:c8da8884460e5a7d (row 12167) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | -20.0 | — | — |
| head | obr_pmd_nov2025:12173:8baa4b257bf95636 (row 12173) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -362.0 | — | — |
| head | obr_pmd_nov2025:12179:2e02e7e2f1fef92f (row 12179) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | -188.0 | — | — |
| head | obr_pmd_nov2025:12185:a740034aabdf7c4c (row 12185) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -96.0 | — | — |
| head | obr_pmd_nov2025:23686:482215ec44d36abe (row 23686) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -4.0 | — | — |
| head | obr_pmd_nov2025:23692:bd30a78d8c67f4ad (row 23692) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -25.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__emi_eligibility_extended_to_scale_ups --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__emi_eligibility_extended_to_scale_ups_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
