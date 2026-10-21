# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11685:440412b0fb8c6e2d | 2,484.7 | 3,572.2 | 1,087.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11691:2bcdf86f45b6b126 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11697:b41b55d5b8cbd0c7 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22832:9f4c74a62730d0a2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22838:b0c109139b2c7337 | — | — | — | — | — |
| measure_year | total | 2,484.7 | 3,572.2 | 1,087.5 | numerical | move_above_threshold |
| head | capital_gains_tax | 2,484.7 | 3,572.2 | 1,087.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11685:440412b0fb8c6e2d (row 11685) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -75.8 | 2,484.7 | 3,572.2 |
| base | obr_pmd_nov2025:11691:2bcdf86f45b6b126 (row 11691) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | -51.4 | — | — |
| base | obr_pmd_nov2025:11697:b41b55d5b8cbd0c7 (row 11697) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,388.5 | — | — |
| base | obr_pmd_nov2025:22832:9f4c74a62730d0a2 (row 22832) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 82.1 | — | — |
| base | obr_pmd_nov2025:22838:b0c109139b2c7337 (row 22838) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 6.7 | — | — |
| head | obr_pmd_nov2025:11685:440412b0fb8c6e2d (row 11685) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -75.8 | 2,484.7 | 3,572.2 |
| head | obr_pmd_nov2025:11691:2bcdf86f45b6b126 (row 11691) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | -51.4 | — | — |
| head | obr_pmd_nov2025:11697:b41b55d5b8cbd0c7 (row 11697) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,388.5 | — | — |
| head | obr_pmd_nov2025:22832:9f4c74a62730d0a2 (row 22832) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 82.1 | — | — |
| head | obr_pmd_nov2025:22838:b0c109139b2c7337 (row 22838) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 6.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027.json` (sha256 `b2fcd4a18ae65879d7a5ac229e81420ab42a81eacfee436bf2a61f0383194d81`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027.json` (sha256 `d3869fd3670970969cb8f36a7f38c5776be44968871896e1dfcc5016cb52322d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
