# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: numerical, structural
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12341:ce174c39c117892d | 236.5 | -759.4 | -995.9 | numerical, structural | move_above_threshold; sign_reversal |
| source_row | obr_pmd_nov2025:12347:687b6f32b91450d1 | 1,982.1 | 3,699.2 | 1,717.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12353:cddf67051176b3d2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23968:50cda063301b35eb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23974:5b32bac74f033733 | — | — | — | — | — |
| measure_year | total | 2,218.6 | 2,939.8 | 721.2 | numerical | move_above_threshold |
| head | income_tax | 236.5 | -759.4 | -995.9 | numerical, structural | move_above_threshold; sign_reversal |
| head | ni_class_1_employee | 259.1 | 479.4 | 220.2 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,723.5 | 3,219.8 | 1,496.3 | numerical | move_above_threshold |
| head | ni_class_4 | -0.5 | 0.1 | 0.6 | structural | sign_reversal |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12341:ce174c39c117892d (row 12341) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -714.5 | 236.5 | -759.4 |
| base | obr_pmd_nov2025:12347:687b6f32b91450d1 (row 12347) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 3,531.4 | 1,982.1 | 3,699.2 |
| base | obr_pmd_nov2025:12353:cddf67051176b3d2 (row 12353) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -177.3 | — | — |
| base | obr_pmd_nov2025:23968:50cda063301b35eb (row 23968) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -7.5 | — | — |
| base | obr_pmd_nov2025:23974:5b32bac74f033733 (row 23974) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -48.6 | — | — |
| head | obr_pmd_nov2025:12341:ce174c39c117892d (row 12341) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -714.5 | 236.5 | -759.4 |
| head | obr_pmd_nov2025:12347:687b6f32b91450d1 (row 12347) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 3,531.4 | 1,982.1 | 3,699.2 |
| head | obr_pmd_nov2025:12353:cddf67051176b3d2 (row 12353) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -177.3 | — | — |
| head | obr_pmd_nov2025:23968:50cda063301b35eb (row 23968) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -7.5 | — | — |
| head | obr_pmd_nov2025:23974:5b32bac74f033733 (row 23974) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -48.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030.json` (sha256 `1d0e46c2e52f8baae7435d72eb63c91eb36003e87ad19ff9728167dd376e0642`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030.json` (sha256 `6cac7ca49d250560055c628e5ed491973fc6c99af83c48a75df27dcd3aa78bad`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
