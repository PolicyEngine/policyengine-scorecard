# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21634:ff94f5b54b89d1ee | -859.8 | -2,000.2 | -1,140.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21640:c223f09f1998ebbe | — | — | — | — | — |
| measure_year | total | -859.8 | -2,000.2 | -1,140.3 | numerical | move_above_threshold |
| head | housing_benefit | -86.7 | -169.2 | -82.5 | numerical | move_above_threshold |
| head | universal_credit | -773.2 | -1,831.0 | -1,057.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -859.8 | -2,000.2 |
| base | obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |
| head | obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -859.8 | -2,000.2 |
| head | obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `069fc53a2a9c5c55542696c70cfcd7f47e8e5371bc2f9d51c68550ab4ab4d0a5`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `9dd0b66a749fcee87834f296b87f3c8366a62d53e7b114b442a5843ede3121ea`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
