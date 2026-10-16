# Investigation packet: autumn_budget_2025 / ab2025__rebuilding_britain_capital_investment / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Rebuilding Britain: Accelerate delivery of growth-enhancing capital investment, including the Lower Thames Crossing
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12110:26b198e29bb6f957 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23635:29a8c7cebab9d757 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23641:dc2b468c50338778 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12110:26b198e29bb6f957 (row 12110) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 19.5 | — | — |
| head | obr_pmd_nov2025:23635:29a8c7cebab9d757 (row 23635) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (current) | -83.0 | — | — |
| head | obr_pmd_nov2025:23641:dc2b468c50338778 (row 23641) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSGI in CDEL | -949.9 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__rebuilding_britain_capital_investment --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__rebuilding_britain_capital_investment_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
