# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11687:f738e039412d9872 | 5,273.8 | 2,660.3 | -2,613.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11693:fce3f1c54885e725 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11699:6ff71275479301e4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22834:74c3bd563eca97a5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22840:1197e330a3c46ef4 | — | — | — | — | — |
| measure_year | total | 5,273.8 | 2,660.3 | -2,613.5 | numerical, construction | move_above_threshold; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 5,273.8 | 2,660.3 | -2,613.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11687:f738e039412d9872 (row 11687) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 985.9 | 5,273.8 | 2,660.3 |
| base | obr_pmd_nov2025:11693:fce3f1c54885e725 (row 11693) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -58.7 | — | — |
| base | obr_pmd_nov2025:11699:6ff71275479301e4 (row 11699) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,470.6 | — | — |
| base | obr_pmd_nov2025:22834:74c3bd563eca97a5 (row 22834) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 86.7 | — | — |
| base | obr_pmd_nov2025:22840:1197e330a3c46ef4 (row 22840) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 6.8 | — | — |
| head | obr_pmd_nov2025:11687:f738e039412d9872 (row 11687) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 985.9 | 5,273.8 | 2,660.3 |
| head | obr_pmd_nov2025:11693:fce3f1c54885e725 (row 11693) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -58.7 | — | — |
| head | obr_pmd_nov2025:11699:6ff71275479301e4 (row 11699) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,470.6 | — | — |
| head | obr_pmd_nov2025:22834:74c3bd563eca97a5 (row 22834) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 86.7 | — | — |
| head | obr_pmd_nov2025:22840:1197e330a3c46ef4 (row 22840) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 6.8 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029.json` (sha256 `52c401fd1a83f6997d6573525214d4eb4a8987a144a8e063dc0e68db79216f49`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029.json` (sha256 `91cf6a52fc6dabc3a60f63e90a46c31606aeadd72303143a5c2d7aa024bb8518`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
