# Investigation packet: autumn_budget_2025 / ab2025__jobs_and_skills_youth_guarantee_and_levy / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Jobs and Skills: Invest in Youth Guarantee, Growth and Skills Levy, and employment & skills support
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23719:4b2770afecb31b76 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23725:9ba7404b8ef23bde | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23719:4b2770afecb31b76 (row 23719) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -601.0 | — | — |
| head | obr_pmd_nov2025:23725:9ba7404b8ef23bde (row 23725) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | 45.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__jobs_and_skills_youth_guarantee_and_levy --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__jobs_and_skills_youth_guarantee_and_levy_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
