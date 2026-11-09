# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 | 0.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24152:3f0b4da150453149 | -1,143.3 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24158:73455589333cbd4a | — | — | — | — | — |
| measure_year | total | -1,143.3 | 0.0 | 1,143.3 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,143.3 | -0.0 | 1,143.3 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 (row 12717) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 490.7 | 0.0 | — |
| base | obr_pmd_nov2025:24152:3f0b4da150453149 (row 24152) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,693.9 | -1,143.3 | — |
| base | obr_pmd_nov2025:24158:73455589333cbd4a (row 24158) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -127.3 | — | — |
| head | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 (row 12717) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 490.7 | 0.0 | — |
| head | obr_pmd_nov2025:24152:3f0b4da150453149 (row 24152) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,693.9 | -1,143.3 | — |
| head | obr_pmd_nov2025:24158:73455589333cbd4a (row 24158) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -127.3 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028.json` (sha256 `80ba3d22311b57d7e7ed5617a2e1f050c5d4ff2e987654c344320e6d46e7bc41`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028.json` (sha256 `693a9827cdfa058de3ead7e3522352a32c44c82b40f6da8185a38beb63f6a72a`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
