# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -1,314.5 | -1,115.7 | 198.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | -7.4 | 0.0 | 7.4 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,322.0 | -1,115.7 | 206.2 | numerical | move_above_threshold |
| head | child_benefit | -7.4 | -0.0 | 7.4 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,314.5 | -1,115.7 | 198.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -1,314.5 | -1,115.7 |
| base | obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | -7.4 | 0.0 |
| head | obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -1,314.5 | -1,115.7 |
| head | obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | -7.4 | 0.0 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `0e0f9e90337a2fcc2b87382647f62c21a1e167bd3b2189e4f857d9f2ab2468ea`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `8e4151feccadf769c1fd669f3f711178189245f8ff3494927754bfbe07236e16`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
