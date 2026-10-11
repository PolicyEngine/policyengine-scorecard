# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22857:92bf18d3bd843235 | 417.6 | 226.9 | -190.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22863:06a9e56d1d0f70ad | — | — | — | — | — |
| measure_year | total | 417.6 | 226.9 | -190.7 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 417.6 | 226.9 | -190.7 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:22857:92bf18d3bd843235 (row 22857) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 1,459.0 | 417.6 | 226.9 |
| obr_pmd_nov2025:22863:06a9e56d1d0f70ad (row 22863) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 145.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028.json` (sha256 `55fcf11ef2837e1cc314711718afe2f3f39aae016679e49e96fc20810c7df7e4`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028.json` (sha256 `3da36dfebf68e4209af0b06a55a4688ccd81765e889405777ae95af09be71874`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__winter_fuel_means_test --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__winter_fuel_means_test --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
