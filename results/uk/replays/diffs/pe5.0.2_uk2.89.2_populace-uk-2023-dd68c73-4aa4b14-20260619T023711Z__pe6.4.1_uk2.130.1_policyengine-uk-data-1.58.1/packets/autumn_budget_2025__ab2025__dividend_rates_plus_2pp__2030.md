# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12311:9143a3313d158e51 | — | 1,034.8 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12317:4cf949c78d705d18 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12323:e028d55f29a62741 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12329:964a3194129b2c01 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23956:8842f3881bb217c0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23962:1d523435af45cc88 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 1,034.8 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12311:9143a3313d158e51 (row 12311) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 1,457.9 | — | 1,034.8 |
| head | obr_pmd_nov2025:12317:4cf949c78d705d18 (row 12317) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -387.3 | — | — |
| head | obr_pmd_nov2025:12323:e028d55f29a62741 (row 12323) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 312.1 | — | 0.0 |
| head | obr_pmd_nov2025:12329:964a3194129b2c01 (row 12329) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | 6.7 | — | — |
| head | obr_pmd_nov2025:23956:8842f3881bb217c0 (row 23956) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:23962:1d523435af45cc88 (row 23962) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.7 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2030.json` (sha256 `058666d8f589264bd2c95c152fee301b34d710b77687cd694100e3d4af47a3b6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
