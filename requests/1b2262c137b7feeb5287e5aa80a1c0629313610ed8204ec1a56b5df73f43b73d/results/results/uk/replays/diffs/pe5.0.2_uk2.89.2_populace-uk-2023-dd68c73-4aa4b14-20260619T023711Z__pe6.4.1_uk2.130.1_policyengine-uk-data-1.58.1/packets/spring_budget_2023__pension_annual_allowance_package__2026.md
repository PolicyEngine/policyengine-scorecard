# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10234:7fb22cdd33e49932 | -6,040.7 | -3,540.3 | 2,500.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10240:c53005dc3f74f60f | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20997:a2d202e6d4474250 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21003:24d20cb8f6deed27 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21009:ca378bb43ec6d967 | — | — | — | — | — |
| measure_year | total | -6,040.7 | -3,540.3 | 2,500.5 | numerical | move_above_threshold |
| head | income_tax | -6,040.7 | -3,540.3 | 2,500.5 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10234:7fb22cdd33e49932 (row 10234) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -414.6 | -6,040.7 | -3,540.3 |
| base | obr_pmd_nov2025:10240:c53005dc3f74f60f (row 10240) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -21.1 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:20997:a2d202e6d4474250 (row 20997) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -29.5 | — | — |
| base | obr_pmd_nov2025:21003:24d20cb8f6deed27 (row 21003) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Net public service pension payments | 196.3 | — | — |
| base | obr_pmd_nov2025:21009:ca378bb43ec6d967 (row 21009) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -0.8 | — | — |
| head | obr_pmd_nov2025:10234:7fb22cdd33e49932 (row 10234) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -414.6 | -6,040.7 | -3,540.3 |
| head | obr_pmd_nov2025:10240:c53005dc3f74f60f (row 10240) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -21.1 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:20997:a2d202e6d4474250 (row 20997) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -29.5 | — | — |
| head | obr_pmd_nov2025:21003:24d20cb8f6deed27 (row 21003) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Net public service pension payments | 196.3 | — | — |
| head | obr_pmd_nov2025:21009:ca378bb43ec6d967 (row 21009) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -0.8 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2026.json` (sha256 `632dae64fed7ec57ab16a5659f2917abbbb4d3ec4f5ddb66d7c0cadcd1aa891d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2026.json` (sha256 `f0f5a287d5dcd6e8f39ba9b6baabcde03f1f92023c0195f8a29f2629a3c1d587`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
