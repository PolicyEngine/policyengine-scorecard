# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12308:5c1e45be5eff2e8d | 954.3 | 1,042.3 | 88.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12314:745357cae61de123 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12320:1654d36a764609bd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12326:b1eebc6c379e8995 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23953:91469837ddf069e6 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23959:39d2734cb67f68a1 | — | — | — | — | — |
| measure_year | total | 954.3 | 1,042.3 | 88.0 | numerical | move_above_threshold |
| head | income_tax | 954.3 | 1,042.3 | 88.0 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12308:5c1e45be5eff2e8d (row 12308) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,030.7 | 954.3 | 1,042.3 |
| base | obr_pmd_nov2025:12314:745357cae61de123 (row 12314) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -182.6 | — | — |
| base | obr_pmd_nov2025:12320:1654d36a764609bd (row 12320) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 122.2 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12326:b1eebc6c379e8995 (row 12326) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 16.9 | — | — |
| base | obr_pmd_nov2025:23953:91469837ddf069e6 (row 23953) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.2 | — | — |
| base | obr_pmd_nov2025:23959:39d2734cb67f68a1 (row 23959) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:12308:5c1e45be5eff2e8d (row 12308) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 1,030.7 | 954.3 | 1,042.3 |
| head | obr_pmd_nov2025:12314:745357cae61de123 (row 12314) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -182.6 | — | — |
| head | obr_pmd_nov2025:12320:1654d36a764609bd (row 12320) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 122.2 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12326:b1eebc6c379e8995 (row 12326) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 16.9 | — | — |
| head | obr_pmd_nov2025:23953:91469837ddf069e6 (row 23953) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.2 | — | — |
| head | obr_pmd_nov2025:23959:39d2734cb67f68a1 (row 23959) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027.json` (sha256 `7970c90a8394eb2674c453f57b1aef362ca5d26caead9a49fb256c6f6686c60d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027.json` (sha256 `b9d0ecafecc8d23f80a897be4c893757928c5c44253aa5a4ac4329b70c1c0a22`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
