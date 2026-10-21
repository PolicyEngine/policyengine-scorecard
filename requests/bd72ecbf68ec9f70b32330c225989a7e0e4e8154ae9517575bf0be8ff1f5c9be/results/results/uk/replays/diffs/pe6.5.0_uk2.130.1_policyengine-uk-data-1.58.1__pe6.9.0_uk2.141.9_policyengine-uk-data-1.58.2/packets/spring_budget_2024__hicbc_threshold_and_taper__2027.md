# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10990:e86af1dbeb4da64e | -1,274.7 | -1,118.0 | 156.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22209:71f606ed0f936afe | -323.6 | -317.9 | 5.7 | numerical | move_above_threshold |
| measure_year | total | -1,598.2 | -1,435.8 | 162.4 | numerical | move_above_threshold |
| head | child_benefit | -323.6 | -317.9 | 5.7 | numerical | move_above_threshold |
| head | income_tax | -1,274.7 | -1,118.0 | 156.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,274.7 | -1,118.0 |
| base | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | -323.6 | -317.9 |
| head | obr_pmd_nov2025:10990:e86af1dbeb4da64e (row 10990) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -221.0 | -1,274.7 | -1,118.0 |
| head | obr_pmd_nov2025:22209:71f606ed0f936afe (row 22209) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -426.0 | -323.6 | -317.9 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `08d394e58b585063a9dbcd8e81b7a3e8be04301f3534debb25215d2ed377c036`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027.json` (sha256 `e811a44ac50b3f7f0710696fe7b515823d54360ec7c1aabb4c2ca3289aa4916e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
