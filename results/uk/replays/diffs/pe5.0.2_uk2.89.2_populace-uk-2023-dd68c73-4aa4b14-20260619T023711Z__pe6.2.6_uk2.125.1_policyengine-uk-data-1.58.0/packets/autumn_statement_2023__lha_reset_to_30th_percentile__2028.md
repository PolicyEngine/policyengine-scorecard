# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21634:ff94f5b54b89d1ee | -859.8 | -2,025.5 | -1,165.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21640:c223f09f1998ebbe | — | — | — | — | — |
| measure_year | total | -859.8 | -2,025.5 | -1,165.6 | numerical | move_above_threshold |
| head | housing_benefit | -86.7 | -182.5 | -95.8 | numerical | move_above_threshold |
| head | universal_credit | -773.2 | -1,843.0 | -1,069.8 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -859.8 | -2,025.5 |
| obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `069fc53a2a9c5c55542696c70cfcd7f47e8e5371bc2f9d51c68550ab4ab4d0a5`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `8efb26c1dad1540bc4ac9f5ac2b890afcd30dfe772668f39d6125918fe66670a`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
