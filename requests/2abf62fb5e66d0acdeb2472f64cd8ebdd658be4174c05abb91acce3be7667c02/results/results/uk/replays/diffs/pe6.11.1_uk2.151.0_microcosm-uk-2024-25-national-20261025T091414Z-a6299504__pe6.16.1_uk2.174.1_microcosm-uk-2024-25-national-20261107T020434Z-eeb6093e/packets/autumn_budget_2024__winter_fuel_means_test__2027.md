# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22856:c29981419df6c6f6 | 391.2 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:22862:63e7eea1be5ed5df | — | — | — | — | — |
| measure_year | total | 391.2 | 0.0 | -391.2 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | winter_fuel_allowance | 391.2 | -0.0 | -391.2 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22856:c29981419df6c6f6 (row 22856) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,439.0 | 391.2 | — |
| base | obr_pmd_nov2025:22862:63e7eea1be5ed5df (row 22862) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 140.0 | — | — |
| head | obr_pmd_nov2025:22856:c29981419df6c6f6 (row 22856) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,439.0 | 391.2 | — |
| head | obr_pmd_nov2025:22862:63e7eea1be5ed5df (row 22862) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 140.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027.json` (sha256 `858b0024ea605aa2696a8cb5454606e1ac5e4163fa1bf7e01234bac106542087`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027.json` (sha256 `33a97c9e4c15a41c0f1518e8afebefee473cc710cb8c8c28ece61ce0a4dafa01`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
