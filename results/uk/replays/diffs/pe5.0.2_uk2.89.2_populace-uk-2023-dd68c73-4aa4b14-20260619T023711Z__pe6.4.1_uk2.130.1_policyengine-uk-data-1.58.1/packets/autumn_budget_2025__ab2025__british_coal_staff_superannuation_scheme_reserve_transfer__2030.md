# Investigation packet: autumn_budget_2025 / ab2025__british_coal_staff_superannuation_scheme_reserve_transfer / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: British Coal Staff Superannuation Scheme: Transfer investment reserve to scheme members
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12695:5a208e3ccaed48b5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12701:52845dbea8417bb0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24130:8e14d091d903952e | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12695:5a208e3ccaed48b5 (row 12695) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Gross operating surplus | -53.0 | — | — |
| head | obr_pmd_nov2025:12701:52845dbea8417bb0 (row 12701) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 36.0 | — | — |
| head | obr_pmd_nov2025:24130:8e14d091d903952e (row 24130) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Public corporations capital expenditure | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__british_coal_staff_superannuation_scheme_reserve_transfer --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__british_coal_staff_superannuation_scheme_reserve_transfer_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
