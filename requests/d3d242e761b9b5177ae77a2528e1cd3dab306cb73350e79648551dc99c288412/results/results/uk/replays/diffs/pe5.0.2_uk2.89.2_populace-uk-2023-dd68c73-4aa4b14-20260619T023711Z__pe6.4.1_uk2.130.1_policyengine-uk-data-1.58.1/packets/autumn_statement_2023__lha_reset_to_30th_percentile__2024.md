# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21630:bf9643f47e057983 | -584.6 | -1,687.1 | -1,102.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21636:60e317e2af427357 | — | — | — | — | — |
| measure_year | total | -584.6 | -1,687.1 | -1,102.5 | numerical | move_above_threshold |
| head | housing_benefit | -35.5 | -132.2 | -96.7 | numerical | move_above_threshold |
| head | universal_credit | -549.0 | -1,554.9 | -1,005.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21630:bf9643f47e057983 (row 21630) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -952.6 | -584.6 | -1,687.1 |
| base | obr_pmd_nov2025:21636:60e317e2af427357 (row 21636) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare outside cap | -330.0 | — | — |
| head | obr_pmd_nov2025:21630:bf9643f47e057983 (row 21630) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -952.6 | -584.6 | -1,687.1 |
| head | obr_pmd_nov2025:21636:60e317e2af427357 (row 21636) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare outside cap | -330.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024.json` (sha256 `3d18ee904f201df8e54a18d90f97d6bdd7e2cccdaf26652fb254df1b2089e20d`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024.json` (sha256 `1b25059169b034204e37dc04c26fac63088ac7d7d55cb65c1fe6bd7e2710b8b4`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
