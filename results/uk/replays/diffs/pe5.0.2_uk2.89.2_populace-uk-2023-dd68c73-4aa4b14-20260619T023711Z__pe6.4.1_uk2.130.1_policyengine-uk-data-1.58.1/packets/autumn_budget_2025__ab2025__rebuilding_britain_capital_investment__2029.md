# Investigation packet: autumn_budget_2025 / ab2025__rebuilding_britain_capital_investment / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Rebuilding Britain: Accelerate delivery of growth-enhancing capital investment, including the Lower Thames Crossing
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12112:a399b129c64ed3a5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23637:8623dae9cc846018 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23643:ca6ac37cb3f11ea1 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12112:a399b129c64ed3a5 (row 12112) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 19.5 | — | — |
| head | obr_pmd_nov2025:23637:8623dae9cc846018 (row 23637) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Other AME (current) | -83.0 | — | — |
| head | obr_pmd_nov2025:23643:ca6ac37cb3f11ea1 (row 23643) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSGI in CDEL | 1,589.8 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__rebuilding_britain_capital_investment --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__rebuilding_britain_capital_investment_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
