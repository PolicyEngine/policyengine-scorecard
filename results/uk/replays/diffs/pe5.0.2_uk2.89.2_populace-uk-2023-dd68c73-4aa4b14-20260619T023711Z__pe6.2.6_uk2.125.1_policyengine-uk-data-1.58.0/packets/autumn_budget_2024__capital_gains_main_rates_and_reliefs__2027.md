# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11685:440412b0fb8c6e2d | 4,952.4 | 2,502.0 | -2,450.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11691:2bcdf86f45b6b126 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11697:b41b55d5b8cbd0c7 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22832:9f4c74a62730d0a2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22838:b0c109139b2c7337 | — | — | — | — | — |
| measure_year | total | 4,952.4 | 2,502.0 | -2,450.4 | numerical, construction | move_above_threshold; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 4,952.4 | 2,502.0 | -2,450.4 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11685:440412b0fb8c6e2d (row 11685) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -75.8 | 4,952.4 | 2,502.0 |
| obr_pmd_nov2025:11691:2bcdf86f45b6b126 (row 11691) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | -51.4 | — | — |
| obr_pmd_nov2025:11697:b41b55d5b8cbd0c7 (row 11697) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,388.5 | — | — |
| obr_pmd_nov2025:22832:9f4c74a62730d0a2 (row 22832) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 82.1 | — | — |
| obr_pmd_nov2025:22838:b0c109139b2c7337 (row 22838) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 6.7 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027.json` (sha256 `3ba224e1859ebadf4c5793116540f67845b104d7fa899c3eb378d99e5f54a738`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027.json` (sha256 `798f95d6a41278ddf44029b22caeb7d677385f787bfb74d577f92ad89d076020`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
