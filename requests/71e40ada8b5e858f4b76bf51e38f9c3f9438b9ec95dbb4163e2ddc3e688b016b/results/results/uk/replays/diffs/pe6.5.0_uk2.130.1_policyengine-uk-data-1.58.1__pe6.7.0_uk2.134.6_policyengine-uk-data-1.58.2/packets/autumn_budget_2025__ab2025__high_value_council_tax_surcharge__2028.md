# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.0_uk2.134.6_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12369:1c7f6fbb4117ff9a | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12375:297fca1f0cf23095 | 483.9 | 458.4 | -25.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12381:b19a4aab53a82dbb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12387:e6f697153fe34521 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23990:9db8028b6ef06f71 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23996:6faaf572a33432bb | — | — | — | — | — |
| measure_year | total | 483.9 | 458.4 | -25.5 | numerical | move_above_threshold |
| head | high_value_council_tax_surcharge | 483.9 | 458.4 | -25.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12369:1c7f6fbb4117ff9a (row 12369) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -45.4 | — | — |
| base | obr_pmd_nov2025:12375:297fca1f0cf23095 (row 12375) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | High-value council tax surcharge | 454.3 | 483.9 | 458.4 |
| base | obr_pmd_nov2025:12381:b19a4aab53a82dbb (row 12381) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -13.1 | — | — |
| base | obr_pmd_nov2025:12387:e6f697153fe34521 (row 12387) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | 2.6 | — | — |
| base | obr_pmd_nov2025:23990:9db8028b6ef06f71 (row 23990) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.2 | — | — |
| base | obr_pmd_nov2025:23996:6faaf572a33432bb (row 23996) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 0.5 | — | — |
| head | obr_pmd_nov2025:12369:1c7f6fbb4117ff9a (row 12369) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -45.4 | — | — |
| head | obr_pmd_nov2025:12375:297fca1f0cf23095 (row 12375) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | High-value council tax surcharge | 454.3 | 483.9 | 458.4 |
| head | obr_pmd_nov2025:12381:b19a4aab53a82dbb (row 12381) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -13.1 | — | — |
| head | obr_pmd_nov2025:12387:e6f697153fe34521 (row 12387) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | 2.6 | — | — |
| head | obr_pmd_nov2025:23990:9db8028b6ef06f71 (row 23990) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 0.2 | — | — |
| head | obr_pmd_nov2025:23996:6faaf572a33432bb (row 23996) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 0.5 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2028.json` (sha256 `9ef0857afae5abcd32ea1e0eedfa96aa72753a1087c6358a7d1ba9be6a562dc2`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.0_uk2.134.6_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2028.json` (sha256 `d48552e19feb2574d34cfcf06e0b9c0e821f9bc93eaf8c3a999976c3d08d7a81`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.7.0_uk2.134.6_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.0_uk2.134.6_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
