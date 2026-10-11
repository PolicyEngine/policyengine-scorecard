# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10232:aa24b205227c35bd | -4,297.5 | -2,781.3 | 1,516.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10238:f00ba92ca8350bec | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20995:8087b1a02a4eee19 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21001:ccc579e7814559b3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21007:877d001aa00f2eaf | — | — | — | — | — |
| measure_year | total | -4,297.5 | -2,781.3 | 1,516.2 | numerical | move_above_threshold |
| head | income_tax | -4,297.5 | -2,781.3 | 1,516.2 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10232:aa24b205227c35bd (row 10232) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -233.9 | -4,297.5 | -2,781.3 |
| obr_pmd_nov2025:10238:f00ba92ca8350bec (row 10238) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -14.4 | 0.0 | 0.0 |
| obr_pmd_nov2025:20995:8087b1a02a4eee19 (row 20995) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | -16.7 | — | — |
| obr_pmd_nov2025:21001:ccc579e7814559b3 (row 21001) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Net public service pension payments | 67.8 | — | — |
| obr_pmd_nov2025:21007:877d001aa00f2eaf (row 21007) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | -0.5 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024.json` (sha256 `e8e41b75b27a9fcf68b4dd1ddd4498bed2162c42ffdbb1499b532cfa6f922554`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024.json` (sha256 `a8039939f2ab7038772dd622e96d37ec8ddd5eca9c86ca4c325e5bc1a74d5d4e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2023__pension_annual_allowance_package --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2023__pension_annual_allowance_package --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
