# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10235:fbb8ccda250b78e9 | -3,725.2 | -3,120.6 | 604.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10241:b45d113eb69a2a68 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20998:5405e18b093611d0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21004:4de031e5ab4ad901 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21010:b33224f6af5b4ee6 | — | — | — | — | — |
| measure_year | total | -3,725.2 | -3,120.6 | 604.6 | numerical | move_above_threshold |
| head | income_tax | -3,725.2 | -3,120.6 | 604.6 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10235:fbb8ccda250b78e9 (row 10235) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -420.4 | -3,725.2 | -3,120.6 |
| base | obr_pmd_nov2025:10241:b45d113eb69a2a68 (row 10241) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -21.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:20998:5405e18b093611d0 (row 20998) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -30.2 | — | — |
| base | obr_pmd_nov2025:21004:4de031e5ab4ad901 (row 21004) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Net public service pension payments | 183.3 | — | — |
| base | obr_pmd_nov2025:21010:b33224f6af5b4ee6 (row 21010) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -0.6 | — | — |
| head | obr_pmd_nov2025:10235:fbb8ccda250b78e9 (row 10235) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -420.4 | -3,725.2 | -3,120.6 |
| head | obr_pmd_nov2025:10241:b45d113eb69a2a68 (row 10241) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -21.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:20998:5405e18b093611d0 (row 20998) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -30.2 | — | — |
| head | obr_pmd_nov2025:21004:4de031e5ab4ad901 (row 21004) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Net public service pension payments | 183.3 | — | — |
| head | obr_pmd_nov2025:21010:b33224f6af5b4ee6 (row 21010) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -0.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2027.json` (sha256 `d2f9d714e1d75a1d0b347b290bfa70e547c75622492725fcd600c506941865bc`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2027.json` (sha256 `154e9a26aac6070e2c977e72ec05a26eecf921be85af2e955ac79b214c2901a1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
