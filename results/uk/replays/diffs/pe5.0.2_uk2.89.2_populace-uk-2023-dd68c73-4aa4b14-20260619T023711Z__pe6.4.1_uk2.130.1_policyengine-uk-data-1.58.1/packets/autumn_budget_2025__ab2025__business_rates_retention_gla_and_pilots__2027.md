# Investigation packet: autumn_budget_2025 / ab2025__business_rates_retention_gla_and_pilots / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates Retention: Extend Greater London Authority enhanced business rates retention arrangements, and pilot Business Rate Retentions for West England Combined Authority, Cornwall, and Liverpool City Region, for three years from April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23791:00b25ab90b4436fd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23797:85dd174a21091903 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23803:5bbb4d1128e67eb3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23809:45fd9580fd6536ab | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23815:e6f8b6b873d84333 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23821:33ef26066b0a0a99 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23791:00b25ab90b4436fd (row 23791) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 544.4 | — | — |
| head | obr_pmd_nov2025:23797:85dd174a21091903 (row 23797) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Locally-financed current expenditure | -306.5 | — | — |
| head | obr_pmd_nov2025:23803:5bbb4d1128e67eb3 (row 23803) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (current) | -243.3 | — | — |
| head | obr_pmd_nov2025:23809:45fd9580fd6536ab (row 23809) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSGI in CDEL | 1,234.0 | — | — |
| head | obr_pmd_nov2025:23815:e6f8b6b873d84333 (row 23815) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Locally-financed capital expenditure | -1,234.0 | — | — |
| head | obr_pmd_nov2025:23821:33ef26066b0a0a99 (row 23821) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (capital) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_retention_gla_and_pilots --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_retention_gla_and_pilots_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
