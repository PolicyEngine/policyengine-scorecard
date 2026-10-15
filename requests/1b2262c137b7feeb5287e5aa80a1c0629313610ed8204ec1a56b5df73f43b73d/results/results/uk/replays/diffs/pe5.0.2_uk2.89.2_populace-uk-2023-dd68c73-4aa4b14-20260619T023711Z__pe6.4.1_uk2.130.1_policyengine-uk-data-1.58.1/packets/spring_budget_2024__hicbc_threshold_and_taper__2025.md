# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10988:6a33f7863750611c | -1,592.8 | -980.5 | 612.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22207:01b31afdbe23dae6 | 0.0 | -282.5 | -282.5 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,592.8 | -1,263.0 | 329.8 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -282.5 | -282.5 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,592.8 | -980.5 | 612.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -1,592.8 | -980.5 |
| base | obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | 0.0 | -282.5 |
| head | obr_pmd_nov2025:10988:6a33f7863750611c (row 10988) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | -277.0 | -1,592.8 | -980.5 |
| head | obr_pmd_nov2025:22207:01b31afdbe23dae6 (row 22207) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -359.0 | 0.0 | -282.5 |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `19be94b2d580628b8d982fc38d0e321de5863a2c1fb21d1478d48a683ea115dd`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025.json` (sha256 `7678f9d2bf3ac8a792d0e4b178746588c9ecdd51d9dcabb97cbf772a006c633d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
