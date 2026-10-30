# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12278:a0955f3d22653115 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12284:4b5e915d45bc4a6b | 889.6 | 450.4 | -439.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12290:02404f5b489513cd | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12296:63c346a2595fc727 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12302:347982f07f265709 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23947:c194392122620e36 | — | — | — | — | — |
| measure_year | total | 889.6 | 450.4 | -439.2 | numerical | move_above_threshold |
| head | income_tax | 889.6 | 450.4 | -439.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12278:a0955f3d22653115 (row 12278) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:12284:4b5e915d45bc4a6b (row 12284) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 0.0 | 889.6 | 450.4 |
| base | obr_pmd_nov2025:12290:02404f5b489513cd (row 12290) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | 0.0 | — | — |
| base | obr_pmd_nov2025:12296:63c346a2595fc727 (row 12296) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 6.5 | — | — |
| base | obr_pmd_nov2025:12302:347982f07f265709 (row 12302) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 0.0 | — | — |
| base | obr_pmd_nov2025:23947:c194392122620e36 (row 23947) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:12278:a0955f3d22653115 (row 12278) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12284:4b5e915d45bc4a6b (row 12284) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 0.0 | 889.6 | 450.4 |
| head | obr_pmd_nov2025:12290:02404f5b489513cd (row 12290) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12296:63c346a2595fc727 (row 12296) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 6.5 | — | — |
| head | obr_pmd_nov2025:12302:347982f07f265709 (row 12302) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 0.0 | — | — |
| head | obr_pmd_nov2025:23947:c194392122620e36 (row 23947) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2027.json` (sha256 `99058adff8017a2924674500805494b29d171d2ad9d416eca842d62ec5a6e1f3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__property_income_separate_rates_2027.json` (sha256 `0b992607b078db7bcc9c31e86882effceca597721e775b31f755d2ae89dad6b8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__property_income_separate_rates_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
