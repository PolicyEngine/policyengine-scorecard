# Investigation packet: autumn_budget_2025 / ab2025__business_rates_retention_gla_and_pilots / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates Retention: Extend Greater London Authority enhanced business rates retention arrangements, and pilot Business Rate Retentions for West England Combined Authority, Cornwall, and Liverpool City Region, for three years from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23793:78a5420d81c9b32d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23799:fe1a7a50e1fecc02 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23805:2c37c9e6710e6e89 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23811:8922a33257b51e5c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23817:cb38d53f5331964d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23823:14ff0c5ba697fffc | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23793:78a5420d81c9b32d (row 23793) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23799:fe1a7a50e1fecc02 (row 23799) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Locally-financed current expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23805:2c37c9e6710e6e89 (row 23805) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other AME (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:23811:8922a33257b51e5c (row 23811) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSGI in CDEL | 1,200.0 | — | — |
| head | obr_pmd_nov2025:23817:cb38d53f5331964d (row 23817) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Locally-financed capital expenditure | 0.0 | — | — |
| head | obr_pmd_nov2025:23823:14ff0c5ba697fffc (row 23823) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other AME (capital) | -1,200.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_retention_gla_and_pilots --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_retention_gla_and_pilots_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
