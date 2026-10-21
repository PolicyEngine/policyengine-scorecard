# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12280:e36c79de21c4177c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc | 976.2 | 1,044.3 | 68.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12292:de3e9e9091c35830 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12298:f4388d7e0643d0ef | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12304:884ec485f8ff3f23 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 | — | — | — | — | — |
| measure_year | total | 976.2 | 1,044.3 | 68.1 | numerical | move_above_threshold |
| head | income_tax | 976.2 | 1,044.3 | 68.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12280:e36c79de21c4177c (row 12280) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -6.4 | — | — |
| base | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc (row 12286) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 427.0 | 976.2 | 1,044.3 |
| base | obr_pmd_nov2025:12292:de3e9e9091c35830 (row 12292) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -11.9 | — | — |
| base | obr_pmd_nov2025:12298:f4388d7e0643d0ef (row 12298) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 18.6 | — | — |
| base | obr_pmd_nov2025:12304:884ec485f8ff3f23 (row 12304) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -23.5 | — | — |
| base | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 (row 23949) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 30.7 | — | — |
| head | obr_pmd_nov2025:12280:e36c79de21c4177c (row 12280) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -6.4 | — | — |
| head | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc (row 12286) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 427.0 | 976.2 | 1,044.3 |
| head | obr_pmd_nov2025:12292:de3e9e9091c35830 (row 12292) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -11.9 | — | — |
| head | obr_pmd_nov2025:12298:f4388d7e0643d0ef (row 12298) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 18.6 | — | — |
| head | obr_pmd_nov2025:12304:884ec485f8ff3f23 (row 12304) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -23.5 | — | — |
| head | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 (row 23949) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 30.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2029.json` (sha256 `ddc928b45430d749aa4f07a99b45eb6438314df6e70c72b443a19f8aff2aae6d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__property_income_separate_rates_2029.json` (sha256 `702a972ea29a70d160a4cffe5d5e96f4c555eb0aa2632811885dfbedbaf8a6e1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__property_income_separate_rates_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
