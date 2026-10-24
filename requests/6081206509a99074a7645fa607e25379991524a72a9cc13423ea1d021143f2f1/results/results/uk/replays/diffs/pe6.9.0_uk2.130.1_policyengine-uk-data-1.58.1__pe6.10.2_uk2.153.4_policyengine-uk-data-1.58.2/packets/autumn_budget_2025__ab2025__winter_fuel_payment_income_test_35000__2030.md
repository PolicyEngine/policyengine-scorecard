# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12719:670f8310e3289a5b | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:24154:67e883d6279cdc10 | -1,171.4 | -1,157.4 | 14.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:24160:0419e9d97e55970a | — | — | — | — | — |
| measure_year | total | -1,171.4 | -1,157.4 | 14.0 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,171.4 | -1,157.4 | 14.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12719:670f8310e3289a5b (row 12719) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 561.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:24154:67e883d6279cdc10 (row 24154) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -1,753.8 | -1,171.4 | -1,157.4 |
| base | obr_pmd_nov2025:24160:0419e9d97e55970a (row 24160) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -132.0 | — | — |
| head | obr_pmd_nov2025:12719:670f8310e3289a5b (row 12719) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 561.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:24154:67e883d6279cdc10 (row 24154) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -1,753.8 | -1,171.4 | -1,157.4 |
| head | obr_pmd_nov2025:24160:0419e9d97e55970a (row 24160) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -132.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030.json` (sha256 `46c72cc4a70892baf9e55fff64819c01d986123be30c954053cb792dcfed67b4`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030.json` (sha256 `6c0fdf7e9dfd62ca3f79ea36a006f572b888295ea8c020ac6e560b754bf3f501`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
