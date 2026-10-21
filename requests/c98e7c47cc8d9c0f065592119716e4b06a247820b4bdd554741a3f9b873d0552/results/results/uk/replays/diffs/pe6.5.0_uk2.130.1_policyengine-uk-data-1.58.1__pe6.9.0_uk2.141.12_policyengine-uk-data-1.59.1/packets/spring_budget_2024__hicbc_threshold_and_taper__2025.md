# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -980.5 | -934.9 | 45.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | -282.5 | -337.0 | -54.5 | numerical | move_above_threshold |
| measure_year | total | -1,263.0 | -1,271.9 | -9.0 | — | — |
| head | child_benefit | -282.5 | -337.0 | -54.5 | numerical | move_above_threshold |
| head | income_tax | -980.5 | -934.9 | 45.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -980.5 | -934.9 |
| base | obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | -282.5 | -337.0 |
| head | obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -980.5 | -934.9 |
| head | obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | -282.5 | -337.0 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `94318470b42905aafc78093eb0c8d7fc7c3eeca16fa2b5118161d6c1225ff88c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `aa436b9fc26be557cc2666c1d0b0a044e9aed6915281a4d7be04af48be0e3b91`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
