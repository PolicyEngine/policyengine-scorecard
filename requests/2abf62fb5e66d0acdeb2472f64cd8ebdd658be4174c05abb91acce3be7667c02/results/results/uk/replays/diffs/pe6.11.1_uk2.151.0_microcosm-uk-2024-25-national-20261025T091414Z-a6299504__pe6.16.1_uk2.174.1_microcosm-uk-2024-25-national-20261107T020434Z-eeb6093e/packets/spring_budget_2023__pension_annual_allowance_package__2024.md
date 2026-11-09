# Investigation packet: spring_budget_2023 / spring_budget_2023__pension_annual_allowance_package / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10232:aa24b205227c35bd | -2,207.7 | -2,376.4 | -168.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10238:f00ba92ca8350bec | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:20995:8087b1a02a4eee19 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21001:ccc579e7814559b3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21007:877d001aa00f2eaf | — | — | — | — | — |
| measure_year | total | -2,207.7 | -2,376.4 | -168.7 | numerical | move_above_threshold |
| head | income_tax | -2,207.7 | -2,376.4 | -168.7 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10232:aa24b205227c35bd (row 10232) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -233.9 | -2,207.7 | -2,376.4 |
| base | obr_pmd_nov2025:10238:f00ba92ca8350bec (row 10238) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -14.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:20995:8087b1a02a4eee19 (row 20995) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | -16.7 | — | — |
| base | obr_pmd_nov2025:21001:ccc579e7814559b3 (row 21001) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Net public service pension payments | 67.8 | — | — |
| base | obr_pmd_nov2025:21007:877d001aa00f2eaf (row 21007) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | -0.5 | — | — |
| head | obr_pmd_nov2025:10232:aa24b205227c35bd (row 10232) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -233.9 | -2,207.7 | -2,376.4 |
| head | obr_pmd_nov2025:10238:f00ba92ca8350bec (row 10238) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -14.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:20995:8087b1a02a4eee19 (row 20995) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | -16.7 | — | — |
| head | obr_pmd_nov2025:21001:ccc579e7814559b3 (row 21001) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Net public service pension payments | 67.8 | — | — |
| head | obr_pmd_nov2025:21007:877d001aa00f2eaf (row 21007) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | -0.5 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024.json` (sha256 `ee2279b32051a662faba47eb985b747bcc12da84bd38fd335ff256f1a19f7209`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024.json` (sha256 `81f7dd24b0ba2f62012a39a32152fa069925baba979b9529a4e695a55b05f6f7`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.annual_allowance.default": {"2023-01-01.2035-12-31": 40000}, "gov.hmrc.income_tax.allowances.annual_allowance.minimum": {"2023-01-01.2035-12-31": 4000}, "gov.hmrc.income_tax.allowances.annual_allowance.taper": {"2023-01-01.2035-12-31": 240000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__pension_annual_allowance_package --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
