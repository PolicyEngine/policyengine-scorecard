# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:24152:3f0b4da150453149 | -1,197.6 | -1,184.9 | 12.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:24158:73455589333cbd4a | — | — | — | — | — |
| measure_year | total | -1,197.6 | -1,184.9 | 12.7 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,197.6 | -1,184.9 | 12.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 (row 12717) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 490.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:24152:3f0b4da150453149 (row 24152) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,693.9 | -1,197.6 | -1,184.9 |
| base | obr_pmd_nov2025:24158:73455589333cbd4a (row 24158) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -127.3 | — | — |
| head | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 (row 12717) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 490.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:24152:3f0b4da150453149 (row 24152) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,693.9 | -1,197.6 | -1,184.9 |
| head | obr_pmd_nov2025:24158:73455589333cbd4a (row 24158) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -127.3 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028.json` (sha256 `edc4de8e4678bfe397f1b6cc41104172fd9ad2ad41dd2ca22af943b444a06375`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028.json` (sha256 `2d767056966820e461d4b87d07a9a5f5a12df8350b767bb1daf5d1e4feb2d6da`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
