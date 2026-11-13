# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22855:dbc5baf2a54734dc | 398.8 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:22861:0f81af8bde9e95a0 | — | — | — | — | — |
| measure_year | total | 398.8 | 0.0 | -398.8 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | winter_fuel_allowance | 398.8 | -0.0 | -398.8 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22855:dbc5baf2a54734dc (row 22855) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 1,420.0 | 398.8 | — |
| base | obr_pmd_nov2025:22861:0f81af8bde9e95a0 (row 22861) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 136.0 | — | — |
| head | obr_pmd_nov2025:22855:dbc5baf2a54734dc (row 22855) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 1,420.0 | 398.8 | — |
| head | obr_pmd_nov2025:22861:0f81af8bde9e95a0 (row 22861) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 136.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026.json` (sha256 `ab43fb15da80bb3f7c4b1105375394ea71d888447560ca2da5f34cfd77d1064f`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026.json` (sha256 `aaba1cfd51b65cf7a0385b6d9990135dddd04083a5a1cd03e71b30268bf39bbb`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
