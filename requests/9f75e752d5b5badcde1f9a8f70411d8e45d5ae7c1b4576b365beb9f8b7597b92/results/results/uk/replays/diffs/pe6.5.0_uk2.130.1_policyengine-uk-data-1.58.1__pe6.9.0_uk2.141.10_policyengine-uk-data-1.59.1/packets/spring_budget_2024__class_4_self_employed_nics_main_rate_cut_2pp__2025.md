# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10970:e5f920b816ad93c4 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10976:230199453880fc45 | -661.7 | -684.0 | -22.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10982:c5dd8885d4087144 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22189:215059939a4b5efc | 41.9 | 40.6 | -1.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22195:db7688f590170511 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22201:b16f4f7afafa9096 | — | — | — | — | — |
| measure_year | total | -619.9 | -643.4 | -23.5 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -661.7 | -684.0 | -22.2 | numerical | move_above_threshold |
| head | universal_credit | 41.9 | 40.6 | -1.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10970:e5f920b816ad93c4 (row 10970) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -13.6 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10976:230199453880fc45 (row 10976) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -678.4 | -661.7 | -684.0 |
| base | obr_pmd_nov2025:10982:c5dd8885d4087144 (row 10982) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -168.7 | — | — |
| base | obr_pmd_nov2025:22189:215059939a4b5efc (row 22189) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 11.0 | 41.9 | 40.6 |
| base | obr_pmd_nov2025:22195:db7688f590170511 (row 22195) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.1 | — | — |
| base | obr_pmd_nov2025:22201:b16f4f7afafa9096 (row 22201) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -1.0 | — | — |
| head | obr_pmd_nov2025:10970:e5f920b816ad93c4 (row 10970) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -13.6 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10976:230199453880fc45 (row 10976) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -678.4 | -661.7 | -684.0 |
| head | obr_pmd_nov2025:10982:c5dd8885d4087144 (row 10982) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -168.7 | — | — |
| head | obr_pmd_nov2025:22189:215059939a4b5efc (row 22189) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 11.0 | 41.9 | 40.6 |
| head | obr_pmd_nov2025:22195:db7688f590170511 (row 22195) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.1 | — | — |
| head | obr_pmd_nov2025:22201:b16f4f7afafa9096 (row 22201) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -1.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2025.json` (sha256 `959efb8637454eb55a96655c48da22379b3219bab7d955188508fbb4e2d96de4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2025.json` (sha256 `01b741e23b8691dad06d02c52656e452ebb7cd0b33ab7c4192e5299a2bd59836`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
