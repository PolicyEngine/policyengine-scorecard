# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10231:ce0a1472426c8430 | -3,693.2 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10237:2f261725299509e1 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:20994:3447da176e4bc085 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21000:c0139e6de0095ba4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21006:5ca828fbfe74cf61 | — | — | — | — | — |
| measure_year | total | -3,693.2 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10231:ce0a1472426c8430 (row 10231) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | -80.9 | -3,693.2 | — |
| base | obr_pmd_nov2025:10237:2f261725299509e1 (row 10237) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | -9.0 | 0.0 | — |
| base | obr_pmd_nov2025:20994:3447da176e4bc085 (row 20994) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | -5.8 | — | — |
| base | obr_pmd_nov2025:21000:c0139e6de0095ba4 (row 21000) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Net public service pension payments | 42.3 | — | — |
| base | obr_pmd_nov2025:21006:5ca828fbfe74cf61 (row 21006) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | -0.1 | — | — |
| head | obr_pmd_nov2025:10231:ce0a1472426c8430 (row 10231) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | -80.9 | -3,693.2 | — |
| head | obr_pmd_nov2025:10237:2f261725299509e1 (row 10237) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | -9.0 | 0.0 | — |
| head | obr_pmd_nov2025:20994:3447da176e4bc085 (row 20994) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | -5.8 | — | — |
| head | obr_pmd_nov2025:21000:c0139e6de0095ba4 (row 21000) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Net public service pension payments | 42.3 | — | — |
| head | obr_pmd_nov2025:21006:5ca828fbfe74cf61 (row 21006) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | -0.1 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2023.json` (sha256 `ed71ced0005bee9267a0d5dcb11f01520bb353d7065560fad2cd58b814bca3ff`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2023
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
