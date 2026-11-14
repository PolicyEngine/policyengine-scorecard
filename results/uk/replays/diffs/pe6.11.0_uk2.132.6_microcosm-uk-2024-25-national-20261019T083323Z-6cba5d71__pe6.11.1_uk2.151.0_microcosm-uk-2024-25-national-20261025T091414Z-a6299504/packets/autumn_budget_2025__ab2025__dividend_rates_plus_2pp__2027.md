# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12308:5c1e45be5eff2e8d | 1,120.4 | 1,070.0 | -50.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12314:745357cae61de123 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12320:1654d36a764609bd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12326:b1eebc6c379e8995 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23953:91469837ddf069e6 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23959:39d2734cb67f68a1 | — | — | — | — | — |
| measure_year | total | 1,120.4 | 1,070.0 | -50.4 | numerical | move_above_threshold |
| head | income_tax | 1,120.4 | 1,070.0 | -50.4 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12308:5c1e45be5eff2e8d (row 12308) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,030.7 | 1,120.4 | 1,070.0 |
| base | obr_pmd_nov2025:12314:745357cae61de123 (row 12314) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -182.6 | — | — |
| base | obr_pmd_nov2025:12320:1654d36a764609bd (row 12320) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 122.2 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12326:b1eebc6c379e8995 (row 12326) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 16.9 | — | — |
| base | obr_pmd_nov2025:23953:91469837ddf069e6 (row 23953) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.2 | — | — |
| base | obr_pmd_nov2025:23959:39d2734cb67f68a1 (row 23959) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:12308:5c1e45be5eff2e8d (row 12308) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,030.7 | 1,120.4 | 1,070.0 |
| head | obr_pmd_nov2025:12314:745357cae61de123 (row 12314) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -182.6 | — | — |
| head | obr_pmd_nov2025:12320:1654d36a764609bd (row 12320) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 122.2 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12326:b1eebc6c379e8995 (row 12326) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 16.9 | — | — |
| head | obr_pmd_nov2025:23953:91469837ddf069e6 (row 23953) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.2 | — | — |
| head | obr_pmd_nov2025:23959:39d2734cb67f68a1 (row 23959) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027.json` (sha256 `cef72e4e0d7e6cbd6b933cc3b6ad4ca26812a20f9d61befd2a32f4d69e070961`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027.json` (sha256 `2bdce9dac68e44b22eb80273848628e50a0bb5a41fc6e28b1c2355fb1e84fd6d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
