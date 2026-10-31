# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10233:f9cad5be5ec138c8 | -2,625.6 | -2,526.5 | 99.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10239:eae2e7a942d667da | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20996:18794ff6dbde2924 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21002:97562450c81ff19c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21008:3fcd0f4987e122f2 | — | — | — | — | — |
| measure_year | total | -2,625.6 | -2,526.5 | 99.2 | numerical | move_above_threshold |
| head | income_tax | -2,625.6 | -2,526.5 | 99.2 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10233:f9cad5be5ec138c8 (row 10233) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -405.0 | -2,625.6 | -2,526.5 |
| base | obr_pmd_nov2025:10239:eae2e7a942d667da (row 10239) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -20.6 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:20996:18794ff6dbde2924 (row 20996) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -28.7 | — | — |
| base | obr_pmd_nov2025:21002:97562450c81ff19c (row 21002) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Net public service pension payments | 186.2 | — | — |
| base | obr_pmd_nov2025:21008:3fcd0f4987e122f2 (row 21008) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.9 | — | — |
| head | obr_pmd_nov2025:10233:f9cad5be5ec138c8 (row 10233) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -405.0 | -2,625.6 | -2,526.5 |
| head | obr_pmd_nov2025:10239:eae2e7a942d667da (row 10239) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -20.6 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:20996:18794ff6dbde2924 (row 20996) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -28.7 | — | — |
| head | obr_pmd_nov2025:21002:97562450c81ff19c (row 21002) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Net public service pension payments | 186.2 | — | — |
| head | obr_pmd_nov2025:21008:3fcd0f4987e122f2 (row 21008) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025.json` (sha256 `4ddb613642163b2083417e9de81ae4da41ea4adce88e2ee1995eafba2a87ac1f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025.json` (sha256 `ceef9a7848abd1eb0ba9c1ed4935546ee2d0edda28aa59a9a94b1d98caedf858`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
