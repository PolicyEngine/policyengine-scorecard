# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_standard_allowance_above_inflation / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23330:9881d3a86b7a4bbc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 | -409.5 | -731.5 | -322.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23342:0fd5ad27ca12101a | — | — | — | — | — |
| measure_year | total | -409.5 | -731.5 | -322.0 | numerical | move_above_threshold |
| head | universal_credit | -409.5 | -731.5 | -322.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:23330:9881d3a86b7a4bbc (row 23330) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -205.0 | — | — |
| obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 (row 23336) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -938.1 | -409.5 | -731.5 |
| obr_pmd_nov2025:23342:0fd5ad27ca12101a (row 23342) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027.json` (sha256 `6f47a7fe1b09a531640bd4ed65f0cd76fb1bc5f67e24ef439b258cf715192332`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027.json` (sha256 `42f38d30547ff4635fcd27370d6102e1a89f680e42af906874960c7214de3925`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027
```

## Sources the registry cites

* https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
