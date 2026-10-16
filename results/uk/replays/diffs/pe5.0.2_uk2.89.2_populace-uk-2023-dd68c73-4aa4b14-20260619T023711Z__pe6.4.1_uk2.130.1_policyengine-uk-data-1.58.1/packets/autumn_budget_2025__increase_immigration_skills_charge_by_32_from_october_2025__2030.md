# Investigation packet: autumn_budget_2025 / autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Increase Immigration Skills Charge by 32% from October 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12761:b72fb7ef4c8dfa91 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24214:38465dc0555a1b62 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12761:b72fb7ef4c8dfa91 (row 12761) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Immigration skills charge | 154.7 | — | — |
| head | obr_pmd_nov2025:24214:38465dc0555a1b62 (row 24214) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -154.7 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
