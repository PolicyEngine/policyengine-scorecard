# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.138.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22858:6050e74df71edc1c | 228.8 | 232.9 | 4.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22864:4349e70268452209 | — | — | — | — | — |
| measure_year | total | 228.8 | 232.9 | 4.1 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 228.8 | 232.9 | 4.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22858:6050e74df71edc1c (row 22858) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 1,501.0 | 228.8 | 232.9 |
| base | obr_pmd_nov2025:22864:4349e70268452209 (row 22864) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 152.0 | — | — |
| head | obr_pmd_nov2025:22858:6050e74df71edc1c (row 22858) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | 1,501.0 | 228.8 | 232.9 |
| head | obr_pmd_nov2025:22864:4349e70268452209 (row 22864) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 152.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029.json` (sha256 `cd5e27afec6cdf0bdf5d00e5ce9165a700a60030c06157e897e35dc0f9c6e114`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.138.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029.json` (sha256 `a6a085984b165494724e0f2a1eca2f22007515a2879fb527c5ddad4f090063e5`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.7.6_uk2.138.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.138.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
