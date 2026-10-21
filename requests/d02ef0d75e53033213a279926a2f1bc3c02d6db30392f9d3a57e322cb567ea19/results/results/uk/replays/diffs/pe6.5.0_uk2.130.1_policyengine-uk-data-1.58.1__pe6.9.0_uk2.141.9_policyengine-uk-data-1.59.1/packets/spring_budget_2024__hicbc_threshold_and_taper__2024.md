# Investigation packet: spring_budget_2024 / spring_budget_2024__hicbc_threshold_and_taper / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10987:0f254c98c34bc660 | -779.6 | -914.2 | -134.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22206:49a0caec037600d2 | -336.2 | -189.6 | 146.6 | numerical | move_above_threshold |
| measure_year | total | -1,115.8 | -1,103.8 | 12.0 | numerical | move_above_threshold |
| head | child_benefit | -336.2 | -189.6 | 146.6 | numerical | move_above_threshold |
| head | income_tax | -779.6 | -914.2 | -134.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10987:0f254c98c34bc660 (row 10987) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -222.0 | -779.6 | -914.2 |
| base | obr_pmd_nov2025:22206:49a0caec037600d2 (row 22206) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -319.0 | -336.2 | -189.6 |
| head | obr_pmd_nov2025:10987:0f254c98c34bc660 (row 10987) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | -222.0 | -779.6 | -914.2 |
| head | obr_pmd_nov2025:22206:49a0caec037600d2 (row 22206) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -319.0 | -336.2 | -189.6 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024.json` (sha256 `d447896e86025f660ff1176cf6ce58260ecfa3557a814b2de117ff18cddce35e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024.json` (sha256 `41ff71882113dbc46b21c150e270bdb8db040b7cfa369a26bf14b6c85f4ad030`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {"2024-01-01.2035-12-31": 60000}, "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {"2024-01-01.2035-12-31": 50000}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__hicbc_threshold_and_taper --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
