# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10952:4fd6a5a070b4cece | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10958:c7a912de7a1a9114 | -11,126.7 | -11,417.3 | -290.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10964:a7faf866a29dd04c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22171:93d8943dfe121528 | 174.9 | 187.6 | 12.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22177:7951bb67665daeb2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22183:bc17379ef6f3a48b | — | — | — | — | — |
| measure_year | total | -10,951.8 | -11,229.8 | -278.0 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,132.1 | -11,420.6 | -288.4 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 5.4 | 3.2 | -2.2 | numerical | move_above_threshold |
| head | universal_credit | 174.9 | 187.6 | 12.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10952:4fd6a5a070b4cece (row 10952) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 259.6 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10958:c7a912de7a1a9114 (row 10958) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,471.7 | -11,126.7 | -11,417.3 |
| base | obr_pmd_nov2025:10964:a7faf866a29dd04c (row 10964) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -257.0 | — | — |
| base | obr_pmd_nov2025:22171:93d8943dfe121528 (row 22171) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 153.5 | 174.9 | 187.6 |
| base | obr_pmd_nov2025:22177:7951bb67665daeb2 (row 22177) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 2.3 | — | — |
| base | obr_pmd_nov2025:22183:bc17379ef6f3a48b (row 22183) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 18.7 | — | — |
| head | obr_pmd_nov2025:10952:4fd6a5a070b4cece (row 10952) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 259.6 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10958:c7a912de7a1a9114 (row 10958) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,471.7 | -11,126.7 | -11,417.3 |
| head | obr_pmd_nov2025:10964:a7faf866a29dd04c (row 10964) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -257.0 | — | — |
| head | obr_pmd_nov2025:22171:93d8943dfe121528 (row 22171) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 153.5 | 174.9 | 187.6 |
| head | obr_pmd_nov2025:22177:7951bb67665daeb2 (row 22177) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 2.3 | — | — |
| head | obr_pmd_nov2025:22183:bc17379ef6f3a48b (row 22183) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 18.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025.json` (sha256 `d5ec66727171f2295cb55aef166d6e39175b997b357b3a922a71ea3655be90be`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025.json` (sha256 `2d8b048f75c6c858724fb349c6a3d886c238075a08affc1c300e76ec6e3ca225`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
