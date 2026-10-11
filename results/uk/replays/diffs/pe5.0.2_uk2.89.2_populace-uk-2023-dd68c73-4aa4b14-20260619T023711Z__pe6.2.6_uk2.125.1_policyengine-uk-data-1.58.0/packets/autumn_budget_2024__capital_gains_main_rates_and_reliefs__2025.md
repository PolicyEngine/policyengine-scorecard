# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11683:b9096ecd110093bf | 4,655.3 | 2,337.8 | -2,317.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11689:8192b33705abc153 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11695:6d29375672cd45e7 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22830:1b3ca3ad7932d614 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22836:46b312b678d3c12e | — | — | — | — | — |
| measure_year | total | 4,655.3 | 2,337.8 | -2,317.5 | numerical, construction | move_above_threshold; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 4,655.3 | 2,337.8 | -2,317.5 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11683:b9096ecd110093bf (row 11683) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 1,005.0 | 4,655.3 | 2,337.8 |
| obr_pmd_nov2025:11689:8192b33705abc153 (row 11689) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | -40.9 | — | — |
| obr_pmd_nov2025:11695:6d29375672cd45e7 (row 11695) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 448.7 | — | — |
| obr_pmd_nov2025:22830:1b3ca3ad7932d614 (row 22830) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 25.6 | — | — |
| obr_pmd_nov2025:22836:46b312b678d3c12e (row 22836) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 1.4 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025.json` (sha256 `f8dcfdd9c3c8032dfe54a1451a0598d73df2065370401e74a60873c16032cb8f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025.json` (sha256 `8316a941248c156b9b971b9ee86298b354a2d84241a625400da378a94d77b6ba`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
