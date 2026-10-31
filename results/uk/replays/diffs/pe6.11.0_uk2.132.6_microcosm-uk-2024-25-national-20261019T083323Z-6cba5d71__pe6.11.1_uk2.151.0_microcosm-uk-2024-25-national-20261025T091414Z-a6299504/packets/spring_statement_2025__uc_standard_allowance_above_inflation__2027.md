# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_standard_allowance_above_inflation / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30
* Flags: numerical, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23330:9881d3a86b7a4bbc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 | -733.4 | -1,142.7 | -409.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23342:0fd5ad27ca12101a | — | — | — | — | — |
| measure_year | total | -733.4 | -1,142.7 | -409.3 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | -733.4 | -1,142.7 | -409.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23330:9881d3a86b7a4bbc (row 23330) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -205.0 | — | — |
| base | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 (row 23336) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -938.1 | -733.4 | -1,142.7 |
| base | obr_pmd_nov2025:23342:0fd5ad27ca12101a (row 23342) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23330:9881d3a86b7a4bbc (row 23330) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -205.0 | — | — |
| head | obr_pmd_nov2025:23336:5d8fea1a1f3c86d6 (row 23336) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -938.1 | -733.4 | -1,142.7 |
| head | obr_pmd_nov2025:23342:0fd5ad27ca12101a (row 23342) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027.json` (sha256 `0dc083d4f1503c5059c33b6e4fb63edff890d72c65cf34a258d623a29e7a91e0`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027.json` (sha256 `d88327f50d60ea25ffdd8d481f102853a6f9d14a4af5ff5f9a684399f522667f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2027
```

## Sources the registry cites

* base: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025
* head: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
