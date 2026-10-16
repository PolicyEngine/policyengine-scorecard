# Investigation packet: autumn_budget_2025 / ab2025__emi_eligibility_extended_to_scale_ups / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Enterprise Management Incentives (EMI): Increase eligibility to allow scale-ups, as well as start-ups, to access the scheme from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12164:db95099900e172a6 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12170:bd9be59407d40b09 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12176:640cb4e39ce5953c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12182:e1e4607ea824e5ce | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23683:9dec559c3669d298 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23689:6195a79cc5cd21c2 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12164:db95099900e172a6 (row 12164) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -2.0 | — | — |
| head | obr_pmd_nov2025:12170:bd9be59407d40b09 (row 12170) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -117.0 | — | — |
| head | obr_pmd_nov2025:12176:640cb4e39ce5953c (row 12176) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -62.0 | — | — |
| head | obr_pmd_nov2025:12182:e1e4607ea824e5ce (row 12182) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -42.0 | — | — |
| head | obr_pmd_nov2025:23683:9dec559c3669d298 (row 23683) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.0 | — | — |
| head | obr_pmd_nov2025:23689:6195a79cc5cd21c2 (row 23689) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -8.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__emi_eligibility_extended_to_scale_ups --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__emi_eligibility_extended_to_scale_ups_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
