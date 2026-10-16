# Investigation packet: autumn_budget_2025 / ab2025__uc_standard_allowance_and_health_element_rebalancing / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit: Changes to the standard allowance and health element to protect existing claimants and new health element claimants who meet the Severe Conditions Criteria from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:24164:59bbc18ef2b0b52d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24170:6eb0f852198750c1 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:24164:59bbc18ef2b0b52d (row 24164) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -625.2 | — | — |
| head | obr_pmd_nov2025:24170:6eb0f852198750c1 (row 24170) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -5.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_standard_allowance_and_health_element_rebalancing --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_standard_allowance_and_health_element_rebalancing_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
