# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11683:b9096ecd110093bf | 2,321.6 | 1,745.2 | -576.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11689:8192b33705abc153 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11695:6d29375672cd45e7 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22830:1b3ca3ad7932d614 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22836:46b312b678d3c12e | — | — | — | — | — |
| measure_year | total | 2,321.6 | 1,745.2 | -576.4 | numerical | move_above_threshold |
| head | capital_gains_tax | 2,321.6 | 1,745.2 | -576.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11683:b9096ecd110093bf (row 11683) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 1,005.0 | 2,321.6 | 1,745.2 |
| base | obr_pmd_nov2025:11689:8192b33705abc153 (row 11689) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | -40.9 | — | — |
| base | obr_pmd_nov2025:11695:6d29375672cd45e7 (row 11695) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 448.7 | — | — |
| base | obr_pmd_nov2025:22830:1b3ca3ad7932d614 (row 22830) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 25.6 | — | — |
| base | obr_pmd_nov2025:22836:46b312b678d3c12e (row 22836) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 1.4 | — | — |
| head | obr_pmd_nov2025:11683:b9096ecd110093bf (row 11683) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 1,005.0 | 2,321.6 | 1,745.2 |
| head | obr_pmd_nov2025:11689:8192b33705abc153 (row 11689) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | -40.9 | — | — |
| head | obr_pmd_nov2025:11695:6d29375672cd45e7 (row 11695) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 448.7 | — | — |
| head | obr_pmd_nov2025:22830:1b3ca3ad7932d614 (row 22830) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 25.6 | — | — |
| head | obr_pmd_nov2025:22836:46b312b678d3c12e (row 22836) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 1.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025.json` (sha256 `555a99a755e55b48db107cf5e6432f43e2e12f7608e5bb8a279e0b69abc38740`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025.json` (sha256 `e0da2de3760a846dd92e686cc3c7526c95f48ef66fc0a7728e7b094614f490fb`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
