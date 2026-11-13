# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22853:636080d8aa33dd8e | 1,576.5 | 1,628.6 | 52.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22859:a286d64db3a4de9d | — | — | — | — | — |
| measure_year | total | 1,576.5 | 1,628.6 | 52.1 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 1,576.5 | 1,628.6 | 52.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22853:636080d8aa33dd8e (row 22853) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 1,324.0 | 1,576.5 | 1,628.6 |
| base | obr_pmd_nov2025:22859:a286d64db3a4de9d (row 22859) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 126.0 | — | — |
| head | obr_pmd_nov2025:22853:636080d8aa33dd8e (row 22853) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 1,324.0 | 1,576.5 | 1,628.6 |
| head | obr_pmd_nov2025:22859:a286d64db3a4de9d (row 22859) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 126.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024.json` (sha256 `ade8525ae2923a97c3a95be057ab1da78db7c9ded6fb5369cbd7d6844071acab`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024.json` (sha256 `121c2b074b2f05c32b2068adf3dee3df11db47f7092927eea92f0e0e9e77afbc`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
