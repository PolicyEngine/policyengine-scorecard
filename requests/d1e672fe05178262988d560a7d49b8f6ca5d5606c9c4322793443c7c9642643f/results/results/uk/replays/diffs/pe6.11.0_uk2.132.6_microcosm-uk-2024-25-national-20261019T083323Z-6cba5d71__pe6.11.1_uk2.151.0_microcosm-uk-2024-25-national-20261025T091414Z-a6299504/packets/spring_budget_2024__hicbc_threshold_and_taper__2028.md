# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10991:11a476b01436c0db | -1,711.1 | -1,601.8 | 109.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 | 0.0 | 0.0 | 0.0 | — | — |
| measure_year | total | -1,711.1 | -1,601.8 | 109.3 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -0.0 | 0.0 | — | — |
| head | income_tax | -1,711.1 | -1,601.8 | 109.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10991:11a476b01436c0db (row 10991) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -193.0 | -1,711.1 | -1,601.8 |
| base | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 (row 22210) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -465.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10991:11a476b01436c0db (row 10991) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -193.0 | -1,711.1 | -1,601.8 |
| head | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 (row 22210) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -465.0 | 0.0 | 0.0 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028.json` (sha256 `c94b30f0addb457d7e449073a175eb52b2907e8f4b43a756ebf5e4e82025d9dd`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028.json` (sha256 `5abcd9a215e413dac52df8031def5a6f18418306d638c30342dada46a164e0f8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
