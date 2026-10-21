# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12281:fe6a41b2e002c02c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12287:19f9ac9e5f5eff97 | 1,025.5 | 1,097.0 | 71.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12293:a028a5ab264bbfc5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12299:48c029a08ab46ea9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12305:de095fd703abbe33 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23950:496b684d37af3c66 | — | — | — | — | — |
| measure_year | total | 1,025.5 | 1,097.0 | 71.6 | numerical | move_above_threshold |
| head | income_tax | 1,025.5 | 1,097.0 | 71.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12281:fe6a41b2e002c02c (row 12281) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | -7.0 | — | — |
| base | obr_pmd_nov2025:12287:19f9ac9e5f5eff97 (row 12287) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 433.3 | 1,025.5 | 1,097.0 |
| base | obr_pmd_nov2025:12293:a028a5ab264bbfc5 (row 12293) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Inheritance tax | -12.9 | — | — |
| base | obr_pmd_nov2025:12299:48c029a08ab46ea9 (row 12299) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | 24.9 | — | — |
| base | obr_pmd_nov2025:12305:de095fd703abbe33 (row 12305) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Stamp duty | -25.6 | — | — |
| base | obr_pmd_nov2025:23950:496b684d37af3c66 (row 23950) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 31.0 | — | — |
| head | obr_pmd_nov2025:12281:fe6a41b2e002c02c (row 12281) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | -7.0 | — | — |
| head | obr_pmd_nov2025:12287:19f9ac9e5f5eff97 (row 12287) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 433.3 | 1,025.5 | 1,097.0 |
| head | obr_pmd_nov2025:12293:a028a5ab264bbfc5 (row 12293) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Inheritance tax | -12.9 | — | — |
| head | obr_pmd_nov2025:12299:48c029a08ab46ea9 (row 12299) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | 24.9 | — | — |
| head | obr_pmd_nov2025:12305:de095fd703abbe33 (row 12305) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Stamp duty | -25.6 | — | — |
| head | obr_pmd_nov2025:23950:496b684d37af3c66 (row 23950) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 31.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2030.json` (sha256 `475032df4ba4aa52951217dccffa075bf8bd5ee67d6ffd83a05ec7fe76cdd88d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__property_income_separate_rates_2030.json` (sha256 `40cb1efe6fbc95672ff29cecb5d90d37c1414f7a349ff461be8530546635383b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__property_income_separate_rates_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
