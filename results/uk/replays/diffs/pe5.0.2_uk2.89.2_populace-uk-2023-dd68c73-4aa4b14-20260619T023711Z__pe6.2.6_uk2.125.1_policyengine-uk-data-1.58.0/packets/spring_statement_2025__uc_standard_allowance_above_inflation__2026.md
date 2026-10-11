# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_standard_allowance_above_inflation / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23329:e052a44f1c2e1bfc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23335:7e9f9d66b5194ff6 | -403.7 | -720.9 | -317.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23341:8eed9bf63783ccbd | — | — | — | — | — |
| measure_year | total | -403.7 | -720.9 | -317.2 | numerical | move_above_threshold |
| head | universal_credit | -403.7 | -720.9 | -317.2 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:23329:e052a44f1c2e1bfc (row 23329) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -146.0 | — | — |
| obr_pmd_nov2025:23335:7e9f9d66b5194ff6 (row 23335) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -667.4 | -403.7 | -720.9 |
| obr_pmd_nov2025:23341:8eed9bf63783ccbd (row 23341) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2026.json` (sha256 `37a3baee9f6212fee0d6a719b6487d935adad3edb14b7f1d951c432e9242f69b`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2026.json` (sha256 `30fe29e14a777d3d05d18f3c9ca45ff271e251e0f248bf12a47ec714f839128f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2026
```

## Sources the registry cites

* https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
