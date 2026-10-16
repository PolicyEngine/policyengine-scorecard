# Investigation packet: autumn_budget_2025 / ab2025__emi_eligibility_extended_to_scale_ups / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Enterprise Management Incentives (EMI): Increase eligibility to allow scale-ups, as well as start-ups, to access the scheme from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12166:2fb34ced85907504 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12172:4797dd76d06cf68b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12178:f7e841b5a31f4f1b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12184:86e9bafdc19543a9 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23685:600a246e78d84074 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23691:1c909aed1bb67c29 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12166:2fb34ced85907504 (row 12166) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -16.0 | — | — |
| head | obr_pmd_nov2025:12172:4797dd76d06cf68b (row 12172) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -302.0 | — | — |
| head | obr_pmd_nov2025:12178:f7e841b5a31f4f1b (row 12178) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | -156.0 | — | — |
| head | obr_pmd_nov2025:12184:86e9bafdc19543a9 (row 12184) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -89.0 | — | — |
| head | obr_pmd_nov2025:23685:600a246e78d84074 (row 23685) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -3.0 | — | — |
| head | obr_pmd_nov2025:23691:1c909aed1bb67c29 (row 23691) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -21.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__emi_eligibility_extended_to_scale_ups --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__emi_eligibility_extended_to_scale_ups_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
