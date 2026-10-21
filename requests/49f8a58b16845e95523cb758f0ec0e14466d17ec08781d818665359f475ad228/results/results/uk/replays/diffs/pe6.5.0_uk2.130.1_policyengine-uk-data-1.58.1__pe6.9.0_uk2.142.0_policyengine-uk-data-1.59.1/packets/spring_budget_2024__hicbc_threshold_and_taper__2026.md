# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,131.6 | -1,036.0 | 95.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | -307.8 | -377.1 | -69.3 | numerical | move_above_threshold |
| measure_year | total | -1,439.4 | -1,413.1 | 26.3 | numerical | move_above_threshold |
| head | child_benefit | -307.8 | -377.1 | -69.3 | numerical | move_above_threshold |
| head | income_tax | -1,131.6 | -1,036.0 | 95.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,131.6 | -1,036.0 |
| base | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | -307.8 | -377.1 |
| head | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,131.6 | -1,036.0 |
| head | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | -307.8 | -377.1 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `cc42be76afaa03e82fc8f08fc52d5a63abaa43a4874604745fcd102c740a6b5e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `89db57d0de95dece4643233ec9ad58839e74565010cc5d2cf8c0596f1dabeb85`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
