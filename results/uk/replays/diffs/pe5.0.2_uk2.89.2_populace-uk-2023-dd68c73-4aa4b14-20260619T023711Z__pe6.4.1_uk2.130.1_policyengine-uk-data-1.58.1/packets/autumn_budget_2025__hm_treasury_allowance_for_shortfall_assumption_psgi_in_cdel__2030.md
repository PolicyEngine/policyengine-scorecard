# Investigation packet: autumn_budget_2025 / autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: HM Treasury Allowance for Shortfall assumption - PSGI in CDEL
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:24286:27303b1b5b9c63a1 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:24286:27303b1b5b9c63a1 (row 24286) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSGI in CDEL | -3,250.5 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
