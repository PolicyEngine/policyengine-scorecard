# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10971:395ed623a9b23942 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10977:57eced9fbf6bab3b | -1,167.9 | -696.1 | 471.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10983:7b2d9bff53b719f4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22190:dc5ace295177c84b | 15.4 | 44.1 | 28.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22196:7b25d8523b72e3f3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22202:b518451c4427e13f | — | — | — | — | — |
| measure_year | total | -1,152.5 | -652.0 | 500.5 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -1,167.9 | -696.1 | 471.8 | numerical | move_above_threshold |
| head | universal_credit | 15.4 | 44.1 | 28.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10971:395ed623a9b23942 (row 10971) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 190.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10977:57eced9fbf6bab3b (row 10977) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -699.5 | -1,167.9 | -696.1 |
| base | obr_pmd_nov2025:10983:7b2d9bff53b719f4 (row 10983) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -261.5 | — | — |
| base | obr_pmd_nov2025:22190:dc5ace295177c84b (row 22190) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 12.4 | 15.4 | 44.1 |
| base | obr_pmd_nov2025:22196:7b25d8523b72e3f3 (row 22196) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 2.1 | — | — |
| base | obr_pmd_nov2025:22202:b518451c4427e13f (row 22202) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 18.5 | — | — |
| head | obr_pmd_nov2025:10971:395ed623a9b23942 (row 10971) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 190.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10977:57eced9fbf6bab3b (row 10977) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -699.5 | -1,167.9 | -696.1 |
| head | obr_pmd_nov2025:10983:7b2d9bff53b719f4 (row 10983) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -261.5 | — | — |
| head | obr_pmd_nov2025:22190:dc5ace295177c84b (row 22190) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 12.4 | 15.4 | 44.1 |
| head | obr_pmd_nov2025:22196:7b25d8523b72e3f3 (row 22196) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 2.1 | — | — |
| head | obr_pmd_nov2025:22202:b518451c4427e13f (row 22202) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 18.5 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026.json` (sha256 `d814f3a0c7cb6a75f5dbf50558a56e457ae2b87914d36f77d751ec82bf3b18dd`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026.json` (sha256 `475b9eba4f4391bd6f72339d175c22febe2887d56512423c3b0c348b97a8bb57`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
