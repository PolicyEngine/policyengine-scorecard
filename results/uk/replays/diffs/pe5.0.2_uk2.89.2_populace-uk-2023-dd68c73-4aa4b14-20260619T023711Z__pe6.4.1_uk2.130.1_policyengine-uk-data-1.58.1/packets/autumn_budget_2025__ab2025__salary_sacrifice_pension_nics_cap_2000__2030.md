# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12341:ce174c39c117892d | — | 213.1 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12347:687b6f32b91450d1 | — | 2,129.2 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12353:cddf67051176b3d2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23968:50cda063301b35eb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23974:5b32bac74f033733 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 2,342.3 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12341:ce174c39c117892d (row 12341) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -714.5 | — | 213.1 |
| head | obr_pmd_nov2025:12347:687b6f32b91450d1 (row 12347) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 3,531.4 | — | 2,129.2 |
| head | obr_pmd_nov2025:12353:cddf67051176b3d2 (row 12353) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -177.3 | — | — |
| head | obr_pmd_nov2025:23968:50cda063301b35eb (row 23968) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -7.5 | — | — |
| head | obr_pmd_nov2025:23974:5b32bac74f033733 (row 23974) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -48.6 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030.json` (sha256 `fa2ea6f929c75a84a492dead281d2e1d4e3d0fe5595fa49e5efd3d7bcab5cf2b`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
