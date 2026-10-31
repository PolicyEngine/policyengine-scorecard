# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11686:9ceb140875d859b8 | 4,193.4 | 3,024.5 | -1,168.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11692:6df82bc59b0bf861 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11698:85efd8e5130ecc7d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22833:50327aa26d0c6316 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22839:e2b393c5a46deff3 | — | — | — | — | — |
| measure_year | total | 4,193.4 | 3,024.5 | -1,168.8 | numerical | move_above_threshold |
| head | capital_gains_tax | 4,193.4 | 3,024.5 | -1,168.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11686:9ceb140875d859b8 (row 11686) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 755.7 | 4,193.4 | 3,024.5 |
| base | obr_pmd_nov2025:11692:6df82bc59b0bf861 (row 11692) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -54.3 | — | — |
| base | obr_pmd_nov2025:11698:85efd8e5130ecc7d (row 11698) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,388.9 | — | — |
| base | obr_pmd_nov2025:22833:50327aa26d0c6316 (row 22833) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 81.9 | — | — |
| base | obr_pmd_nov2025:22839:e2b393c5a46deff3 (row 22839) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 6.5 | — | — |
| head | obr_pmd_nov2025:11686:9ceb140875d859b8 (row 11686) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 755.7 | 4,193.4 | 3,024.5 |
| head | obr_pmd_nov2025:11692:6df82bc59b0bf861 (row 11692) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -54.3 | — | — |
| head | obr_pmd_nov2025:11698:85efd8e5130ecc7d (row 11698) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,388.9 | — | — |
| head | obr_pmd_nov2025:22833:50327aa26d0c6316 (row 22833) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 81.9 | — | — |
| head | obr_pmd_nov2025:22839:e2b393c5a46deff3 (row 22839) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 6.5 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028.json` (sha256 `b49866ecb51144bcf7ceef1b853c16595b6e74e9bafac2c1ee9f435e848a45c0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028.json` (sha256 `0a8c6d326ff8d1945530be7089be4f4d24026d68383709178dea57dbf13595d6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
