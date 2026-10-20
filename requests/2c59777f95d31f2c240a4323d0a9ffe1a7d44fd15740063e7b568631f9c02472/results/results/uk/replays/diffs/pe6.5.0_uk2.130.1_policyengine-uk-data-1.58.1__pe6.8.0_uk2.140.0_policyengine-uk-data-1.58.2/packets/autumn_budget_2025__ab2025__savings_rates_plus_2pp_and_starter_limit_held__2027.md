# Investigation packet: autumn_budget_2025 / ab2025__savings_rates_plus_2pp_and_starter_limit_held / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Savings Income: Increase tax rates on savings income by 2ppts at the basic, higher and additional rate from 6 April 2027 and maintain the Starting Rate of Savings limit at £5000 from April 2026 to April 2031
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12332:c6b82f1f54c54340 | 994.0 | 1,073.6 | 79.6 | numerical | move_above_threshold |
| measure_year | total | 994.0 | 1,073.6 | 79.6 | numerical | move_above_threshold |
| head | income_tax | 994.0 | 1,073.6 | 79.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12332:c6b82f1f54c54340 (row 12332) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 52.8 | 994.0 | 1,073.6 |
| head | obr_pmd_nov2025:12332:c6b82f1f54c54340 (row 12332) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 52.8 | 994.0 | 1,073.6 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2027.json` (sha256 `33a3d9ecc61adebf98dcdaf7957b901fc287af39384b3a8f20c8be1d0dae36ff`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2027.json` (sha256 `2dae757c893fbb11de0a60bcd34f3db103f51f795b989d93a0b5bc8f59ebdea5`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
