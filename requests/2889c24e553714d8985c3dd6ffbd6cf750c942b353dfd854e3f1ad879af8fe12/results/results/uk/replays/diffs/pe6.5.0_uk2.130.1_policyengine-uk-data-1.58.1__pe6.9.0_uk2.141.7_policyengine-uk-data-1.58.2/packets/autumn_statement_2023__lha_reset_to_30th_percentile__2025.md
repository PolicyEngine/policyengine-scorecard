# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21631:75b9415771e2e20c | -1,883.1 | -1,929.3 | -46.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21637:973f5a064b8352ab | — | — | — | — | — |
| measure_year | total | -1,883.1 | -1,929.3 | -46.2 | numerical | move_above_threshold |
| head | housing_benefit | -145.1 | -147.2 | -2.2 | numerical | move_above_threshold |
| head | universal_credit | -1,738.0 | -1,782.0 | -44.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -1,883.1 | -1,929.3 |
| base | obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |
| head | obr_pmd_nov2025:21631:75b9415771e2e20c (row 21631) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -1,092.1 | -1,883.1 | -1,929.3 |
| head | obr_pmd_nov2025:21637:973f5a064b8352ab (row 21637) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare outside cap | -391.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `b1775483183a2130cda55a67718c282141d62afff85c1f22031b0dc5d150363d`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025.json` (sha256 `5b8eaa1c3d908da7250b4959ff1f3722e751bfc0b9b6f9e47c324c08a785c5b5`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.7_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
