# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21631:75b9415771e2e20c | -1,883.1 | -1,869.7 | 13.4 | — | — |
| source_row | obr_pmd_nov2025:21637:973f5a064b8352ab | — | — | — | — | — |
| measure_year | total | -1,883.1 | -1,869.7 | 13.4 | — | — |
| head | housing_benefit | -145.1 | -147.0 | -1.9 | numerical | move_above_threshold |
| head | universal_credit | -1,738.0 | -1,722.7 | 15.3 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -1,883.1 | -1,869.7 |
| base | obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |
| head | obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -1,883.1 | -1,869.7 |
| head | obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `e077fcc69af55c80dc7088b46ac87d928703cc62cf6c34ea11370ea929cd290a`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `dc97311a3dc32f8158adef655fe313ee8f7b443e45739e45a87c9f5f37b05e9a`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
