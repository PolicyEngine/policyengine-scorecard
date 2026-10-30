# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22858:6050e74df71edc1c | 228.8 | 407.9 | 179.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22864:4349e70268452209 | — | — | — | — | — |
| measure_year | total | 228.8 | 407.9 | 179.1 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 228.8 | 407.9 | 179.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22858:6050e74df71edc1c (row 22858) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 1,501.0 | 228.8 | 407.9 |
| base | obr_pmd_nov2025:22864:4349e70268452209 (row 22864) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 152.0 | — | — |
| head | obr_pmd_nov2025:22858:6050e74df71edc1c (row 22858) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 1,501.0 | 228.8 | 407.9 |
| head | obr_pmd_nov2025:22864:4349e70268452209 (row 22864) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 152.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029.json` (sha256 `2218497ae40700866633b825c6f8e750191678ac829093d748a7f2ca244e9f4d`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029.json` (sha256 `8a5b883dbdc0d4682725c4cc5fb71e25d07fc25c67a8f6e8e218c0312c5d1d27`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
