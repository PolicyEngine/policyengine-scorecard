# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22854:edbde987f66af165 | 399.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:22860:4f83faabe04eeb65 | — | — | — | — | — |
| measure_year | total | 399.0 | 0.0 | -399.0 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | winter_fuel_allowance | 399.0 | -0.0 | -399.0 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22854:edbde987f66af165 (row 22854) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 1,378.0 | 399.0 | — |
| base | obr_pmd_nov2025:22860:4f83faabe04eeb65 (row 22860) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 132.0 | — | — |
| head | obr_pmd_nov2025:22854:edbde987f66af165 (row 22854) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 1,378.0 | 399.0 | — |
| head | obr_pmd_nov2025:22860:4f83faabe04eeb65 (row 22860) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 132.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025.json` (sha256 `fed32c39e4da33db5185ff19db7dee1488c039771cd9ed96842cdf17286b8153`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025.json` (sha256 `927be3752ca441e0ca05dfce3b2fd46ae2a632d962762df3c902cbb5867f6774`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
