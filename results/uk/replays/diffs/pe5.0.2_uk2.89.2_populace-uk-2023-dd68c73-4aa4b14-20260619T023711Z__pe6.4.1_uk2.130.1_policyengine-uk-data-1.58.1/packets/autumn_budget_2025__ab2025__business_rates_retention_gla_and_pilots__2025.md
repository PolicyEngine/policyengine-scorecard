# Investigation packet: autumn_budget_2025 / ab2025__business_rates_retention_gla_and_pilots / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates Retention: Extend Greater London Authority enhanced business rates retention arrangements, and pilot Business Rate Retentions for West England Combined Authority, Cornwall, and Liverpool City Region, for three years from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23789:0823667ed4e2a468 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23795:94ee8d6bda798dbe | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23801:90c4f8cee2c9d0f9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23807:419f2bf3b2433142 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23813:11ab3f767f101441 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23819:31d30cc2b318f31c | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23789:0823667ed4e2a468 (row 23789) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23795:94ee8d6bda798dbe (row 23795) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23801:90c4f8cee2c9d0f9 (row 23801) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other AME (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23807:419f2bf3b2433142 (row 23807) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSGI in CDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23813:11ab3f767f101441 (row 23813) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Locally-financed capital expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23819:31d30cc2b318f31c (row 23819) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Other AME (capital) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_retention_gla_and_pilots --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_retention_gla_and_pilots_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
