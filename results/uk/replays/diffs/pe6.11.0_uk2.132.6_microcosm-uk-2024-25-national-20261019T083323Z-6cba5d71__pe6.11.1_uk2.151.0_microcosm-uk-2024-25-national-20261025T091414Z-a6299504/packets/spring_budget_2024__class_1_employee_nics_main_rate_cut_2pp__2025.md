# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10952:4fd6a5a070b4cece | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10958:c7a912de7a1a9114 | -11,327.6 | -11,126.7 | 200.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10964:a7faf866a29dd04c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22171:93d8943dfe121528 | 198.5 | 174.9 | -23.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22177:7951bb67665daeb2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22183:bc17379ef6f3a48b | — | — | — | — | — |
| measure_year | total | -11,129.1 | -10,951.8 | 177.3 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,335.4 | -11,132.1 | 203.3 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 7.9 | 5.4 | -2.4 | numerical | move_above_threshold |
| head | universal_credit | 198.5 | 174.9 | -23.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10952:4fd6a5a070b4cece (row 10952) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 259.6 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10958:c7a912de7a1a9114 (row 10958) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,471.7 | -11,327.6 | -11,126.7 |
| base | obr_pmd_nov2025:10964:a7faf866a29dd04c (row 10964) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -257.0 | — | — |
| base | obr_pmd_nov2025:22171:93d8943dfe121528 (row 22171) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 153.5 | 198.5 | 174.9 |
| base | obr_pmd_nov2025:22177:7951bb67665daeb2 (row 22177) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 2.3 | — | — |
| base | obr_pmd_nov2025:22183:bc17379ef6f3a48b (row 22183) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 18.7 | — | — |
| head | obr_pmd_nov2025:10952:4fd6a5a070b4cece (row 10952) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 259.6 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10958:c7a912de7a1a9114 (row 10958) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,471.7 | -11,327.6 | -11,126.7 |
| head | obr_pmd_nov2025:10964:a7faf866a29dd04c (row 10964) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -257.0 | — | — |
| head | obr_pmd_nov2025:22171:93d8943dfe121528 (row 22171) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 153.5 | 198.5 | 174.9 |
| head | obr_pmd_nov2025:22177:7951bb67665daeb2 (row 22177) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 2.3 | — | — |
| head | obr_pmd_nov2025:22183:bc17379ef6f3a48b (row 22183) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 18.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025.json` (sha256 `e3fc7895fb8284fbd11fc5ab51c6c580fa29c3f3d9647d230d3b7d57e0322411`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025.json` (sha256 `d5ec66727171f2295cb55aef166d6e39175b997b357b3a922a71ea3655be90be`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
