# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10233:f9cad5be5ec138c8 | -5,395.1 | -3,047.4 | 2,347.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10239:eae2e7a942d667da | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20996:18794ff6dbde2924 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21002:97562450c81ff19c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21008:3fcd0f4987e122f2 | — | — | — | — | — |
| measure_year | total | -5,395.1 | -3,047.4 | 2,347.7 | numerical | move_above_threshold |
| head | income_tax | -5,395.1 | -3,047.4 | 2,347.7 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10233:f9cad5be5ec138c8 (row 10233) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -405.0 | -5,395.1 | -3,047.4 |
| obr_pmd_nov2025:10239:eae2e7a942d667da (row 10239) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -20.6 | 0.0 | 0.0 |
| obr_pmd_nov2025:20996:18794ff6dbde2924 (row 20996) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -28.7 | — | — |
| obr_pmd_nov2025:21002:97562450c81ff19c (row 21002) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Net public service pension payments | 186.2 | — | — |
| obr_pmd_nov2025:21008:3fcd0f4987e122f2 (row 21008) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.9 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025.json` (sha256 `64dba3c5fb37101d55915559ede077a03a75dcfb37be9d135a228205f8432598`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025.json` (sha256 `0b70828cc20dd5e3bf3ce0f264629be7e70127bf292a9bc08e20824669f7d59f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2023__pension_annual_allowance_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2023__pension_annual_allowance_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
