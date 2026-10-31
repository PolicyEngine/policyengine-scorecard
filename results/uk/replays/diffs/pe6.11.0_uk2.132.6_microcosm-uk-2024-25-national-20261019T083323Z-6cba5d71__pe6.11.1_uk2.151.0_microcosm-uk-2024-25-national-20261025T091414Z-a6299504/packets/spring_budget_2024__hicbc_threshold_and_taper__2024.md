# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10987:0f254c98c34bc660 | -1,117.4 | -952.4 | 165.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22206:49a0caec037600d2 | -10.3 | 0.0 | 10.3 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,127.8 | -952.4 | 175.4 | numerical | move_above_threshold |
| head | child_benefit | -10.3 | -0.0 | 10.3 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,117.4 | -952.4 | 165.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10987:0f254c98c34bc660 (row 10987) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -222.0 | -1,117.4 | -952.4 |
| base | obr_pmd_nov2025:22206:49a0caec037600d2 (row 22206) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -319.0 | -10.3 | 0.0 |
| head | obr_pmd_nov2025:10987:0f254c98c34bc660 (row 10987) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -222.0 | -1,117.4 | -952.4 |
| head | obr_pmd_nov2025:22206:49a0caec037600d2 (row 22206) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -319.0 | -10.3 | 0.0 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024.json` (sha256 `076b6982e8bc47a46837a15874976e06a95adcc139bd90290d79fe24375f9380`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024.json` (sha256 `1f934300e3c3da859bf752893f2e9c7c42ddaf684a5836df6e9cb10e6c1287d3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
