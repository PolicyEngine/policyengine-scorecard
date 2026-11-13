# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22857:92bf18d3bd843235 | 398.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:22863:06a9e56d1d0f70ad | — | — | — | — | — |
| measure_year | total | 398.0 | 0.0 | -398.0 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | winter_fuel_allowance | 398.0 | -0.0 | -398.0 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22857:92bf18d3bd843235 (row 22857) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 1,459.0 | 398.0 | — |
| base | obr_pmd_nov2025:22863:06a9e56d1d0f70ad (row 22863) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 145.0 | — | — |
| head | obr_pmd_nov2025:22857:92bf18d3bd843235 (row 22857) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 1,459.0 | 398.0 | — |
| head | obr_pmd_nov2025:22863:06a9e56d1d0f70ad (row 22863) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 145.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028.json` (sha256 `86e1fdebd148482e04b7477e0641c7d0945344bbb0f8e324971e84e66fb6fa79`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028.json` (sha256 `c731ef983a19fc2bf3ba2cca5f0be667fdff4982ae1b995a2d20b9f7acf8d7d2`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
