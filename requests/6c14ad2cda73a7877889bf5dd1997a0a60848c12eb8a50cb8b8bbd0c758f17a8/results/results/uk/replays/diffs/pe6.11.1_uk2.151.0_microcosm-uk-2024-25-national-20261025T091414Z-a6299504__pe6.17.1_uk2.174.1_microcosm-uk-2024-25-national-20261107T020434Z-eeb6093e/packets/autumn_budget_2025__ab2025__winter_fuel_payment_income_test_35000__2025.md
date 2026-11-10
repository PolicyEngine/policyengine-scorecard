# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12714:7759d518d7c6f285 | 0.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24149:cb9c6124ee5756b0 | -1,195.9 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24155:58c670cb9cae45ee | — | — | — | — | — |
| measure_year | total | -1,195.9 | 0.0 | 1,195.9 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,195.9 | -0.0 | 1,195.9 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12714:7759d518d7c6f285 (row 12714) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:24149:cb9c6124ee5756b0 (row 24149) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,661.9 | -1,195.9 | — |
| base | obr_pmd_nov2025:24155:58c670cb9cae45ee (row 24155) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -123.7 | — | — |
| head | obr_pmd_nov2025:12714:7759d518d7c6f285 (row 12714) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:24149:cb9c6124ee5756b0 (row 24149) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,661.9 | -1,195.9 | — |
| head | obr_pmd_nov2025:24155:58c670cb9cae45ee (row 24155) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -123.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025.json` (sha256 `8a1f72a4bb390bbad687b1362457d6490c8abb3bc84a9d542c1e6bd89eb92403`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025.json` (sha256 `90039272aab4b2fa8c2570219e4d403976509b714e874efcc16cb9f58b4b74df`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
