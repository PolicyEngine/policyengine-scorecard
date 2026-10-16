# Investigation packet: autumn_budget_2025 / ab2025__salary_sacrifice_pension_nics_cap_2000 / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12337:3b045b83864340cb | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12343:b79b48811830e061 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12349:62c228b05eaaf660 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23964:2443fe5bded00bd3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23970:3ec40cddcc137aad | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12337:3b045b83864340cb (row 12337) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -25.4 | — | 0.0 |
| head | obr_pmd_nov2025:12343:b79b48811830e061 (row 12343) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -10.7 | — | 0.0 |
| head | obr_pmd_nov2025:12349:62c228b05eaaf660 (row 12349) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 0.5 | — | — |
| head | obr_pmd_nov2025:23964:2443fe5bded00bd3 (row 23964) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -0.3 | — | — |
| head | obr_pmd_nov2025:23970:3ec40cddcc137aad (row 23970) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -1.7 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2026.json` (sha256 `9a4468f67cfbf9c53d0e69ed2fd68087d342f36e87c3ad7089489b6361e2e0f2`), reversal_on_certified_world; baseline dict `{"gov.contrib.behavioral_responses.salary_sacrifice_broad_base_haircut_rate": {"2029-01-01.2030-12-31": 0.0}, "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {"2029-01-01.2030-12-31": 1e+100}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
