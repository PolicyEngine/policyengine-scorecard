# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22855:dbc5baf2a54734dc | 367.9 | 184.7 | -183.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22861:0f81af8bde9e95a0 | — | — | — | — | — |
| measure_year | total | 367.9 | 184.7 | -183.2 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 367.9 | 184.7 | -183.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22855:dbc5baf2a54734dc (row 22855) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 1,420.0 | 367.9 | 184.7 |
| base | obr_pmd_nov2025:22861:0f81af8bde9e95a0 (row 22861) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 136.0 | — | — |
| head | obr_pmd_nov2025:22855:dbc5baf2a54734dc (row 22855) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 1,420.0 | 367.9 | 184.7 |
| head | obr_pmd_nov2025:22861:0f81af8bde9e95a0 (row 22861) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 136.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026.json` (sha256 `d922c443a06b28350c40a8835f34dd5f8e0884d030da1eed8b26d875c781a680`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026.json` (sha256 `5edee34ea8c3dc9e5bb3402daeea66adc1b9fc117f57e21f9d5cbc56d11ddb59`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
