# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12310:28dedd8eb897f229 | 1,006.6 | 1,101.5 | 94.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12316:2ab7b0caaa0ace9c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12322:5c15c5632066facd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12328:1632ff19af602d74 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23955:dbe102793cb8649d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23961:62a49588692d5238 | — | — | — | — | — |
| measure_year | total | 1,006.6 | 1,101.5 | 94.9 | numerical | move_above_threshold |
| head | income_tax | 1,006.6 | 1,101.5 | 94.9 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12310:28dedd8eb897f229 (row 12310) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,387.7 | 1,006.6 | 1,101.5 |
| base | obr_pmd_nov2025:12316:2ab7b0caaa0ace9c (row 12316) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -336.4 | — | — |
| base | obr_pmd_nov2025:12322:5c15c5632066facd (row 12322) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 266.5 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12328:1632ff19af602d74 (row 12328) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 8.6 | — | — |
| base | obr_pmd_nov2025:23955:dbe102793cb8649d (row 23955) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.1 | — | — |
| base | obr_pmd_nov2025:23961:62a49588692d5238 (row 23961) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 0.9 | — | — |
| head | obr_pmd_nov2025:12310:28dedd8eb897f229 (row 12310) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,387.7 | 1,006.6 | 1,101.5 |
| head | obr_pmd_nov2025:12316:2ab7b0caaa0ace9c (row 12316) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -336.4 | — | — |
| head | obr_pmd_nov2025:12322:5c15c5632066facd (row 12322) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 266.5 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12328:1632ff19af602d74 (row 12328) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 8.6 | — | — |
| head | obr_pmd_nov2025:23955:dbe102793cb8649d (row 23955) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:23961:62a49588692d5238 (row 23961) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 0.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2029.json` (sha256 `f36de12fce6069936f24b61a4b0c92ada96d6c423c03d075c2edd4a4f7fcbd3b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2029.json` (sha256 `fdd8f665b307ada67cc83b83f3dcd24feea4e8d9c2497f84cd9aedd4c09c4fec`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
