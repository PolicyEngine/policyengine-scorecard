# Investigation packet: autumn_budget_2025 / ab2025__motability_vat_on_advance_payments_and_ipt / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Motability: Introduce VAT at the standard rate on Advance Payments paid to Motability or equivalent schemes, and Insurance Premium Tax at the standard rate on insurance related to vehicle leases, from 1 July 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12090:1188631cef7c0330 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12096:373b025f9677162a | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12090:1188631cef7c0330 (row 12090) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Insurance premium tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12096:373b025f9677162a (row 12096) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__motability_vat_on_advance_payments_and_ipt --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__motability_vat_on_advance_payments_and_ipt_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
