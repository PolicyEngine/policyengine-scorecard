# Investigation packet: autumn_budget_2025 / ab2025__savings_rates_plus_2pp_and_starter_limit_held / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Savings Income: Increase tax rates on savings income by 2ppts at the basic, higher and additional rate from 6 April 2027 and maintain the Starting Rate of Savings limit at £5000 from April 2026 to April 2031
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12335:4ff6459d9e873238 | 1,155.8 | 258.1 | -897.7 | numerical | move_above_threshold |
| measure_year | total | 1,155.8 | 258.1 | -897.7 | numerical | move_above_threshold |
| head | income_tax | 1,155.8 | 258.1 | -897.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12335:4ff6459d9e873238 (row 12335) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 507.3 | 1,155.8 | 258.1 |
| head | obr_pmd_nov2025:12335:4ff6459d9e873238 (row 12335) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 507.3 | 1,155.8 | 258.1 |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2030.json` (sha256 `d81eab99191e27ea2a863a2b98564e642da9ac4d71bef18f135ee1d60b385d71`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2030.json` (sha256 `ebcaa5ca79e5eb530aa4259738c4786bd9f6ff43b2a6e82d04b0eac406671247`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
