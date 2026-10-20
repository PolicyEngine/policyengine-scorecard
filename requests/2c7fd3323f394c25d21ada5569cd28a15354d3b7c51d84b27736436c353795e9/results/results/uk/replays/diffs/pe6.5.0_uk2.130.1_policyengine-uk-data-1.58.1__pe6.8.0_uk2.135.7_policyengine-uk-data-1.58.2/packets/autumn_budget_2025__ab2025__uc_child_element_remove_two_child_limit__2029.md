# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.135.7_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23529:1e1a237caba88918 | -3,259.2 | -3,298.6 | -39.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23535:0e2f301b9e5ffadd | — | — | — | — | — |
| measure_year | total | -3,259.2 | -3,298.6 | -39.4 | numerical | move_above_threshold |
| head | universal_credit | -3,259.2 | -3,298.6 | -39.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23529:1e1a237caba88918 (row 23529) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -2,570.3 | -3,259.2 | -3,298.6 |
| base | obr_pmd_nov2025:23535:0e2f301b9e5ffadd (row 23535) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare outside cap | -525.0 | — | — |
| head | obr_pmd_nov2025:23529:1e1a237caba88918 (row 23529) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -2,570.3 | -3,259.2 | -3,298.6 |
| head | obr_pmd_nov2025:23535:0e2f301b9e5ffadd (row 23535) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare outside cap | -525.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029.json` (sha256 `01d8330f2277aebd78f1230393923e3a12ec9305f5f7669e0b56cb0ad05e4831`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.135.7_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029.json` (sha256 `c9a6e1f0733a19db6905c492f7e3149402d2d2737337dd88f250078d73f3bc48`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.8.0_uk2.135.7_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.135.7_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
