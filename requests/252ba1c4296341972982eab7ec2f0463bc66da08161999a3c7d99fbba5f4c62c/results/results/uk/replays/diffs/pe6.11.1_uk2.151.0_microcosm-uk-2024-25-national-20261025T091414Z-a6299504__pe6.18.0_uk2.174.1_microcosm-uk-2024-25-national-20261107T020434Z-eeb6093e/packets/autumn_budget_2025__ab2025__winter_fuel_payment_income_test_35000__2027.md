# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12716:668d8da17b50bcad | 0.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24151:5d9b3e6bbec76d40 | -1,157.8 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24157:1488946a6937ebc5 | — | — | — | — | — |
| measure_year | total | -1,157.8 | 0.0 | 1,157.8 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,157.8 | -0.0 | 1,157.8 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12716:668d8da17b50bcad (row 12716) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 891.9 | 0.0 | — |
| base | obr_pmd_nov2025:24151:5d9b3e6bbec76d40 (row 24151) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,676.3 | -1,157.8 | — |
| base | obr_pmd_nov2025:24157:1488946a6937ebc5 (row 24157) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -125.9 | — | — |
| head | obr_pmd_nov2025:12716:668d8da17b50bcad (row 12716) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 891.9 | 0.0 | — |
| head | obr_pmd_nov2025:24151:5d9b3e6bbec76d40 (row 24151) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,676.3 | -1,157.8 | — |
| head | obr_pmd_nov2025:24157:1488946a6937ebc5 (row 24157) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -125.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027.json` (sha256 `ee0d9fe538788b3f3856353436da122004ae72819ef1dd88432d6ec5b5720448`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027.json` (sha256 `8c1c0241c36c9864653d53ad9d40030d39f00cec99992dd81a4ccf3e02f81094`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
