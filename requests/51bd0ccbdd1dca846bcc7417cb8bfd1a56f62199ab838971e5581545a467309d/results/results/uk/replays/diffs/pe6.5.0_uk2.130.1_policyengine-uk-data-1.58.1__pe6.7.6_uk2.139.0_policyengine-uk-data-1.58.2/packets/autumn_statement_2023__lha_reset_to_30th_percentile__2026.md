# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21632:353c5d3f922bfc89 | -1,917.2 | -1,961.7 | -44.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21638:ceefaca226c58d41 | — | — | — | — | — |
| measure_year | total | -1,917.2 | -1,961.7 | -44.5 | numerical | move_above_threshold |
| head | housing_benefit | -149.9 | -151.3 | -1.4 | — | — |
| head | universal_credit | -1,767.2 | -1,810.4 | -43.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21632:353c5d3f922bfc89 (row 21632) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,188.5 | -1,917.2 | -1,961.7 |
| base | obr_pmd_nov2025:21638:ceefaca226c58d41 (row 21638) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -399.0 | — | — |
| head | obr_pmd_nov2025:21632:353c5d3f922bfc89 (row 21632) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,188.5 | -1,917.2 | -1,961.7 |
| head | obr_pmd_nov2025:21638:ceefaca226c58d41 (row 21638) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -399.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026.json` (sha256 `8313ba1a6d650a3e952a8711767906484d1bb488128ef8f4b39b1e1e0299be18`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026.json` (sha256 `96fb43180f2de9a75ef0837490e8da894c9fb10d9702be16cf70a4c5da3f6517`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.139.0_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
