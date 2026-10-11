# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10969:8dde405208f86bbd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10975:497e18b9ba827fa3 | -1,114.8 | -609.3 | 505.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10981:ee23395fc58c2e94 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22188:9f98363a90ba075c | 12.9 | 36.2 | 23.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22194:376f5e7bc1c25928 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22200:454271d3e97ec8eb | — | — | — | — | — |
| measure_year | total | -1,101.8 | -573.0 | 528.8 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -1,114.8 | -609.3 | 505.5 | numerical | move_above_threshold |
| head | universal_credit | 12.9 | 36.2 | 23.3 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10969:8dde405208f86bbd (row 10969) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| obr_pmd_nov2025:10975:497e18b9ba827fa3 (row 10975) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -666.5 | -1,114.8 | -609.3 |
| obr_pmd_nov2025:10981:ee23395fc58c2e94 (row 10981) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -51.8 | — | — |
| obr_pmd_nov2025:22188:9f98363a90ba075c (row 22188) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 8.3 | 12.9 | 36.2 |
| obr_pmd_nov2025:22194:376f5e7bc1c25928 (row 22194) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| obr_pmd_nov2025:22200:454271d3e97ec8eb (row 22200) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024.json` (sha256 `ffcc6f491732be630b29189d1603666a728313f546618b5e82303e1acdd38434`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024.json` (sha256 `fbd23a5a3c4a87c9f19a1ea3aeef964d3e0a7a4e45fc1c58ab1acf70b3b2eeca`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
