# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12306:73a2ece6287dce1c | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12312:a797de74813b43ad | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12318:715477c9bb8d949a | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12324:6e8044dc6b149536 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23951:caaf431ee96d9479 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23957:e09736297edd4051 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12306:73a2ece6287dce1c (row 12306) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12312:a797de74813b43ad (row 12312) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:12318:715477c9bb8d949a (row 12318) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12324:6e8044dc6b149536 (row 12324) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23951:caaf431ee96d9479 (row 23951) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23957:e09736297edd4051 (row 23957) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2025.json` (sha256 `d3831091b2cdb8b406169eb56b822eb0bc2dcd145a8644ea8b591643ee28f862`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
