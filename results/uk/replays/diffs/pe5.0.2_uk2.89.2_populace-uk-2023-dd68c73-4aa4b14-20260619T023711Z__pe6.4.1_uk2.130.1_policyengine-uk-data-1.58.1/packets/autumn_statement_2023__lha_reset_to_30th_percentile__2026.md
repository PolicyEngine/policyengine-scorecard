# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21632:353c5d3f922bfc89 | -833.7 | -1,917.2 | -1,083.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21638:ceefaca226c58d41 | — | — | — | — | — |
| measure_year | total | -833.7 | -1,917.2 | -1,083.5 | numerical | move_above_threshold |
| head | housing_benefit | -79.0 | -149.9 | -70.9 | numerical | move_above_threshold |
| head | universal_credit | -754.6 | -1,767.2 | -1,012.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21632:353c5d3f922bfc89 (row 21632) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,188.5 | -833.7 | -1,917.2 |
| base | obr_pmd_nov2025:21638:ceefaca226c58d41 (row 21638) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -399.0 | — | — |
| head | obr_pmd_nov2025:21632:353c5d3f922bfc89 (row 21632) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,188.5 | -833.7 | -1,917.2 |
| head | obr_pmd_nov2025:21638:ceefaca226c58d41 (row 21638) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -399.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026.json` (sha256 `e1cd05702abbf0e1e6f13cbee082aedb707daa98ddc4bae3d3ce6d6bfa91d985`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026.json` (sha256 `fb22d157d7bc6a8e5cc6e38119fba1a6b1c3c94c41342887c3fe0f6c2edeae1c`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
