# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10987:0f254c98c34bc660 | -1,491.8 | -885.0 | 606.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22206:49a0caec037600d2 | 0.0 | -273.4 | -273.4 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,491.8 | -1,158.4 | 333.4 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -273.4 | -273.4 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,491.8 | -885.0 | 606.8 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10987:0f254c98c34bc660 (row 10987) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -222.0 | -1,491.8 | -885.0 |
| obr_pmd_nov2025:22206:49a0caec037600d2 (row 22206) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -319.0 | 0.0 | -273.4 |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024.json` (sha256 `80f6e9f694dc205da1ad721c56e69b2db797da8ca50bfa74c6c07995994ce339`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024.json` (sha256 `00344f64d8ca25bf0ee3c28233fc16709bddc6e80937131414a64003302ae37d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__hicbc_threshold_and_taper --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__hicbc_threshold_and_taper --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
