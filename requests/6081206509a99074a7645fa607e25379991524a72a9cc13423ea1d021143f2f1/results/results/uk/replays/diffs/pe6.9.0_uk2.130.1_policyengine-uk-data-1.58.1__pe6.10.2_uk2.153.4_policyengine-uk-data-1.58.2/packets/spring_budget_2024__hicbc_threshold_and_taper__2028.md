# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10991:11a476b01436c0db | -1,394.7 | -1,215.8 | 178.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 | -363.1 | -364.5 | -1.4 | — | — |
| measure_year | total | -1,757.8 | -1,580.3 | 177.5 | numerical | move_above_threshold |
| head | child_benefit | -363.1 | -364.5 | -1.4 | — | — |
| head | income_tax | -1,394.7 | -1,215.8 | 178.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10991:11a476b01436c0db (row 10991) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -193.0 | -1,394.7 | -1,215.8 |
| base | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 (row 22210) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -465.0 | -363.1 | -364.5 |
| head | obr_pmd_nov2025:10991:11a476b01436c0db (row 10991) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -193.0 | -1,394.7 | -1,215.8 |
| head | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 (row 22210) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -465.0 | -363.1 | -364.5 |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028.json` (sha256 `a982bffd46f17da5650e11744fdbc9711079f52f8c5d92de46f05d7c5d0cd2a8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028.json` (sha256 `139b38d17dda2207526110e777076145537e12292050640c86ad991b2345a37c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
