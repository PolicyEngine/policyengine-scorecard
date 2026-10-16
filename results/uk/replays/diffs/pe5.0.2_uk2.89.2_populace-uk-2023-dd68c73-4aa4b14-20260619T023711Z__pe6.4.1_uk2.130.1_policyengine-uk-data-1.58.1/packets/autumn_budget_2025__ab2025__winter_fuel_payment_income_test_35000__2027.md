# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12716:668d8da17b50bcad | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24151:5d9b3e6bbec76d40 | — | -1,210.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24157:1488946a6937ebc5 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | -1,210.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12716:668d8da17b50bcad (row 12716) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 891.9 | — | 0.0 |
| head | obr_pmd_nov2025:24151:5d9b3e6bbec76d40 (row 24151) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,676.3 | — | -1,210.0 |
| head | obr_pmd_nov2025:24157:1488946a6937ebc5 (row 24157) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -125.9 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027.json` (sha256 `3ce236c62bd9d82428c9dc9e839ff6c6b1049c91293628125f01fba5f23dc586`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
