# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22857:92bf18d3bd843235 | 417.6 | 217.9 | -199.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22863:06a9e56d1d0f70ad | — | — | — | — | — |
| measure_year | total | 417.6 | 217.9 | -199.7 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 417.6 | 217.9 | -199.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22857:92bf18d3bd843235 (row 22857) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 1,459.0 | 417.6 | 217.9 |
| base | obr_pmd_nov2025:22863:06a9e56d1d0f70ad (row 22863) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 145.0 | — | — |
| head | obr_pmd_nov2025:22857:92bf18d3bd843235 (row 22857) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 1,459.0 | 417.6 | 217.9 |
| head | obr_pmd_nov2025:22863:06a9e56d1d0f70ad (row 22863) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 145.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028.json` (sha256 `55fcf11ef2837e1cc314711718afe2f3f39aae016679e49e96fc20810c7df7e4`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028.json` (sha256 `2e678c2e4b104657161f55ee953855d381a55f7f6198b8c108335113972f17da`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
