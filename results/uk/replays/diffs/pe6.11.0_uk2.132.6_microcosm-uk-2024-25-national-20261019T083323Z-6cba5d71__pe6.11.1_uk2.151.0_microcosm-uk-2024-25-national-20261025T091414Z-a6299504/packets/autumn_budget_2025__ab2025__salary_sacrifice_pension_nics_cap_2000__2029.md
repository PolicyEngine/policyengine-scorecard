# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: numerical, structural
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12340:56a6872c6215ff54 | 166.5 | -729.5 | -896.0 | numerical, structural | move_above_threshold; sign_reversal |
| source_row | obr_pmd_nov2025:12346:3b87f6a01f129a2e | 1,988.0 | 3,565.5 | 1,577.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12352:de2a74b6a1944c9b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23973:beed70e727200ebb | — | — | — | — | — |
| measure_year | total | 2,154.5 | 2,835.9 | 681.4 | numerical | move_above_threshold |
| head | income_tax | 166.5 | -729.5 | -896.0 | numerical, structural | move_above_threshold; sign_reversal |
| head | ni_class_1_employee | 265.4 | 464.9 | 199.5 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,723.7 | 3,100.5 | 1,376.8 | numerical | move_above_threshold |
| head | ni_class_4 | -1.1 | 0.1 | 1.2 | numerical, structural | move_above_threshold; sign_reversal |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | 166.5 | -729.5 |
| base | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | 1,988.0 | 3,565.5 |
| base | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| base | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| base | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |
| head | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | 166.5 | -729.5 |
| head | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | 1,988.0 | 3,565.5 |
| head | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| head | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| head | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `c6a4edb908a7813713d6d7bfdc8c34efb6af7075021b6e562773ebd6893de04e`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `95fb6ef783c67263b2b53b2ee3243ff65cfa9b2fcf1762a8460f2802d69062b9`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
