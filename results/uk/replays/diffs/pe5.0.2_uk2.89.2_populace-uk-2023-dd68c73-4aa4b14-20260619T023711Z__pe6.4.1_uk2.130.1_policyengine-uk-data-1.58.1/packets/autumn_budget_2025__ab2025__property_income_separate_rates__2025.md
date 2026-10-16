# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12276:1358a50757a0a548 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12282:7f38814af1f52a50 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12288:41e92fa541a78d9c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12294:cf4ed55d420364c2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12300:6f470e8148ff30ef | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23945:8f9256e4921b03e6 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12276:1358a50757a0a548 (row 12276) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12282:7f38814af1f52a50 (row 12282) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12288:41e92fa541a78d9c (row 12288) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12294:cf4ed55d420364c2 (row 12294) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:12300:6f470e8148ff30ef (row 12300) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | 0.0 | — | — |
| head | obr_pmd_nov2025:23945:8f9256e4921b03e6 (row 23945) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2025.json` (sha256 `703e520d7db2c41a62c935f19ce7bb9f06740f462f4128a525d734f3d853c722`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
