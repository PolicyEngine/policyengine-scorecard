# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11684:0d39628e9b763f67 | 4,793.6 | 2,414.6 | -2,379.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11690:cfacef00089fe7d2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11696:84f6e0e5fe5ec657 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22831:ab1c8743daadde1c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22837:75821b59c0b191da | — | — | — | — | — |
| measure_year | total | 4,793.6 | 2,414.6 | -2,379.0 | numerical, construction | move_above_threshold; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 4,793.6 | 2,414.6 | -2,379.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11684:0d39628e9b763f67 (row 11684) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 95.8 | 4,793.6 | 2,414.6 |
| obr_pmd_nov2025:11690:cfacef00089fe7d2 (row 11690) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | -65.7 | — | — |
| obr_pmd_nov2025:11696:84f6e0e5fe5ec657 (row 11696) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 1,262.3 | — | — |
| obr_pmd_nov2025:22831:ab1c8743daadde1c (row 22831) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 73.9 | — | — |
| obr_pmd_nov2025:22837:75821b59c0b191da (row 22837) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 5.8 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026.json` (sha256 `83898bfb4e09e3a135aa520dfd87a2b9f196c51a98c92e7f955f98db141d7e8d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026.json` (sha256 `10b4527f7c98edc27b904831d24a4c21a7a50cac505d667f0dd8f2a5318d96f2`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
