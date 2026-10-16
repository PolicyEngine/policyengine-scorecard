# Investigation packet: autumn_budget_2025 / ab2025__fisheries_and_coastal_growth_fund / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Fisheries and Coastal Growth: Launch a fund to support the domestic fishing sector and coastal communities
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23755:8f3ce8ae300cd385 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23761:169eaa53d9dc4267 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23755:8f3ce8ae300cd385 (row 23755) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -13.5 | — | — |
| head | obr_pmd_nov2025:23761:169eaa53d9dc4267 (row 23761) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSGI in CDEL | -20.4 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__fisheries_and_coastal_growth_fund --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__fisheries_and_coastal_growth_fund_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
