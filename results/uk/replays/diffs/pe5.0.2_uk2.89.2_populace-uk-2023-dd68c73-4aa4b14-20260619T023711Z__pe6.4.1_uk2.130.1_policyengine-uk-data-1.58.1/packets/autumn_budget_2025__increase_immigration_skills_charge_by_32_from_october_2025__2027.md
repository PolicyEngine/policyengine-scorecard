# Investigation packet: autumn_budget_2025 / autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025 / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Increase Immigration Skills Charge by 32% from October 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12758:5dc5154356e18cfe | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24211:a25a4e77df819642 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12758:5dc5154356e18cfe (row 12758) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Immigration skills charge | 164.0 | — | — |
| head | obr_pmd_nov2025:24211:a25a4e77df819642 (row 24211) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -164.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
