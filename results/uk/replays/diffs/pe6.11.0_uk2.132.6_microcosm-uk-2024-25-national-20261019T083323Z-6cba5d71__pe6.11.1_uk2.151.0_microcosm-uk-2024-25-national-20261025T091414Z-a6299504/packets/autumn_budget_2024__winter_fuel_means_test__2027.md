# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22856:c29981419df6c6f6 | 386.7 | 391.2 | 4.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22862:63e7eea1be5ed5df | — | — | — | — | — |
| measure_year | total | 386.7 | 391.2 | 4.5 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 386.7 | 391.2 | 4.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22856:c29981419df6c6f6 (row 22856) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,439.0 | 386.7 | 391.2 |
| base | obr_pmd_nov2025:22862:63e7eea1be5ed5df (row 22862) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 140.0 | — | — |
| head | obr_pmd_nov2025:22856:c29981419df6c6f6 (row 22856) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,439.0 | 386.7 | 391.2 |
| head | obr_pmd_nov2025:22862:63e7eea1be5ed5df (row 22862) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 140.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027.json` (sha256 `d57cefd4c17d2aa5025749f9f25cd236be26849509a461b5d85bc093638d93eb`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027.json` (sha256 `858b0024ea605aa2696a8cb5454606e1ac5e4163fa1bf7e01234bac106542087`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
