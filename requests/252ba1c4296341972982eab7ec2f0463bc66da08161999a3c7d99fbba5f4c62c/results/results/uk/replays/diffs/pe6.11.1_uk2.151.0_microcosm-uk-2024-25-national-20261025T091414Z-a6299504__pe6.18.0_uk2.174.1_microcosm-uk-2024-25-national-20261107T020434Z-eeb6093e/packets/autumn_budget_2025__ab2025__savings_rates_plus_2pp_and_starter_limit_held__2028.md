# Investigation packet: autumn_budget_2025 / ab2025__savings_rates_plus_2pp_and_starter_limit_held / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Savings Income: Increase tax rates on savings income by 2ppts at the basic, higher and additional rate from 6 April 2027 and maintain the Starting Rate of Savings limit at £5000 from April 2026 to April 2031
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12333:e7cb08bb9df37f81 | 284.8 | 1,120.6 | 835.8 | numerical | move_above_threshold |
| measure_year | total | 284.8 | 1,120.6 | 835.8 | numerical | move_above_threshold |
| head | income_tax | 284.8 | 1,120.6 | 835.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12333:e7cb08bb9df37f81 (row 12333) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 522.9 | 284.8 | 1,120.6 |
| head | obr_pmd_nov2025:12333:e7cb08bb9df37f81 (row 12333) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 522.9 | 284.8 | 1,120.6 |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2028.json` (sha256 `0ccd46dccb10301f2c3a24743255ebce549a2bc9ecd38594d72490853d5b29db`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2028.json` (sha256 `b6f81ced7e0931ab2ad4825c757b28e0836bf83380e0c494849a1ab67e1dc87f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
