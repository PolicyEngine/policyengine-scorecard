# Investigation packet: autumn_budget_2025 / autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Council Tax Precepts: £5 flexibility for fire authorities
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12773:44c55279e5fa0759 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24250:8a1308d11421f15b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12773:44c55279e5fa0759 (row 12773) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Council Tax | 74.0 | — | — |
| head | obr_pmd_nov2025:24250:8a1308d11421f15b (row 24250) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Locally-financed current expenditure | -74.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
