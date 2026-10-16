# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10989:43638ad22300c9c3 | -1,720.6 | -1,131.6 | 589.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22208:6c19f800730945b5 | 0.0 | -307.8 | -307.8 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,720.6 | -1,439.4 | 281.2 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -307.8 | -307.8 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,720.6 | -1,131.6 | 589.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,720.6 | -1,131.6 |
| base | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | 0.0 | -307.8 |
| head | obr_pmd_nov2025:10989:43638ad22300c9c3 (row 10989) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -250.0 | -1,720.6 | -1,131.6 |
| head | obr_pmd_nov2025:22208:6c19f800730945b5 (row 22208) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -391.0 | 0.0 | -307.8 |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `213e032f2d5e895a9585842bac1c138bc6b7a28ea845c8cba6a5c82481816967`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026.json` (sha256 `e5c7d918ef295f3fcfdb488fcf53c66a926aa01538565eb899ae46f1b86114b1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
