# Investigation packet: autumn_budget_2025 / ab2025__property_income_separate_rates / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12277:6ce827490c5daa83 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12283:7d672bc1fee61364 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12289:ab09df21e9989520 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12295:46ea47c6a25ea894 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12301:f163cbc02ac890af | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23946:f7e6722cea0e8858 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12277:6ce827490c5daa83 (row 12277) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12283:7d672bc1fee61364 (row 12283) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12289:ab09df21e9989520 (row 12289) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12295:46ea47c6a25ea894 (row 12295) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 0.8 | — | — |
| head | obr_pmd_nov2025:12301:f163cbc02ac890af (row 12301) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | 0.0 | — | — |
| head | obr_pmd_nov2025:23946:f7e6722cea0e8858 (row 23946) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2026.json` (sha256 `660b75030483110d70cb172dc2f169a1b87f9fda7502e1056bfe9d93b5e3548f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.property.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.property.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.property.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__property_income_separate_rates --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__property_income_separate_rates_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
