# Investigation packet: autumn_budget_2025 / ab2025__systems_and_compliance_investment_hmrc_dwp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Systems & Compliance: Invest in HMRC, DWP and other departments to: reduce fraud and error in the welfare system & public sector; ensure tax compliance and implement Budget tax measures; and increase departmental resilience to economic shocks
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23864:4ef112787e1e192b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23870:d884433dc12bf79b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23864:4ef112787e1e192b (row 23864) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -205.0 | — | — |
| head | obr_pmd_nov2025:23870:d884433dc12bf79b (row 23870) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSGI in CDEL | -89.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__systems_and_compliance_investment_hmrc_dwp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__systems_and_compliance_investment_hmrc_dwp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
