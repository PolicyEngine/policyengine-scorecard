# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12338:97e677e9d5b1787d | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12344:4e1c69b7573ca567 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12350:73024e01bfa0eb7b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23965:7a50110b34dcfda3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23971:9ccbfc7e5a8ec42d | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12338:97e677e9d5b1787d (row 12338) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -38.1 | — | 0.0 |
| head | obr_pmd_nov2025:12344:4e1c69b7573ca567 (row 12344) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -16.1 | — | 0.0 |
| head | obr_pmd_nov2025:12350:73024e01bfa0eb7b (row 12350) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 0.8 | — | — |
| head | obr_pmd_nov2025:23965:7a50110b34dcfda3 (row 23965) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -0.4 | — | — |
| head | obr_pmd_nov2025:23971:9ccbfc7e5a8ec42d (row 23971) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -2.6 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2027.json` (sha256 `c3687f2193d97b5faea80e06feb8e72a9472e728f6605fec2076b3e0bd5ff5e0`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
