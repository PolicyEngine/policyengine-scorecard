# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22855:dbc5baf2a54734dc | 184.7 | 190.2 | 5.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22861:0f81af8bde9e95a0 | — | — | — | — | — |
| measure_year | total | 184.7 | 190.2 | 5.5 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 184.7 | 190.2 | 5.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22855:dbc5baf2a54734dc (row 22855) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 1,420.0 | 184.7 | 190.2 |
| base | obr_pmd_nov2025:22861:0f81af8bde9e95a0 (row 22861) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 136.0 | — | — |
| head | obr_pmd_nov2025:22855:dbc5baf2a54734dc (row 22855) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 1,420.0 | 184.7 | 190.2 |
| head | obr_pmd_nov2025:22861:0f81af8bde9e95a0 (row 22861) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 136.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026.json` (sha256 `407c4a10aea48bfe272f478cf9feae279ee59c8d7c5572e70e2075d074d439d9`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026.json` (sha256 `607ccad945eaab05b340ea996e4996e2f85d7e1d341ddacf3b23a59f857a3ee0`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
