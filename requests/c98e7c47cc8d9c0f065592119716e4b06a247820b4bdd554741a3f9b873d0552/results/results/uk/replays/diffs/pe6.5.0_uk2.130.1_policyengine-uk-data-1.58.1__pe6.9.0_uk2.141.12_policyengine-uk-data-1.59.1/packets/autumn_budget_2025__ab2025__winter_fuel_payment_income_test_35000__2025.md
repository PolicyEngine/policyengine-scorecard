# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12714:7759d518d7c6f285 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:24149:cb9c6124ee5756b0 | -1,314.0 | -1,327.8 | -13.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:24155:58c670cb9cae45ee | — | — | — | — | — |
| measure_year | total | -1,314.0 | -1,327.8 | -13.8 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,314.0 | -1,327.8 | -13.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12714:7759d518d7c6f285 (row 12714) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:24149:cb9c6124ee5756b0 (row 24149) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,661.9 | -1,314.0 | -1,327.8 |
| base | obr_pmd_nov2025:24155:58c670cb9cae45ee (row 24155) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -123.7 | — | — |
| head | obr_pmd_nov2025:12714:7759d518d7c6f285 (row 12714) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:24149:cb9c6124ee5756b0 (row 24149) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,661.9 | -1,314.0 | -1,327.8 |
| head | obr_pmd_nov2025:24155:58c670cb9cae45ee (row 24155) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -123.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025.json` (sha256 `9cc87153340d8f21cc0b1d453821c039885e36d16e5bcfc3de098f0e1d258b96`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025.json` (sha256 `95902ce4b592e3d09e22a318ff8423e5626a836a866a48158b9d959f0f49a041`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
