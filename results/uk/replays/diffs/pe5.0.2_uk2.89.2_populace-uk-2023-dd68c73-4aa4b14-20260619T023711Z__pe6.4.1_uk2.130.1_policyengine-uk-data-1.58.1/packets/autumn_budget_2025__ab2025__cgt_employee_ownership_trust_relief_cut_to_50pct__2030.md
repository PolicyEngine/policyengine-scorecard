# Investigation packet: autumn_budget_2025 / ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Reduce Capital Gains Tax relief on qualifying disposals to employee ownership trusts from 100% to 50% from 26 November 2025
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12359:a675f99fb7dd4bed | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12365:6999b1b1b7c6bad0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23980:c1309af340dd2dca | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23986:134697a0edd688f6 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12359:a675f99fb7dd4bed (row 12359) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | 802.1 | — | — |
| head | obr_pmd_nov2025:12365:6999b1b1b7c6bad0 (row 12365) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 170.3 | — | — |
| head | obr_pmd_nov2025:23980:c1309af340dd2dca (row 23980) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 1.2 | — | — |
| head | obr_pmd_nov2025:23986:134697a0edd688f6 (row 23986) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 10.2 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
