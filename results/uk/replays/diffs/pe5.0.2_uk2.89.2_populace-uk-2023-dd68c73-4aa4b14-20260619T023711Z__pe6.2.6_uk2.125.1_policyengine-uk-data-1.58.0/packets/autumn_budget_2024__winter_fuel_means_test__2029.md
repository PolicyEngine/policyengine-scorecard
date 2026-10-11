# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22858:6050e74df71edc1c | 453.2 | 241.1 | -212.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22864:4349e70268452209 | — | — | — | — | — |
| measure_year | total | 453.2 | 241.1 | -212.1 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 453.2 | 241.1 | -212.1 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:22858:6050e74df71edc1c (row 22858) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 1,501.0 | 453.2 | 241.1 |
| obr_pmd_nov2025:22864:4349e70268452209 (row 22864) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 152.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029.json` (sha256 `8e0471c0cb60e12aed60caec4a2bf2c83af5730a955454c156becb4d2e30ab34`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029.json` (sha256 `ed41d9a544d6a8907133e375e8dac09b30a109b3b25d3dd0d239de1ec1d22540`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
