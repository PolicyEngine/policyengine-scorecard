# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12278:a0955f3d22653115 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12284:4b5e915d45bc4a6b | — | 889.6 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12290:02404f5b489513cd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12296:63c346a2595fc727 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12302:347982f07f265709 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23947:c194392122620e36 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 889.6 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12278:a0955f3d22653115 (row 12278) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12284:4b5e915d45bc4a6b (row 12284) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 0.0 | — | 889.6 |
| head | obr_pmd_nov2025:12290:02404f5b489513cd (row 12290) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12296:63c346a2595fc727 (row 12296) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 6.5 | — | — |
| head | obr_pmd_nov2025:12302:347982f07f265709 (row 12302) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 0.0 | — | — |
| head | obr_pmd_nov2025:23947:c194392122620e36 (row 23947) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2027.json` (sha256 `6e8d6d3c8588b6b3e3f3a29c05d4eec0910889902bb89edd8654361b8a52a2cb`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
