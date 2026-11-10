# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12715:2f68d12cab62adaa | 0.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24150:3a557c09d1d519f6 | -1,178.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:24156:4971f6103c685e64 | — | — | — | — | — |
| measure_year | total | -1,178.0 | 0.0 | 1,178.0 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | winter_fuel_allowance | -1,178.0 | -0.0 | 1,178.0 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12715:2f68d12cab62adaa (row 12715) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 408.5 | 0.0 | — |
| base | obr_pmd_nov2025:24150:3a557c09d1d519f6 (row 24150) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,672.2 | -1,178.0 | — |
| base | obr_pmd_nov2025:24156:4971f6103c685e64 (row 24156) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -125.1 | — | — |
| head | obr_pmd_nov2025:12715:2f68d12cab62adaa (row 12715) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 408.5 | 0.0 | — |
| head | obr_pmd_nov2025:24150:3a557c09d1d519f6 (row 24150) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,672.2 | -1,178.0 | — |
| head | obr_pmd_nov2025:24156:4971f6103c685e64 (row 24156) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -125.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2026.json` (sha256 `e0e7137e821923e3cc41cb8bb9349eb09a243bfc5c27282e74ef5b29ab435b72`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2026.json` (sha256 `daa1553c8e118b933ae9d4ff786caf8a4863db2a3d1bf9c430fbbfbdc71410c0`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
