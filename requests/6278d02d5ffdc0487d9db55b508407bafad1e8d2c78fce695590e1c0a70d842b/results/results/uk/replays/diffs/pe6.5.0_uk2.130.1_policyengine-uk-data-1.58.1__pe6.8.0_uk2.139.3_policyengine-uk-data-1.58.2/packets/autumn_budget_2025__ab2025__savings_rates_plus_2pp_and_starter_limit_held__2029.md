# Investigation packet: autumn_budget_2025 / ab2025__savings_rates_plus_2pp_and_starter_limit_held / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Savings Income: Increase tax rates on savings income by 2ppts at the basic, higher and additional rate from 6 April 2027 and maintain the Starting Rate of Savings limit at £5000 from April 2026 to April 2031
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12334:b5f43f5e38667473 | 1,096.2 | 1,182.9 | 86.6 | numerical | move_above_threshold |
| measure_year | total | 1,096.2 | 1,182.9 | 86.6 | numerical | move_above_threshold |
| head | income_tax | 1,096.2 | 1,182.9 | 86.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12334:b5f43f5e38667473 (row 12334) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 469.1 | 1,096.2 | 1,182.9 |
| head | obr_pmd_nov2025:12334:b5f43f5e38667473 (row 12334) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 469.1 | 1,096.2 | 1,182.9 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2029.json` (sha256 `25b3e7d4a86c6093072eb51bddb118e8f703ec74d5978ad18699aadc8b53fb63`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2029.json` (sha256 `a8201b85e9541352c8549678c2d76d252141613d6d35414cfa929a63cd49ac9c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.savings.additional": {"2027-01-01.2030-12-31": 0.45}, "gov.hmrc.income_tax.rates.savings.basic": {"2027-01-01.2030-12-31": 0.2}, "gov.hmrc.income_tax.rates.savings.higher": {"2027-01-01.2030-12-31": 0.4}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.139.3_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
