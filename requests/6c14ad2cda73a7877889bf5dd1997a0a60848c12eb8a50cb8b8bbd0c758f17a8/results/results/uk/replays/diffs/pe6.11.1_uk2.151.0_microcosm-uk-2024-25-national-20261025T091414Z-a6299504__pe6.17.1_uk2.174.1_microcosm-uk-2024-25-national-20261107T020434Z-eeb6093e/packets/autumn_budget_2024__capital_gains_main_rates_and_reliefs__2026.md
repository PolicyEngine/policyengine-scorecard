# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11684:0d39628e9b763f67 | 2,812.7 | 2,846.1 | 33.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11690:cfacef00089fe7d2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11696:84f6e0e5fe5ec657 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22831:ab1c8743daadde1c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22837:75821b59c0b191da | — | — | — | — | — |
| measure_year | total | 2,812.7 | 2,846.1 | 33.3 | numerical | move_above_threshold |
| head | capital_gains_tax | 2,812.7 | 2,846.1 | 33.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11684:0d39628e9b763f67 (row 11684) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 95.8 | 2,812.7 | 2,846.1 |
| base | obr_pmd_nov2025:11690:cfacef00089fe7d2 (row 11690) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | -65.7 | — | — |
| base | obr_pmd_nov2025:11696:84f6e0e5fe5ec657 (row 11696) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 1,262.3 | — | — |
| base | obr_pmd_nov2025:22831:ab1c8743daadde1c (row 22831) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 73.9 | — | — |
| base | obr_pmd_nov2025:22837:75821b59c0b191da (row 22837) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 5.8 | — | — |
| head | obr_pmd_nov2025:11684:0d39628e9b763f67 (row 11684) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 95.8 | 2,812.7 | 2,846.1 |
| head | obr_pmd_nov2025:11690:cfacef00089fe7d2 (row 11690) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | -65.7 | — | — |
| head | obr_pmd_nov2025:11696:84f6e0e5fe5ec657 (row 11696) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 1,262.3 | — | — |
| head | obr_pmd_nov2025:22831:ab1c8743daadde1c (row 22831) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 73.9 | — | — |
| head | obr_pmd_nov2025:22837:75821b59c0b191da (row 22837) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 5.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026.json` (sha256 `5609e60bb04012c871e42bd6212a3bd5882c59f2dcf3569aa5ad28fe17495734`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026.json` (sha256 `92512441601212471198659ac19b06b2d1b3398725957453a2eb124bb1c8376c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
