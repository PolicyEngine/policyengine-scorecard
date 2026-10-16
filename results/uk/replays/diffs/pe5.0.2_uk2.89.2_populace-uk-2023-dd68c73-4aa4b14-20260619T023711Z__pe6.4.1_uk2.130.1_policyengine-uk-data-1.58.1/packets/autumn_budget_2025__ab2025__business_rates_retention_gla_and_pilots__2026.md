# Investigation packet: autumn_budget_2025 / ab2025__business_rates_retention_gla_and_pilots / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates Retention: Extend Greater London Authority enhanced business rates retention arrangements, and pilot Business Rate Retentions for West England Combined Authority, Cornwall, and Liverpool City Region, for three years from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23790:f04c53ff10f68178 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23796:f7fcb515238f856f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23802:2e60f699be7ca1dd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23808:accc2b03fb519350 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23814:5be117b1f57fac7f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23820:568734484795b38c | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23790:f04c53ff10f68178 (row 23790) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 533.5 | — | — |
| head | obr_pmd_nov2025:23796:f7fcb515238f856f (row 23796) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Locally-financed current expenditure | -299.6 | — | — |
| head | obr_pmd_nov2025:23802:2e60f699be7ca1dd (row 23802) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other AME (current) | -236.0 | — | — |
| head | obr_pmd_nov2025:23808:accc2b03fb519350 (row 23808) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSGI in CDEL | 1,234.0 | — | — |
| head | obr_pmd_nov2025:23814:5be117b1f57fac7f (row 23814) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Locally-financed capital expenditure | -1,234.0 | — | — |
| head | obr_pmd_nov2025:23820:568734484795b38c (row 23820) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Other AME (capital) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_retention_gla_and_pilots --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_retention_gla_and_pilots_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
