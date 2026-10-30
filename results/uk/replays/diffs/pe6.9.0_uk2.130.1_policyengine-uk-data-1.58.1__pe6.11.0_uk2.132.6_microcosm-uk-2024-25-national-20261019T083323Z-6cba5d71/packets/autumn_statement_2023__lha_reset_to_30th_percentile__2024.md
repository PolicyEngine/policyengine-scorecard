# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21630:bf9643f47e057983 | -1,687.1 | -1,294.6 | 392.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21636:60e317e2af427357 | — | — | — | — | — |
| measure_year | total | -1,687.1 | -1,294.6 | 392.5 | numerical | move_above_threshold |
| head | housing_benefit | -132.2 | -130.9 | 1.3 | — | — |
| head | universal_credit | -1,554.9 | -1,163.7 | 391.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21630:bf9643f47e057983 (row 21630) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -952.6 | -1,687.1 | -1,294.6 |
| base | obr_pmd_nov2025:21636:60e317e2af427357 (row 21636) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare outside cap | -330.0 | — | — |
| head | obr_pmd_nov2025:21630:bf9643f47e057983 (row 21630) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -952.6 | -1,687.1 | -1,294.6 |
| head | obr_pmd_nov2025:21636:60e317e2af427357 (row 21636) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare outside cap | -330.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024.json` (sha256 `fa59bc038d906b37610949121a0d9cfda529c37f09213de7ffe198528296a226`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024.json` (sha256 `84256ae3f5293c59a3d83ac7c7ae78cedab0cdc2b474dd96e639a885fd97df07`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
