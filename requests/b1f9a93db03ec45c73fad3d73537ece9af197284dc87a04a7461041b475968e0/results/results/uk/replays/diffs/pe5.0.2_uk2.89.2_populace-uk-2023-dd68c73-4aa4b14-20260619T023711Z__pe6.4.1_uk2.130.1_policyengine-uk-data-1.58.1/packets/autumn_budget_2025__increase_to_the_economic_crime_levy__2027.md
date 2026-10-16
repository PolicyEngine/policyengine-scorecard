# Investigation packet: autumn_budget_2025 / autumn_budget_2025__increase_to_the_economic_crime_levy / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Increase to the Economic Crime Levy
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12746:8c79af74584ec375 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24193:8011242a7d5190e5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24199:d676ac5afdc23097 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12746:8c79af74584ec375 (row 12746) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Crime levy | 111.0 | — | — |
| head | obr_pmd_nov2025:24193:8011242a7d5190e5 (row 24193) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -85.0 | — | — |
| head | obr_pmd_nov2025:24199:d676ac5afdc23097 (row 24199) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSGI in CDEL | -26.2 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__increase_to_the_economic_crime_levy --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__increase_to_the_economic_crime_levy_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
