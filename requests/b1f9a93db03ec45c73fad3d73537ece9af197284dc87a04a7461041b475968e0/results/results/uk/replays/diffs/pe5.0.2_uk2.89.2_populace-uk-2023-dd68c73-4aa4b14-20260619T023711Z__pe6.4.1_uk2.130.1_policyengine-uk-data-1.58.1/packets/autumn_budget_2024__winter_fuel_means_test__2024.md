# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22853:636080d8aa33dd8e | 1,713.9 | 1,477.7 | -236.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22859:a286d64db3a4de9d | — | — | — | — | — |
| measure_year | total | 1,713.9 | 1,477.7 | -236.2 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 1,713.9 | 1,477.7 | -236.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22853:636080d8aa33dd8e (row 22853) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 1,324.0 | 1,713.9 | 1,477.7 |
| base | obr_pmd_nov2025:22859:a286d64db3a4de9d (row 22859) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 126.0 | — | — |
| head | obr_pmd_nov2025:22853:636080d8aa33dd8e (row 22853) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 1,324.0 | 1,713.9 | 1,477.7 |
| head | obr_pmd_nov2025:22859:a286d64db3a4de9d (row 22859) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 126.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024.json` (sha256 `d37bef86a0f713898b680177199dff5edbe8145b24f36cd8ce711729f64fe0a4`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024.json` (sha256 `ece3c42305edc8d1d93deb0072cca6886c6f353d701979f2833290adda66ae2e`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
