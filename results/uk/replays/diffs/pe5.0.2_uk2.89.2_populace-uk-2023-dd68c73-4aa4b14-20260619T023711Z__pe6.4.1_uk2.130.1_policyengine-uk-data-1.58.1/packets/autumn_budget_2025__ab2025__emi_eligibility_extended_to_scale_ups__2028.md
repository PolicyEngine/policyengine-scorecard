# Investigation packet: autumn_budget_2025 / ab2025__emi_eligibility_extended_to_scale_ups / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Enterprise Management Incentives (EMI): Increase eligibility to allow scale-ups, as well as start-ups, to access the scheme from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12165:541f65cfa45a8a9f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12171:963b86591caaaefc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12177:b8c3eef2bad978e8 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12183:4dd8b3b02d2ec2c3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23684:02ab888415917c1c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23690:7f66e9b0f1955411 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12165:541f65cfa45a8a9f (row 12165) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -9.0 | — | — |
| head | obr_pmd_nov2025:12171:963b86591caaaefc (row 12171) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -209.0 | — | — |
| head | obr_pmd_nov2025:12177:b8c3eef2bad978e8 (row 12177) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -108.0 | — | — |
| head | obr_pmd_nov2025:12183:4dd8b3b02d2ec2c3 (row 12183) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -67.0 | — | — |
| head | obr_pmd_nov2025:23684:02ab888415917c1c (row 23684) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -2.0 | — | — |
| head | obr_pmd_nov2025:23690:7f66e9b0f1955411 (row 23690) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -14.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__emi_eligibility_extended_to_scale_ups --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__emi_eligibility_extended_to_scale_ups_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
