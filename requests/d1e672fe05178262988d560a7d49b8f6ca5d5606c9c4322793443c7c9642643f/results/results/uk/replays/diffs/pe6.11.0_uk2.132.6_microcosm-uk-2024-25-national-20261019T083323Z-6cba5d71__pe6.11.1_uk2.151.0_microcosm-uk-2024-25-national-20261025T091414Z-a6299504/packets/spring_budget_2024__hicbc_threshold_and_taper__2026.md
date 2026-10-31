# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,488.2 | -1,296.9 | 191.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | -6.0 | 0.0 | 6.0 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,494.3 | -1,296.9 | 197.3 | numerical | move_above_threshold |
| head | child_benefit | -6.0 | -0.0 | 6.0 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,488.2 | -1,296.9 | 191.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,488.2 | -1,296.9 |
| base | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | -6.0 | 0.0 |
| head | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,488.2 | -1,296.9 |
| head | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | -6.0 | 0.0 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `3c1ff071a2c415b5bf6ff26565b7217f9adf336bb2bd31ea44d3c32c4ed85f22`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `a7d24338dd3c80dc6594102fd68ec2c4bdf1e5971ff1a64279ce30495b65e597`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
