# Investigation packet: autumn_budget_2025 / ab2025__british_coal_staff_superannuation_scheme_reserve_transfer / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: British Coal Staff Superannuation Scheme: Transfer investment reserve to scheme members
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12693:eeebfaef22935f59 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12699:76d1cef992bcfb83 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24128:b20107c18163b90b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12693:eeebfaef22935f59 (row 12693) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Gross operating surplus | -61.0 | — | — |
| head | obr_pmd_nov2025:12699:76d1cef992bcfb83 (row 12699) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 40.0 | — | — |
| head | obr_pmd_nov2025:24128:b20107c18163b90b (row 24128) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Public corporations capital expenditure | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__british_coal_staff_superannuation_scheme_reserve_transfer --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__british_coal_staff_superannuation_scheme_reserve_transfer_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
