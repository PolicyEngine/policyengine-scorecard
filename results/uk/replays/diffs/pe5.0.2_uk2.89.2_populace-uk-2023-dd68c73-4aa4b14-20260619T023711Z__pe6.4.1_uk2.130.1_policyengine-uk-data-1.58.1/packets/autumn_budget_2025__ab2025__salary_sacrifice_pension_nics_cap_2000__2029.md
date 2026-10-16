# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12340:56a6872c6215ff54 | — | 119.2 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12346:3b87f6a01f129a2e | — | 2,131.3 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12352:de2a74b6a1944c9b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23973:beed70e727200ebb | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 2,250.5 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12340:56a6872c6215ff54 (row 12340) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,390.6 | — | 119.2 |
| head | obr_pmd_nov2025:12346:3b87f6a01f129a2e (row 12346) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 3,522.7 | — | 2,131.3 |
| head | obr_pmd_nov2025:12352:de2a74b6a1944c9b (row 12352) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -176.8 | — | — |
| head | obr_pmd_nov2025:23967:c98aa1d14ad9fd8e (row 23967) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 14.6 | — | — |
| head | obr_pmd_nov2025:23973:beed70e727200ebb (row 23973) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 94.9 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029.json` (sha256 `d286c5f8dc2533f852e0a8877d378de99076f73882640cc89b6f506feb210085`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
