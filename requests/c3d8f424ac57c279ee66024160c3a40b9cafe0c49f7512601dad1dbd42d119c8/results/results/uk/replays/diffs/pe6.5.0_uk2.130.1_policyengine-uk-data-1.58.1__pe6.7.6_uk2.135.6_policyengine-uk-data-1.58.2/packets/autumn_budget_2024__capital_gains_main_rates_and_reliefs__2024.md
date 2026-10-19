# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11682:73295721bdfdb9e8 | 956.3 | 726.8 | -229.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11688:dcd2e2e6301193f3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11694:ade1673d32f6604b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22829:48aea91ecc2734f1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22835:93eff38f9e206ebc | — | — | — | — | — |
| measure_year | total | 956.3 | 726.8 | -229.5 | numerical | move_above_threshold |
| head | capital_gains_tax | 956.3 | 726.8 | -229.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11682:73295721bdfdb9e8 (row 11682) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | 956.3 | 726.8 |
| base | obr_pmd_nov2025:11688:dcd2e2e6301193f3 (row 11688) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Stamp duty | 36.7 | — | — |
| base | obr_pmd_nov2025:11694:ade1673d32f6604b (row 11694) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 45.9 | — | — |
| base | obr_pmd_nov2025:22829:48aea91ecc2734f1 (row 22829) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 4.5 | — | — |
| base | obr_pmd_nov2025:22835:93eff38f9e206ebc (row 22835) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.9 | — | — |
| head | obr_pmd_nov2025:11682:73295721bdfdb9e8 (row 11682) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | 956.3 | 726.8 |
| head | obr_pmd_nov2025:11688:dcd2e2e6301193f3 (row 11688) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Stamp duty | 36.7 | — | — |
| head | obr_pmd_nov2025:11694:ade1673d32f6604b (row 11694) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 45.9 | — | — |
| head | obr_pmd_nov2025:22829:48aea91ecc2734f1 (row 22829) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 4.5 | — | — |
| head | obr_pmd_nov2025:22835:93eff38f9e206ebc (row 22835) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024.json` (sha256 `d1bb43b79baa0e9517665cebacf0f870b7db6bcbb6f2452661430591e562a6c4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024.json` (sha256 `c954456289c0a7a852fc52650ccd1d404787f63dc2148f1b2d1637ae429692bf`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.135.6_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
