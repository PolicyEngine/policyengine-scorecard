# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12339:f1cbe0cc8417d518 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12345:62f5602cdc68a152 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12351:0722288bec0713d2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23966:68d7c7b9372ff8ee | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23972:f23aa7a5db4c06fc | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12339:f1cbe0cc8417d518 (row 12339) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -50.8 | — | 0.0 |
| head | obr_pmd_nov2025:12345:62f5602cdc68a152 (row 12345) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -21.5 | — | 0.0 |
| head | obr_pmd_nov2025:12351:0722288bec0713d2 (row 12351) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 1.1 | — | — |
| head | obr_pmd_nov2025:23966:68d7c7b9372ff8ee (row 23966) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.5 | — | — |
| head | obr_pmd_nov2025:23972:f23aa7a5db4c06fc (row 23972) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -3.5 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2028.json` (sha256 `fd1a12ef068d0370864223063ac2629283a49a82c2db2da78c33eadc7948bdcc`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
