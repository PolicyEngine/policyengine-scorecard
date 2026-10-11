# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10991:11a476b01436c0db | -1,972.0 | -1,371.9 | 600.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22210:0ea61ade0bedb0f5 | 0.0 | -366.9 | -366.9 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,972.0 | -1,738.8 | 233.2 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -366.9 | -366.9 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,972.0 | -1,371.9 | 600.1 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10991:11a476b01436c0db (row 10991) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -193.0 | -1,972.0 | -1,371.9 |
| obr_pmd_nov2025:22210:0ea61ade0bedb0f5 (row 22210) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -465.0 | 0.0 | -366.9 |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028.json` (sha256 `795f1654f1baf12ebaf9e5d69e37c9f9b8073c24cb18285b1451c9f0dc97b3aa`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028.json` (sha256 `5a07d59ddaaa77c239927de152fed3a339d51baa1ccba4d3468d6c837206a847`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
