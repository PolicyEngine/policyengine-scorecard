# Investigation packet: autumn_budget_2025 / ab2025__vct_income_tax_relief_reduced / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Reduce the VCT scheme Income Tax relief from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12203:f32083ee3e7fdd78 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23710:5bd61da0191a57f2 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23716:5b5abd5e1c372e8b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12203:f32083ee3e7fdd78 (row 12203) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 92.0 | — | — |
| head | obr_pmd_nov2025:23710:5bd61da0191a57f2 (row 23710) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 1.0 | — | — |
| head | obr_pmd_nov2025:23716:5b5abd5e1c372e8b (row 23716) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 7.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_income_tax_relief_reduced --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_income_tax_relief_reduced_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
