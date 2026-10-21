# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_standard_allowance_above_inflation / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23331:f2f010bd76ffdb79 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23337:31f0f1693e3bba3c | -746.6 | -1,152.6 | -406.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23343:1625c8ea224af25e | — | — | — | — | — |
| measure_year | total | -746.6 | -1,152.6 | -406.0 | numerical | move_above_threshold |
| head | universal_credit | -746.6 | -1,152.6 | -406.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23331:f2f010bd76ffdb79 (row 23331) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -268.0 | — | — |
| base | obr_pmd_nov2025:23337:31f0f1693e3bba3c (row 23337) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,224.4 | -746.6 | -1,152.6 |
| base | obr_pmd_nov2025:23343:1625c8ea224af25e (row 23343) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23331:f2f010bd76ffdb79 (row 23331) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -268.0 | — | — |
| head | obr_pmd_nov2025:23337:31f0f1693e3bba3c (row 23337) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,224.4 | -746.6 | -1,152.6 |
| head | obr_pmd_nov2025:23343:1625c8ea224af25e (row 23343) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2028.json` (sha256 `3bfe1fe12ecc0d8997f6bd942716abfe32cf0d7a48ac85c69e7b83fb549f63af`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2028.json` (sha256 `5db98d56f9af2ec0aa0ce71067ecaf0e88ae3580efb3b72202c9de4da53e8069`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {"2026-01-01.2026-12-31": 651.97, "2027-01-01.2027-12-31": 666.96, "2028-01-01.2028-12-31": 680.3, "2029-01-01.2029-12-31": 693.91}, "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {"2026-01-01.2026-12-31": 516.46, "2027-01-01.2027-12-31": 528.33, "2028-01-01.2028-12-31": 538.9, "2029-01-01.2029-12-31": 549.68}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {"2026-01-01.2026-12-31": 415.35, "2027-01-01.2027-12-31": 424.9, "2028-01-01.2028-12-31": 433.39, "2029-01-01.2029-12-31": 442.06}, "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {"2026-01-01.2026-12-31": 329.03, "2027-01-01.2027-12-31": 336.59, "2028-01-01.2028-12-31": 343.32, "2029-01-01.2029-12-31": 350.19}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2028
```

## Sources the registry cites

* base: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025
* head: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2025

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
