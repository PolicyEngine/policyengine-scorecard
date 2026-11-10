# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12280:e36c79de21c4177c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc | 424.5 | 854.2 | 429.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12292:de3e9e9091c35830 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12298:f4388d7e0643d0ef | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12304:884ec485f8ff3f23 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 | — | — | — | — | — |
| measure_year | total | 424.5 | 854.2 | 429.7 | numerical | move_above_threshold |
| head | income_tax | 424.5 | 854.2 | 429.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12280:e36c79de21c4177c (row 12280) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -6.4 | — | — |
| base | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc (row 12286) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 427.0 | 424.5 | 854.2 |
| base | obr_pmd_nov2025:12292:de3e9e9091c35830 (row 12292) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -11.9 | — | — |
| base | obr_pmd_nov2025:12298:f4388d7e0643d0ef (row 12298) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 18.6 | — | — |
| base | obr_pmd_nov2025:12304:884ec485f8ff3f23 (row 12304) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -23.5 | — | — |
| base | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 (row 23949) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 30.7 | — | — |
| head | obr_pmd_nov2025:12280:e36c79de21c4177c (row 12280) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -6.4 | — | — |
| head | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc (row 12286) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 427.0 | 424.5 | 854.2 |
| head | obr_pmd_nov2025:12292:de3e9e9091c35830 (row 12292) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -11.9 | — | — |
| head | obr_pmd_nov2025:12298:f4388d7e0643d0ef (row 12298) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 18.6 | — | — |
| head | obr_pmd_nov2025:12304:884ec485f8ff3f23 (row 12304) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -23.5 | — | — |
| head | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 (row 23949) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 30.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__property_income_separate_rates_2029.json` (sha256 `466b77be85eae7298ea9eb3bd2020050646031aa0a72de30a89339be9d31a5c1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__property_income_separate_rates_2029.json` (sha256 `eb2697d465cff26acb479ac990695a7d97d8f7ebb08c1a760a6999172699e675`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__property_income_separate_rates_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__property_income_separate_rates_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
