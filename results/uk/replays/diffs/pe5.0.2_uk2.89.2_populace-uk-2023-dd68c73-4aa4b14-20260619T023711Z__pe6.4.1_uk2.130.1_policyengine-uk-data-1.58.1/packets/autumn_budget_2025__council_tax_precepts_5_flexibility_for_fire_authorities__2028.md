# Investigation packet: autumn_budget_2025 / autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Council Tax Precepts: £5 flexibility for fire authorities
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12771:364fdf4d78c0e222 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24248:d526ffc48701508e | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12771:364fdf4d78c0e222 (row 12771) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Council Tax | 69.0 | — | — |
| head | obr_pmd_nov2025:24248:d526ffc48701508e (row 24248) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Locally-financed current expenditure | -69.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
