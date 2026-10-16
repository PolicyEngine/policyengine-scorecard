# Investigation packet: autumn_budget_2025 / ab2025__systems_and_compliance_investment_hmrc_dwp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Systems & Compliance: Invest in HMRC, DWP and other departments to: reduce fraud and error in the welfare system & public sector; ensure tax compliance and implement Budget tax measures; and increase departmental resilience to economic shocks
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23863:0960788be6d6acff | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23869:0a298441c60ae086 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23863:0960788be6d6acff (row 23863) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -370.2 | — | — |
| head | obr_pmd_nov2025:23869:0a298441c60ae086 (row 23869) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSGI in CDEL | -121.1 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__systems_and_compliance_investment_hmrc_dwp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__systems_and_compliance_investment_hmrc_dwp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
