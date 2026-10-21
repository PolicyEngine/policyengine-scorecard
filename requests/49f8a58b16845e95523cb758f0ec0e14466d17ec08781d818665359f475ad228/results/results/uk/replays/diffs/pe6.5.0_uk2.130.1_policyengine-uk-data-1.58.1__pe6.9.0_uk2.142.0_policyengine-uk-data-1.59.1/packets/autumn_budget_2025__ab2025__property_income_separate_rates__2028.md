# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12279:d5e29857c32b332f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12285:75dff87b1a3e5f53 | 931.5 | 996.5 | 65.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12291:3e7e48668c541715 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12297:350e4e4bda28f94d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12303:0dbe53a3027ab483 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23948:9ec9e2ec991a9b24 | — | — | — | — | — |
| measure_year | total | 931.5 | 996.5 | 65.0 | numerical | move_above_threshold |
| head | income_tax | 931.5 | 996.5 | 65.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12279:d5e29857c32b332f (row 12279) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -8.1 | — | — |
| base | obr_pmd_nov2025:12285:75dff87b1a3e5f53 (row 12285) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 588.3 | 931.5 | 996.5 |
| base | obr_pmd_nov2025:12291:3e7e48668c541715 (row 12291) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -15.1 | — | — |
| base | obr_pmd_nov2025:12297:350e4e4bda28f94d (row 12297) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 12.6 | — | — |
| base | obr_pmd_nov2025:12303:0dbe53a3027ab483 (row 12303) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -29.9 | — | — |
| base | obr_pmd_nov2025:23948:9ec9e2ec991a9b24 (row 23948) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 42.4 | — | — |
| head | obr_pmd_nov2025:12279:d5e29857c32b332f (row 12279) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -8.1 | — | — |
| head | obr_pmd_nov2025:12285:75dff87b1a3e5f53 (row 12285) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 588.3 | 931.5 | 996.5 |
| head | obr_pmd_nov2025:12291:3e7e48668c541715 (row 12291) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -15.1 | — | — |
| head | obr_pmd_nov2025:12297:350e4e4bda28f94d (row 12297) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 12.6 | — | — |
| head | obr_pmd_nov2025:12303:0dbe53a3027ab483 (row 12303) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -29.9 | — | — |
| head | obr_pmd_nov2025:23948:9ec9e2ec991a9b24 (row 23948) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 42.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2028.json` (sha256 `839ac9da294f5eb1ffb294466dee8dd02c04af5725c10984bc928f534cb552d1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__property_income_separate_rates_2028.json` (sha256 `1e6b646ec431d7943f8231b80fbc7c36d0961d8b2baf234276eb91bc0cb43be4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__property_income_separate_rates_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
