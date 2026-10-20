# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,131.6 | -976.0 | 155.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | -307.8 | -344.8 | -37.0 | numerical | move_above_threshold |
| measure_year | total | -1,439.4 | -1,320.8 | 118.6 | numerical | move_above_threshold |
| head | child_benefit | -307.8 | -344.8 | -37.0 | numerical | move_above_threshold |
| head | income_tax | -1,131.6 | -976.0 | 155.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,131.6 | -976.0 |
| base | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | -307.8 | -344.8 |
| head | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,131.6 | -976.0 |
| head | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | -307.8 | -344.8 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `cc42be76afaa03e82fc8f08fc52d5a63abaa43a4874604745fcd102c740a6b5e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `4809e21a3dab357ac3716a10b6ae9e06a26a69d0aadd6dffdb9288c9358365f7`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.140.0_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
