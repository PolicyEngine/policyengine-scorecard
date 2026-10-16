# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24152:3f0b4da150453149 | — | -1,197.6 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24158:73455589333cbd4a | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | -1,197.6 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12717:e1c2c1fcb5ce9548 (row 12717) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 490.7 | — | 0.0 |
| head | obr_pmd_nov2025:24152:3f0b4da150453149 (row 24152) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,693.9 | — | -1,197.6 |
| head | obr_pmd_nov2025:24158:73455589333cbd4a (row 24158) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -127.3 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028.json` (sha256 `c7c8910ee0d2272e06ab30bb8c024f6b65ec11c7a9c6a80b659156ac7e85cc4b`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
