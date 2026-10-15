# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, structural, coverage, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11682:73295721bdfdb9e8 | — | 575.0 | — | coverage | counterpart_on_head_only |
| source_row | obr_pmd_nov2025:11688:dcd2e2e6301193f3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11694:ade1673d32f6604b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22829:48aea91ecc2734f1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22835:93eff38f9e206ebc | — | — | — | — | — |
| measure_year | total | 0.0 | 575.0 | 575.0 | numerical, structural, construction | move_above_threshold; zero_crossing; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 0.0 | 575.0 | 575.0 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11682:73295721bdfdb9e8 (row 11682) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | 575.0 |
| base | obr_pmd_nov2025:11688:dcd2e2e6301193f3 (row 11688) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Stamp duty | 36.7 | — | — |
| base | obr_pmd_nov2025:11694:ade1673d32f6604b (row 11694) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 45.9 | — | — |
| base | obr_pmd_nov2025:22829:48aea91ecc2734f1 (row 22829) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 4.5 | — | — |
| base | obr_pmd_nov2025:22835:93eff38f9e206ebc (row 22835) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.9 | — | — |
| head | obr_pmd_nov2025:11682:73295721bdfdb9e8 (row 11682) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | 575.0 |
| head | obr_pmd_nov2025:11688:dcd2e2e6301193f3 (row 11688) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Stamp duty | 36.7 | — | — |
| head | obr_pmd_nov2025:11694:ade1673d32f6604b (row 11694) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 45.9 | — | — |
| head | obr_pmd_nov2025:22829:48aea91ecc2734f1 (row 22829) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 4.5 | — | — |
| head | obr_pmd_nov2025:22835:93eff38f9e206ebc (row 22835) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.9 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024.json` (sha256 `f5255a6f3c63b7a373a9665927152ba898439ee7ad0a1392ff675d8ef5c7b881`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024.json` (sha256 `1fffeb4ebcafe106ec62bbb6937bc395a5f66beb1adb4f3d744f478cf3bed330`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
