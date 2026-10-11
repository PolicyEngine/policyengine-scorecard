# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21631:75b9415771e2e20c | -799.8 | -1,916.1 | -1,116.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21637:973f5a064b8352ab | — | — | — | — | — |
| measure_year | total | -799.8 | -1,916.1 | -1,116.3 | numerical | move_above_threshold |
| head | housing_benefit | -74.6 | -156.5 | -82.0 | numerical | move_above_threshold |
| head | universal_credit | -725.2 | -1,759.5 | -1,034.3 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -799.8 | -1,916.1 |
| obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `d2769bf900bc9aad6887ca2f42617c70e1d27c2a026522ed87b12c01b77adaf6`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `43d858fa354cac3c526257a4f6ed3e5e01604158fcf3c50022e5af463e71ba2c`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
