# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,844.2 | -1,274.7 | 569.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22209:71f606ed0f936afe | 0.0 | -323.6 | -323.6 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,844.2 | -1,598.2 | 246.0 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -323.6 | -323.6 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,844.2 | -1,274.7 | 569.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,844.2 | -1,274.7 |
| base | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | 0.0 | -323.6 |
| head | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,844.2 | -1,274.7 |
| head | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | 0.0 | -323.6 |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `79736a9be65e683ed261664c1c052f63d435462dec12bb585259d1c735814635`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `30f3bddd65e65c4d7ea39a83348048a3bcddef078584858bff329180bfb80f11`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
