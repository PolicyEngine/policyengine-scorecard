# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_standard_allowance_above_inflation / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23332:5c8171523fd97b4c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23338:27e34c93a163b4f0 | -421.9 | -753.2 | -331.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23344:786ad47c268163cb | — | — | — | — | — |
| measure_year | total | -421.9 | -753.2 | -331.4 | numerical | move_above_threshold |
| head | universal_credit | -421.9 | -753.2 | -331.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23332:5c8171523fd97b4c (row 23332) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare outside cap | -338.0 | — | — |
| base | obr_pmd_nov2025:23338:27e34c93a163b4f0 (row 23338) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -1,546.1 | -421.9 | -753.2 |
| base | obr_pmd_nov2025:23344:786ad47c268163cb (row 23344) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23332:5c8171523fd97b4c (row 23332) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare outside cap | -338.0 | — | — |
| head | obr_pmd_nov2025:23338:27e34c93a163b4f0 (row 23338) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -1,546.1 | -421.9 | -753.2 |
| head | obr_pmd_nov2025:23344:786ad47c268163cb (row 23344) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2029.json` (sha256 `1b36b51794d1b3382fec9c03d97e5a9c8aeb0669446d8dfb7d70413e1aa26027`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2029.json` (sha256 `4b06d1b0f9a41298a4d2d25dc8228179bd8e345301890eb9dc75a1ca1f4a40ae`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2029
```

## Sources the registry cites

* base: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025
* head: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
