# Investigation packet: autumn_budget_2024 / autumn_budget_2024__winter_fuel_means_test / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:22856:c29981419df6c6f6 | 397.3 | 216.2 | -181.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22862:63e7eea1be5ed5df | — | — | — | — | — |
| measure_year | total | 397.3 | 216.2 | -181.1 | numerical | move_above_threshold |
| head | winter_fuel_allowance | 397.3 | 216.2 | -181.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:22856:c29981419df6c6f6 (row 22856) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,439.0 | 397.3 | 216.2 |
| base | obr_pmd_nov2025:22862:63e7eea1be5ed5df (row 22862) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 140.0 | — | — |
| head | obr_pmd_nov2025:22856:c29981419df6c6f6 (row 22856) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,439.0 | 397.3 | 216.2 |
| head | obr_pmd_nov2025:22862:63e7eea1be5ed5df (row 22862) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 140.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027.json` (sha256 `01bc3223958f335ac75c7beb08f9ae727fc0d4476950633b1a5d0ae102037dc5`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027.json` (sha256 `8f7fe092a8c5be604b8e0ff49301549999eae8f0e4587aed1898131e3bc30bc9`), reversal_on_certified_world; baseline dict `{"gov.dwp.winter_fuel_payment.eligibility.require_benefits": {"2024-01-01.2035-12-31": false}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__winter_fuel_means_test --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
