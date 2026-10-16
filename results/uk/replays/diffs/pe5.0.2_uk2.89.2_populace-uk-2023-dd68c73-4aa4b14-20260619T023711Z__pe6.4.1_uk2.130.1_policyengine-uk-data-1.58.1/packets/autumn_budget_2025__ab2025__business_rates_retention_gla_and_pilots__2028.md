# Investigation packet: autumn_budget_2025 / ab2025__business_rates_retention_gla_and_pilots / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates Retention: Extend Greater London Authority enhanced business rates retention arrangements, and pilot Business Rate Retentions for West England Combined Authority, Cornwall, and Liverpool City Region, for three years from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23792:5dfeba95cb8437ee | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23798:8e3f1993faaa7904 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23804:06a84127a4a2ada9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23810:4b5617fb2745d918 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23816:35915daca82a00a2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23822:944cab30d7537928 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23792:5dfeba95cb8437ee (row 23792) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 551.6 | — | — |
| head | obr_pmd_nov2025:23798:8e3f1993faaa7904 (row 23798) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Locally-financed current expenditure | -311.0 | — | — |
| head | obr_pmd_nov2025:23804:06a84127a4a2ada9 (row 23804) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Other AME (current) | -248.3 | — | — |
| head | obr_pmd_nov2025:23810:4b5617fb2745d918 (row 23810) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSGI in CDEL | 1,234.0 | — | — |
| head | obr_pmd_nov2025:23816:35915daca82a00a2 (row 23816) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Locally-financed capital expenditure | -1,234.0 | — | — |
| head | obr_pmd_nov2025:23822:944cab30d7537928 (row 23822) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Other AME (capital) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: no artifact

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_retention_gla_and_pilots --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_retention_gla_and_pilots_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
