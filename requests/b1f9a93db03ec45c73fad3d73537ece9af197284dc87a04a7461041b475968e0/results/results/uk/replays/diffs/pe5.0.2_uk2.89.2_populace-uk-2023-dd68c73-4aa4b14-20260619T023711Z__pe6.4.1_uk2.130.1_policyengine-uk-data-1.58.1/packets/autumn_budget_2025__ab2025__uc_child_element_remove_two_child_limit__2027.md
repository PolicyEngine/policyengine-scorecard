# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23527:76270d3c75a7a426 | — | -2,958.4 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23533:536f90f4ea5cecc8 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | -2,958.4 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:23527:76270d3c75a7a426 (row 23527) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -2,101.0 | — | -2,958.4 |
| head | obr_pmd_nov2025:23533:536f90f4ea5cecc8 (row 23533) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -489.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027.json` (sha256 `bff0cd7a78cc5885e01073b30c9964b46b1938f0029544a3f64199bfe054bd63`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
