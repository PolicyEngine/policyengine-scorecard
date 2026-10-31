# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical, structural
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,603.7 | -1,459.8 | 143.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22209:71f606ed0f936afe | -6.2 | 0.0 | 6.2 | numerical, structural | move_above_threshold; zero_crossing |
| measure_year | total | -1,609.8 | -1,459.8 | 150.1 | numerical | move_above_threshold |
| head | child_benefit | -6.2 | -0.0 | 6.2 | numerical, structural | move_above_threshold; zero_crossing |
| head | income_tax | -1,603.7 | -1,459.8 | 143.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,603.7 | -1,459.8 |
| base | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | -6.2 | 0.0 |
| head | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,603.7 | -1,459.8 |
| head | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | -6.2 | 0.0 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `fe6707f3708c8fdc4a39d1ee439c9bfffe8656d851e392564a53250e3a8ec0ed`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `bd03d605e187ec76be00a5e88ec8f47247027c617f8ba759aa9be6d9ecacb1d6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
