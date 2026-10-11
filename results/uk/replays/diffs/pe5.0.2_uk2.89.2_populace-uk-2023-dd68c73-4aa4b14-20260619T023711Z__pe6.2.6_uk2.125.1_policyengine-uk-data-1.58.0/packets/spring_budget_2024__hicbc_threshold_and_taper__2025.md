# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -1,592.8 | -1,037.8 | 555.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | 0.0 | -277.8 | -277.8 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,592.8 | -1,315.5 | 277.2 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -277.8 | -277.8 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,592.8 | -1,037.8 | 555.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -1,592.8 | -1,037.8 |
| obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | 0.0 | -277.8 |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `19be94b2d580628b8d982fc38d0e321de5863a2c1fb21d1478d48a683ea115dd`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `0ac8167938bd808280704a822eea2b277bdc5da71f6f38367a757e3ff2edd552`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
