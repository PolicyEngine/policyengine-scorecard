# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12719:670f8310e3289a5b | 0.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24154:67e883d6279cdc10 | -1,137.4 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24160:0419e9d97e55970a | — | — | — | — | — |
| measure_year | total | -1,137.4 | 0.0 | 1,137.4 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,137.4 | -0.0 | 1,137.4 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12719:670f8310e3289a5b (row 12719) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 561.7 | 0.0 | — |
| base | obr_pmd_nov2025:24154:67e883d6279cdc10 (row 24154) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -1,753.8 | -1,137.4 | — |
| base | obr_pmd_nov2025:24160:0419e9d97e55970a (row 24160) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -132.0 | — | — |
| head | obr_pmd_nov2025:12719:670f8310e3289a5b (row 12719) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 561.7 | 0.0 | — |
| head | obr_pmd_nov2025:24154:67e883d6279cdc10 (row 24154) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -1,753.8 | -1,137.4 | — |
| head | obr_pmd_nov2025:24160:0419e9d97e55970a (row 24160) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -132.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030.json` (sha256 `a2c3c57052a3b5ab3c60d21f53d0b83da69159d57fbf620ff3b71d10454c607d`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030.json` (sha256 `67758c1321f2e2791d968039600e0c358d2ecd3852f73203107a1e91fca52f76`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
