# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,459.8 | -1,494.4 | -34.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22209:71f606ed0f936afe | 0.0 | 0.0 | 0.0 | — | — |
| measure_year | total | -1,459.8 | -1,494.4 | -34.6 | numerical | move_above_threshold |
| head | child_benefit | -0.0 | -0.0 | 0.0 | — | — |
| head | income_tax | -1,459.8 | -1,494.4 | -34.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,459.8 | -1,494.4 |
| base | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,459.8 | -1,494.4 |
| head | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | 0.0 | 0.0 |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `d971a5af2df8212dc85f6faa156c3f9928a0a2c54bd7a25f781dc1edf21c4f39`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `4abc13ad4d804a91cb81c2ff07651ba45fcd6b0e6d4497246dd92c4f0182257b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
