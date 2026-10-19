# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10233:f9cad5be5ec138c8 | -3,300.7 | -2,938.9 | 361.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10239:eae2e7a942d667da | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20996:18794ff6dbde2924 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21002:97562450c81ff19c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21008:3fcd0f4987e122f2 | — | — | — | — | — |
| measure_year | total | -3,300.7 | -2,938.9 | 361.8 | numerical | move_above_threshold |
| head | income_tax | -3,300.7 | -2,938.9 | 361.8 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10233:f9cad5be5ec138c8 (row 10233) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -405.0 | -3,300.7 | -2,938.9 |
| base | obr_pmd_nov2025:10239:eae2e7a942d667da (row 10239) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -20.6 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:20996:18794ff6dbde2924 (row 20996) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -28.7 | — | — |
| base | obr_pmd_nov2025:21002:97562450c81ff19c (row 21002) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Net public service pension payments | 186.2 | — | — |
| base | obr_pmd_nov2025:21008:3fcd0f4987e122f2 (row 21008) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.9 | — | — |
| head | obr_pmd_nov2025:10233:f9cad5be5ec138c8 (row 10233) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -405.0 | -3,300.7 | -2,938.9 |
| head | obr_pmd_nov2025:10239:eae2e7a942d667da (row 10239) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -20.6 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:20996:18794ff6dbde2924 (row 20996) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -28.7 | — | — |
| head | obr_pmd_nov2025:21002:97562450c81ff19c (row 21002) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Net public service pension payments | 186.2 | — | — |
| head | obr_pmd_nov2025:21008:3fcd0f4987e122f2 (row 21008) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025.json` (sha256 `15c6e033b303a51fa189cbb14399803c6b90b5178d9cf62fc09a4c51daa66e0f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025.json` (sha256 `5f28a1446045ae15952aeb6a33ddd41a1525ab78be718d1bd8d259ad603e3430`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
