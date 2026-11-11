# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12340:56a6872c6215ff54 | -729.5 | -751.6 | -22.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12346:3b87f6a01f129a2e | 3,565.5 | 3,568.5 | 3.1 | — | — |
| source_row | obr_pmd_nov2025:12352:de2a74b6a1944c9b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23973:beed70e727200ebb | — | — | — | — | — |
| measure_year | total | 2,835.9 | 2,816.9 | -19.0 | — | — |
| head | income_tax | -729.5 | -751.6 | -22.0 | numerical | move_above_threshold |
| head | ni_class_1_employee | 464.9 | 460.5 | -4.4 | — | — |
| head | ni_class_1_employer | 3,100.5 | 3,108.0 | 7.5 | — | — |
| head | ni_class_4 | 0.1 | 0.0 | -0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | -729.5 | -751.6 |
| base | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | 3,565.5 | 3,568.5 |
| base | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| base | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| base | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |
| head | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | -729.5 | -751.6 |
| head | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | 3,565.5 | 3,568.5 |
| head | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| head | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| head | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `95fb6ef783c67263b2b53b2ee3243ff65cfa9b2fcf1762a8460f2802d69062b9`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `d0b8f7d9dd27a9fe825b8ee9d370bdcc3d74e2ad9eb16a0731a6b011772e0a96`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
