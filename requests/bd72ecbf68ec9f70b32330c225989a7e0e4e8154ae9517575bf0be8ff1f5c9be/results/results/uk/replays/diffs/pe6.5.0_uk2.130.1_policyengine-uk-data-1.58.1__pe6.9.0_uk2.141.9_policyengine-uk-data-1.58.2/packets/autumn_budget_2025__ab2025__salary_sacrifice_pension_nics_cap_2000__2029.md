# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: numerical, structural
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12340:56a6872c6215ff54 | 119.2 | -682.3 | -801.5 | numerical, structural | move_above_threshold; sign_reversal |
| source_row | obr_pmd_nov2025:12346:3b87f6a01f129a2e | 2,131.3 | 2,779.1 | 647.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12352:de2a74b6a1944c9b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23973:beed70e727200ebb | — | — | — | — | — |
| measure_year | total | 2,250.5 | 2,096.8 | -153.7 | numerical | move_above_threshold |
| head | income_tax | 119.2 | -682.3 | -801.5 | numerical, structural | move_above_threshold; sign_reversal |
| head | ni_class_1_employee | 263.9 | 363.9 | 100.1 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,867.4 | 2,415.3 | 547.9 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | -0.1 | -0.1 | structural | sign_reversal |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | 119.2 | -682.3 |
| base | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | 2,131.3 | 2,779.1 |
| base | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| base | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| base | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |
| head | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | 119.2 | -682.3 |
| head | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | 2,131.3 | 2,779.1 |
| head | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| head | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| head | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `df1aca35339a04dfc2b5fe96eb3a2b0022323c12b2affb805f77c250ac68f3c3`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `45efa3b6d755ceed8822859eae9e97461521acb3eab49755dfd4613c4489dc11`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
