# Investigation packet: autumn_budget_2025 / ab2025__jobs_and_skills_youth_guarantee_and_levy / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Jobs and Skills: Invest in Youth Guarantee, Growth and Skills Levy, and employment & skills support
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23722:556e8bfde8f740cc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23728:e9247389f9eefabf | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23722:556e8bfde8f740cc (row 23722) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -156.9 | — | — |
| head | obr_pmd_nov2025:23728:e9247389f9eefabf (row 23728) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare outside cap | 50.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__jobs_and_skills_youth_guarantee_and_levy --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__jobs_and_skills_youth_guarantee_and_levy_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
