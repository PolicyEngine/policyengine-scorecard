# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12311:9143a3313d158e51 | 1,229.9 | 1,172.4 | -57.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12317:4cf949c78d705d18 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12323:e028d55f29a62741 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12329:964a3194129b2c01 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23956:8842f3881bb217c0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23962:1d523435af45cc88 | — | — | — | — | — |
| measure_year | total | 1,229.9 | 1,172.4 | -57.4 | numerical | move_above_threshold |
| head | income_tax | 1,229.9 | 1,172.4 | -57.4 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12311:9143a3313d158e51 (row 12311) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 1,457.9 | 1,229.9 | 1,172.4 |
| base | obr_pmd_nov2025:12317:4cf949c78d705d18 (row 12317) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -387.3 | — | — |
| base | obr_pmd_nov2025:12323:e028d55f29a62741 (row 12323) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 312.1 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12329:964a3194129b2c01 (row 12329) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | 6.7 | — | — |
| base | obr_pmd_nov2025:23956:8842f3881bb217c0 (row 23956) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.1 | — | — |
| base | obr_pmd_nov2025:23962:1d523435af45cc88 (row 23962) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.7 | — | — |
| head | obr_pmd_nov2025:12311:9143a3313d158e51 (row 12311) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 1,457.9 | 1,229.9 | 1,172.4 |
| head | obr_pmd_nov2025:12317:4cf949c78d705d18 (row 12317) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -387.3 | — | — |
| head | obr_pmd_nov2025:12323:e028d55f29a62741 (row 12323) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 312.1 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12329:964a3194129b2c01 (row 12329) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | 6.7 | — | — |
| head | obr_pmd_nov2025:23956:8842f3881bb217c0 (row 23956) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:23962:1d523435af45cc88 (row 23962) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2030.json` (sha256 `bd6192cbefeaa811ad8da4482da10c412c2ea1ee51d14f2e9ecffc075746f4e3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2030.json` (sha256 `17e0a7e3cb53a6ee7b727304a472dbfb955dec5678cc1a4cd2b09ae59be460a4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
