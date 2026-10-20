# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: numerical, structural
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12341:ce174c39c117892d | 213.1 | -711.9 | -925.0 | numerical, structural | move_above_threshold; sign_reversal |
| source_row | obr_pmd_nov2025:12347:687b6f32b91450d1 | 2,129.2 | 2,124.5 | -4.7 | — | — |
| source_row | obr_pmd_nov2025:12353:cddf67051176b3d2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23968:50cda063301b35eb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23974:5b32bac74f033733 | — | — | — | — | — |
| measure_year | total | 2,342.3 | 1,412.6 | -929.7 | numerical | move_above_threshold |
| head | income_tax | 213.1 | -711.9 | -925.0 | numerical, structural | move_above_threshold; sign_reversal |
| head | ni_class_1_employee | 260.9 | 253.6 | -7.3 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,868.2 | 1,870.8 | 2.6 | — | — |
| head | ni_class_4 | 0.1 | 0.0 | -0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12341:ce174c39c117892d (row 12341) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -714.5 | 213.1 | -711.9 |
| base | obr_pmd_nov2025:12347:687b6f32b91450d1 (row 12347) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 3,531.4 | 2,129.2 | 2,124.5 |
| base | obr_pmd_nov2025:12353:cddf67051176b3d2 (row 12353) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -177.3 | — | — |
| base | obr_pmd_nov2025:23968:50cda063301b35eb (row 23968) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -7.5 | — | — |
| base | obr_pmd_nov2025:23974:5b32bac74f033733 (row 23974) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -48.6 | — | — |
| head | obr_pmd_nov2025:12341:ce174c39c117892d (row 12341) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -714.5 | 213.1 | -711.9 |
| head | obr_pmd_nov2025:12347:687b6f32b91450d1 (row 12347) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 3,531.4 | 2,129.2 | 2,124.5 |
| head | obr_pmd_nov2025:12353:cddf67051176b3d2 (row 12353) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -177.3 | — | — |
| head | obr_pmd_nov2025:23968:50cda063301b35eb (row 23968) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -7.5 | — | — |
| head | obr_pmd_nov2025:23974:5b32bac74f033733 (row 23974) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -48.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030.json` (sha256 `1fa4edfece5a469b6efca1a8597001bb7e98802e03df14a4bbf15c2b78de0be9`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030.json` (sha256 `bcc8b82a1c2a900e1506c1197beef01c18f5420516a786a729f87309cc1f2e4a`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
