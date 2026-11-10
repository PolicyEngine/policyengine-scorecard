# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10971:395ed623a9b23942 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10977:57eced9fbf6bab3b | -722.1 | -742.5 | -20.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10983:7b2d9bff53b719f4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22190:dc5ace295177c84b | 33.2 | 36.2 | 3.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22196:7b25d8523b72e3f3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22202:b518451c4427e13f | — | — | — | — | — |
| measure_year | total | -688.9 | -706.3 | -17.4 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -722.1 | -742.5 | -20.4 | numerical | move_above_threshold |
| head | universal_credit | 33.2 | 36.2 | 3.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10971:395ed623a9b23942 (row 10971) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 190.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10977:57eced9fbf6bab3b (row 10977) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -699.5 | -722.1 | -742.5 |
| base | obr_pmd_nov2025:10983:7b2d9bff53b719f4 (row 10983) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -261.5 | — | — |
| base | obr_pmd_nov2025:22190:dc5ace295177c84b (row 22190) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 12.4 | 33.2 | 36.2 |
| base | obr_pmd_nov2025:22196:7b25d8523b72e3f3 (row 22196) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 2.1 | — | — |
| base | obr_pmd_nov2025:22202:b518451c4427e13f (row 22202) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 18.5 | — | — |
| head | obr_pmd_nov2025:10971:395ed623a9b23942 (row 10971) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 190.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10977:57eced9fbf6bab3b (row 10977) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -699.5 | -722.1 | -742.5 |
| head | obr_pmd_nov2025:10983:7b2d9bff53b719f4 (row 10983) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -261.5 | — | — |
| head | obr_pmd_nov2025:22190:dc5ace295177c84b (row 22190) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 12.4 | 33.2 | 36.2 |
| head | obr_pmd_nov2025:22196:7b25d8523b72e3f3 (row 22196) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 2.1 | — | — |
| head | obr_pmd_nov2025:22202:b518451c4427e13f (row 22202) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 18.5 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026.json` (sha256 `77706763f1cf020b2137e044a6a3488ed930550424112d4d661abe7e6315b951`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026.json` (sha256 `6783374f90bd21eb705868e5382644552670461c46fbbc9156d570019337e556`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
