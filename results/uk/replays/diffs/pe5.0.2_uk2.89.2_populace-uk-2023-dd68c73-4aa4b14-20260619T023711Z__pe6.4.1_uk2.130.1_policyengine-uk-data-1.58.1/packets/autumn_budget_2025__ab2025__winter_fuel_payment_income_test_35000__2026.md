# Investigation packet: autumn_budget_2025 / ab2025__winter_fuel_payment_income_test_35000 / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12715:2f68d12cab62adaa | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24150:3a557c09d1d519f6 | — | -1,297.1 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24156:4971f6103c685e64 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | -1,297.1 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12715:2f68d12cab62adaa (row 12715) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 408.5 | — | 0.0 |
| head | obr_pmd_nov2025:24150:3a557c09d1d519f6 (row 24150) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,672.2 | — | -1,297.1 |
| head | obr_pmd_nov2025:24156:4971f6103c685e64 (row 24156) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -125.1 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2026.json` (sha256 `e20389bad20537f4850eaf026905d1eecff058c6f63fa7898370d65b04611a45`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.maximum_taxable_income": {"2025-01-01.2030-12-31": 0}, "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {"2025-01-01.2030-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__winter_fuel_payment_income_test_35000 --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
