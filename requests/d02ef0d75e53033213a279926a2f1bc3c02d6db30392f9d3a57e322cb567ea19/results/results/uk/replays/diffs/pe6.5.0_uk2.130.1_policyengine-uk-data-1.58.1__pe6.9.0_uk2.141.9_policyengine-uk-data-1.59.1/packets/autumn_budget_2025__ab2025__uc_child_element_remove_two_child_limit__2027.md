# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23527:76270d3c75a7a426 | -2,958.4 | -2,989.5 | -31.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23533:536f90f4ea5cecc8 | — | — | — | — | — |
| measure_year | total | -2,958.4 | -2,989.5 | -31.1 | numerical | move_above_threshold |
| head | universal_credit | -2,958.4 | -2,989.5 | -31.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23527:76270d3c75a7a426 (row 23527) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -2,101.0 | -2,958.4 | -2,989.5 |
| base | obr_pmd_nov2025:23533:536f90f4ea5cecc8 (row 23533) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -489.0 | — | — |
| head | obr_pmd_nov2025:23527:76270d3c75a7a426 (row 23527) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -2,101.0 | -2,958.4 | -2,989.5 |
| head | obr_pmd_nov2025:23533:536f90f4ea5cecc8 (row 23533) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -489.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027.json` (sha256 `c08f9c5853d9732127a07ade3c2ae4c7c01bbe983ff54c5530f465664095037f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027.json` (sha256 `7447874808d511fae9198a7dd87f428d28183be4da34c3096899ba065b300388`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
