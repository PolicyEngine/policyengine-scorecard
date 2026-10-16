# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12279:d5e29857c32b332f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12285:75dff87b1a3e5f53 | — | 931.5 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12291:3e7e48668c541715 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12297:350e4e4bda28f94d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12303:0dbe53a3027ab483 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23948:9ec9e2ec991a9b24 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 931.5 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12279:d5e29857c32b332f (row 12279) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -8.1 | — | — |
| head | obr_pmd_nov2025:12285:75dff87b1a3e5f53 (row 12285) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 588.3 | — | 931.5 |
| head | obr_pmd_nov2025:12291:3e7e48668c541715 (row 12291) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -15.1 | — | — |
| head | obr_pmd_nov2025:12297:350e4e4bda28f94d (row 12297) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 12.6 | — | — |
| head | obr_pmd_nov2025:12303:0dbe53a3027ab483 (row 12303) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | -29.9 | — | — |
| head | obr_pmd_nov2025:23948:9ec9e2ec991a9b24 (row 23948) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 42.4 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2028.json` (sha256 `d1b2a67fa242cdf71566a2f32247c43dd249d9bb6ea6d9c2f31391e70c583563`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
