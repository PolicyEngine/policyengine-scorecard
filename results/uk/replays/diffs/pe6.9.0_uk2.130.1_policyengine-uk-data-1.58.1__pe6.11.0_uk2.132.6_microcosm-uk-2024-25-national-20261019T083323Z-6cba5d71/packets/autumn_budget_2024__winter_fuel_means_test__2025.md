# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22854:edbde987f66af165 | 175.5 | 389.5 | 214.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22860:4f83faabe04eeb65 | — | — | — | — | — |
| measure_year | total | 175.5 | 389.5 | 214.1 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 175.5 | 389.5 | 214.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22854:edbde987f66af165 (row 22854) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 1,378.0 | 175.5 | 389.5 |
| base | obr_pmd_nov2025:22860:4f83faabe04eeb65 (row 22860) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 132.0 | — | — |
| head | obr_pmd_nov2025:22854:edbde987f66af165 (row 22854) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 1,378.0 | 175.5 | 389.5 |
| head | obr_pmd_nov2025:22860:4f83faabe04eeb65 (row 22860) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 132.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025.json` (sha256 `85a1a58845837e4ebdca5799a81f3782319702fcde8fd470119553b274c39629`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025.json` (sha256 `1460df861eb7e8c56a9790a7613269bf543e6ec44ceed126bb3e3a9da7721f1a`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
