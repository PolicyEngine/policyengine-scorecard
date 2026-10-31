# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12371:1db21de47a410031 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12377:ca5b9686e623d09c | 337.3 | 218.4 | -118.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12383:6ffa1d434315db32 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12389:77692a6cdf7badf3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23992:31f86ec1bc626f82 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23998:5f9b3fc8cbd4920e | — | — | — | — | — |
| measure_year | total | 337.3 | 218.4 | -118.8 | numerical | move_above_threshold |
| head | high_value_council_tax_surcharge | 337.3 | 218.4 | -118.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12371:1db21de47a410031 (row 12371) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | -36.0 | — | — |
| base | obr_pmd_nov2025:12377:ca5b9686e623d09c (row 12377) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | High-value council tax surcharge | 478.1 | 337.3 | 218.4 |
| base | obr_pmd_nov2025:12383:6ffa1d434315db32 (row 12383) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Inheritance tax | -18.0 | — | — |
| base | obr_pmd_nov2025:12389:77692a6cdf7badf3 (row 12389) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Stamp duty | 11.1 | — | — |
| base | obr_pmd_nov2025:23992:31f86ec1bc626f82 (row 23992) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.4 | — | — |
| base | obr_pmd_nov2025:23998:5f9b3fc8cbd4920e (row 23998) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.9 | — | — |
| head | obr_pmd_nov2025:12371:1db21de47a410031 (row 12371) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | -36.0 | — | — |
| head | obr_pmd_nov2025:12377:ca5b9686e623d09c (row 12377) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | High-value council tax surcharge | 478.1 | 337.3 | 218.4 |
| head | obr_pmd_nov2025:12383:6ffa1d434315db32 (row 12383) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Inheritance tax | -18.0 | — | — |
| head | obr_pmd_nov2025:12389:77692a6cdf7badf3 (row 12389) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Stamp duty | 11.1 | — | — |
| head | obr_pmd_nov2025:23992:31f86ec1bc626f82 (row 23992) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.4 | — | — |
| head | obr_pmd_nov2025:23998:5f9b3fc8cbd4920e (row 23998) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 0.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2030.json` (sha256 `8cd624a051e432b392d74fcf42da8e98e49a042099bf3676413d7bf801d64455`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2030.json` (sha256 `f2c60ee6922aef6832e5eea4904b90ad9318e4c9fa166d5871d3279cd606601d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
