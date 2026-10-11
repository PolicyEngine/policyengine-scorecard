# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical, construction
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11686:9ceb140875d859b8 | 5,113.0 | 2,590.3 | -2,522.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11692:6df82bc59b0bf861 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11698:85efd8e5130ecc7d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22833:50327aa26d0c6316 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22839:e2b393c5a46deff3 | — | — | — | — | — |
| measure_year | total | 5,113.0 | 2,590.3 | -2,522.6 | numerical, construction | move_above_threshold; premise_check_changed (annual_value_matches_30_april_sample) |
| head | capital_gains_tax | 5,113.0 | 2,590.3 | -2,522.6 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11686:9ceb140875d859b8 (row 11686) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 755.7 | 5,113.0 | 2,590.3 |
| obr_pmd_nov2025:11692:6df82bc59b0bf861 (row 11692) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -54.3 | — | — |
| obr_pmd_nov2025:11698:85efd8e5130ecc7d (row 11698) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,388.9 | — | — |
| obr_pmd_nov2025:22833:50327aa26d0c6316 (row 22833) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 81.9 | — | — |
| obr_pmd_nov2025:22839:e2b393c5a46deff3 (row 22839) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 6.5 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028.json` (sha256 `1ab5607bb181d66be698fce218e3846de4aede26c892880f21152e99a15ee187`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028.json` (sha256 `74d5ae3224affd8979aaf4b9d66afb2f260d533b181b8f090a20e661a4ff003c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-10-30.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-10-30.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-10-30.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
