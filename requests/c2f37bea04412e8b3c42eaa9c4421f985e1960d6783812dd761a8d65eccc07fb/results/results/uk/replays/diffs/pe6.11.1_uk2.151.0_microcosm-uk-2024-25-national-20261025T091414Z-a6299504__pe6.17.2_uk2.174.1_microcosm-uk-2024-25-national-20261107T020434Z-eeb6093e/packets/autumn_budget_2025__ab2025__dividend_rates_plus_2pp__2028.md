# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12309:0fbcc0c4dc21227c | 1,103.7 | 1,120.8 | 17.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12315:7febae39f08cbfb1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12321:a77bafa0f6f15194 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12327:ba862df46bba3c9b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23954:ab16efe1d4cff6cf | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23960:7c6c0ab684177612 | — | — | — | — | — |
| measure_year | total | 1,103.7 | 1,120.8 | 17.1 | numerical | move_above_threshold |
| head | income_tax | 1,103.7 | 1,120.8 | 17.1 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12309:0fbcc0c4dc21227c (row 12309) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,213.1 | 1,103.7 | 1,120.8 |
| base | obr_pmd_nov2025:12315:7febae39f08cbfb1 (row 12315) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -270.8 | — | — |
| base | obr_pmd_nov2025:12321:a77bafa0f6f15194 (row 12321) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 206.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12327:ba862df46bba3c9b (row 12327) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 11.7 | — | — |
| base | obr_pmd_nov2025:23954:ab16efe1d4cff6cf (row 23954) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.1 | — | — |
| base | obr_pmd_nov2025:23960:7c6c0ab684177612 (row 23960) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 1.3 | — | — |
| head | obr_pmd_nov2025:12309:0fbcc0c4dc21227c (row 12309) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 1,213.1 | 1,103.7 | 1,120.8 |
| head | obr_pmd_nov2025:12315:7febae39f08cbfb1 (row 12315) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -270.8 | — | — |
| head | obr_pmd_nov2025:12321:a77bafa0f6f15194 (row 12321) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 206.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12327:ba862df46bba3c9b (row 12327) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 11.7 | — | — |
| head | obr_pmd_nov2025:23954:ab16efe1d4cff6cf (row 23954) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.1 | — | — |
| head | obr_pmd_nov2025:23960:7c6c0ab684177612 (row 23960) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 1.3 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2028.json` (sha256 `506e81d6733c9640ac242d7ebe0418eb149ffbc8d6c3c353659b84c971044403`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2028.json` (sha256 `24000ba8b249ba416da182903f4510ff327efa61f2b91f834bb019d0f3648ad8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
