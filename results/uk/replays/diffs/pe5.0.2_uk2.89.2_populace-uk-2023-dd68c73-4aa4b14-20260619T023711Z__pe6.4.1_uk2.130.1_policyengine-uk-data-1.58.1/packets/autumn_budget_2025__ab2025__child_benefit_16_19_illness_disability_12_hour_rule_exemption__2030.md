# Investigation packet: autumn_budget_2025 / ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Child Benefit: Exempt 16–19-year-olds with an illness or disability from the 12-hour weekly rule and equalise the treatment of non-standard educational settings from 1 September 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12089:2db7f7ee5d104f20 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23548:b16308c3d3827b3c | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12089:2db7f7ee5d104f20 (row 12089) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 0.8 | — | — |
| head | obr_pmd_nov2025:23548:b16308c3d3827b3c (row 23548) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -27.2 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
