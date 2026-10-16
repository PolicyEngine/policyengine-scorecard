# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21629:a71ef831d6e1cb87 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21635:7e6b2c17ec9be5e4 | — | — | — | support | supported_on_base_only |
| measure_year | total | 0.0 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21629:a71ef831d6e1cb87 (row 21629) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:21635:7e6b2c17ec9be5e4 (row 21635) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare outside cap | 0.0 | — | — |
| head | obr_pmd_nov2025:21629:a71ef831d6e1cb87 (row 21629) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:21635:7e6b2c17ec9be5e4 (row 21635) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare outside cap | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2023.json` (sha256 `f5bd85820ca104744aaf88254db52fec8dac203a815709bbd8f336b1080046f4`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2023
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
