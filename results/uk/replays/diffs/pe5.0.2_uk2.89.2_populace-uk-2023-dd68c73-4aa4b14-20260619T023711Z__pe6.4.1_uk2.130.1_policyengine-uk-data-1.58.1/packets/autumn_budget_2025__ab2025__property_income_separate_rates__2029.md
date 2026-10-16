# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12280:e36c79de21c4177c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc | — | 976.2 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12292:de3e9e9091c35830 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12298:f4388d7e0643d0ef | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12304:884ec485f8ff3f23 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 976.2 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12280:e36c79de21c4177c (row 12280) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -6.4 | — | — |
| head | obr_pmd_nov2025:12286:9fd0f4d9d9482bcc (row 12286) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 427.0 | — | 976.2 |
| head | obr_pmd_nov2025:12292:de3e9e9091c35830 (row 12292) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -11.9 | — | — |
| head | obr_pmd_nov2025:12298:f4388d7e0643d0ef (row 12298) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 18.6 | — | — |
| head | obr_pmd_nov2025:12304:884ec485f8ff3f23 (row 12304) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -23.5 | — | — |
| head | obr_pmd_nov2025:23949:adcbd7af1eaeebb1 (row 23949) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 30.7 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2029.json` (sha256 `fb323743217afbbeaa0c0ba704eb8adf5f3309634d733944e8387539e4a1abae`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
