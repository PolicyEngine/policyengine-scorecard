# Investigation packet: autumn_budget_2025 / autumn_budget_2025__increase_to_the_economic_crime_levy / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Increase to the Economic Crime Levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12747:812a5ef3d67d2199 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24194:f2f10488d7cf4ec9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24200:e34ac598863e871c | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12747:812a5ef3d67d2199 (row 12747) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Crime levy | 113.0 | — | — |
| head | obr_pmd_nov2025:24194:f2f10488d7cf4ec9 (row 24194) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -88.0 | — | — |
| head | obr_pmd_nov2025:24200:e34ac598863e871c (row 24200) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSGI in CDEL | -25.1 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__increase_to_the_economic_crime_levy --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__increase_to_the_economic_crime_levy_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
