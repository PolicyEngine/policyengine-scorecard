# Investigation packet: autumn_budget_2025 / ab2025__low_value_imports_customs_reform / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Low Value Imports: Reform the customs treatment of low value imports from March 2029
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12537:ed3a903c9d50ca09 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12543:20e24724c7978ae4 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12537:ed3a903c9d50ca09 (row 12537) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Customs duty | 36.0 | — | — |
| head | obr_pmd_nov2025:12543:20e24724c7978ae4 (row 12543) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT | 6.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__low_value_imports_customs_reform --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__low_value_imports_customs_reform_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
