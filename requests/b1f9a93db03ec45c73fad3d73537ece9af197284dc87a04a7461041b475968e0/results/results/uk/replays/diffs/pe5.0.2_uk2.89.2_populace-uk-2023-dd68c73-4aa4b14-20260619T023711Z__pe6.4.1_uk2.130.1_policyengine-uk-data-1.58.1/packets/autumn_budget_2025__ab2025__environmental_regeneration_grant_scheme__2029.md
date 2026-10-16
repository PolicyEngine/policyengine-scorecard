# Investigation packet: autumn_budget_2025 / ab2025__environmental_regeneration_grant_scheme / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Environmental Regeneration: Launch a new grant scheme for public bodies to support land remediation and reinvest water company fines in projects to clean up rivers, lakes and seas
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12226:20645b9d44b3ac12 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23895:f36e510e14c4cac0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23901:9bdaecc6774ef98e | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12226:20645b9d44b3ac12 (row 12226) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Landfill tax | 25.6 | — | — |
| head | obr_pmd_nov2025:23895:f36e510e14c4cac0 (row 23895) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -15.2 | — | — |
| head | obr_pmd_nov2025:23901:9bdaecc6774ef98e (row 23901) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSGI in CDEL | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__environmental_regeneration_grant_scheme --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__environmental_regeneration_grant_scheme_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
