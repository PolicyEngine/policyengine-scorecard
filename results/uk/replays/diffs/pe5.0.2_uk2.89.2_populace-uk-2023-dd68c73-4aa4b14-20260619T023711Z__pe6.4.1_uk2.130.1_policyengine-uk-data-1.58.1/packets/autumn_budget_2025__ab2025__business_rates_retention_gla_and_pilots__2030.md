# Investigation packet: autumn_budget_2025 / ab2025__business_rates_retention_gla_and_pilots / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates Retention: Extend Greater London Authority enhanced business rates retention arrangements, and pilot Business Rate Retentions for West England Combined Authority, Cornwall, and Liverpool City Region, for three years from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23794:8d8b3904d3d31a45 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23800:c91de807e91808b6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23806:62bb456cc6c6b1d9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23812:266f8f7b8a577061 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23818:62e42fc53af88f7a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23824:bb03ef0d9696ac3e | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23794:8d8b3904d3d31a45 (row 23794) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23800:c91de807e91808b6 (row 23800) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23806:62bb456cc6c6b1d9 (row 23806) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Other AME (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23812:266f8f7b8a577061 (row 23812) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSGI in CDEL | 1,200.0 | — | — |
| head | obr_pmd_nov2025:23818:62e42fc53af88f7a (row 23818) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Locally-financed capital expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23824:bb03ef0d9696ac3e (row 23824) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Other AME (capital) | -1,200.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_retention_gla_and_pilots --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_retention_gla_and_pilots_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
