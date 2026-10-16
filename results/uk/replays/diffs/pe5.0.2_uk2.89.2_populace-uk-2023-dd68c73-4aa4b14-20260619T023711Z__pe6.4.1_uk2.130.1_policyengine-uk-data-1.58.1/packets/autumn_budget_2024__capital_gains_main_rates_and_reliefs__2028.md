# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11686:9ceb140875d859b8 | 5,113.0 | 2,572.4 | -2,540.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11692:6df82bc59b0bf861 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11698:85efd8e5130ecc7d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22833:50327aa26d0c6316 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22839:e2b393c5a46deff3 | — | — | — | — | — |
| measure_year | total | 5,113.0 | 2,572.4 | -2,540.6 | numerical, construction | move_above_threshold; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 5,113.0 | 2,572.4 | -2,540.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11686:9ceb140875d859b8 (row 11686) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 755.7 | 5,113.0 | 2,572.4 |
| base | obr_pmd_nov2025:11692:6df82bc59b0bf861 (row 11692) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -54.3 | — | — |
| base | obr_pmd_nov2025:11698:85efd8e5130ecc7d (row 11698) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,388.9 | — | — |
| base | obr_pmd_nov2025:22833:50327aa26d0c6316 (row 22833) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 81.9 | — | — |
| base | obr_pmd_nov2025:22839:e2b393c5a46deff3 (row 22839) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 6.5 | — | — |
| head | obr_pmd_nov2025:11686:9ceb140875d859b8 (row 11686) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 755.7 | 5,113.0 | 2,572.4 |
| head | obr_pmd_nov2025:11692:6df82bc59b0bf861 (row 11692) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -54.3 | — | — |
| head | obr_pmd_nov2025:11698:85efd8e5130ecc7d (row 11698) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,388.9 | — | — |
| head | obr_pmd_nov2025:22833:50327aa26d0c6316 (row 22833) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 81.9 | — | — |
| head | obr_pmd_nov2025:22839:e2b393c5a46deff3 (row 22839) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 6.5 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028.json` (sha256 `1ab5607bb181d66be698fce218e3846de4aede26c892880f21152e99a15ee187`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028.json` (sha256 `eba0a5e8b15ead96c5b1006d9eb387c9e07b64c805473f706a8d1e9c3ffc2ad2`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
