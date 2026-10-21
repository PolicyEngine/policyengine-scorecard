# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21630:bf9643f47e057983 | -1,687.1 | -1,747.9 | -60.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21636:60e317e2af427357 | — | — | — | — | — |
| measure_year | total | -1,687.1 | -1,747.9 | -60.8 | numerical | move_above_threshold |
| head | housing_benefit | -132.2 | -136.5 | -4.3 | numerical | move_above_threshold |
| head | universal_credit | -1,554.9 | -1,611.4 | -56.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21630:bf9643f47e057983 (row 21630) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -952.6 | -1,687.1 | -1,747.9 |
| base | obr_pmd_nov2025:21636:60e317e2af427357 (row 21636) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare outside cap | -330.0 | — | — |
| head | obr_pmd_nov2025:21630:bf9643f47e057983 (row 21630) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -952.6 | -1,687.1 | -1,747.9 |
| head | obr_pmd_nov2025:21636:60e317e2af427357 (row 21636) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare outside cap | -330.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024.json` (sha256 `02a40eb4097972820eef6f5788f9e37cfeba804c14c64e2b82876bf8fc197f68`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024.json` (sha256 `850e4c3528cecb00c25da24f1fa789d891f9fcfc0c97ffa99cac808b3fa50a7e`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
