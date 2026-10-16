# Investigation packet: autumn_budget_2025 / ab2025__british_coal_staff_superannuation_scheme_reserve_transfer / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: British Coal Staff Superannuation Scheme: Transfer investment reserve to scheme members
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12692:16824392362abacd | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12698:158456023dfaa169 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24127:cff22fe644a40c51 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12692:16824392362abacd (row 12692) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Gross operating surplus | -65.0 | — | — |
| head | obr_pmd_nov2025:12698:158456023dfaa169 (row 12698) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 42.0 | — | — |
| head | obr_pmd_nov2025:24127:cff22fe644a40c51 (row 24127) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Public corporations capital expenditure | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__british_coal_staff_superannuation_scheme_reserve_transfer --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__british_coal_staff_superannuation_scheme_reserve_transfer_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
