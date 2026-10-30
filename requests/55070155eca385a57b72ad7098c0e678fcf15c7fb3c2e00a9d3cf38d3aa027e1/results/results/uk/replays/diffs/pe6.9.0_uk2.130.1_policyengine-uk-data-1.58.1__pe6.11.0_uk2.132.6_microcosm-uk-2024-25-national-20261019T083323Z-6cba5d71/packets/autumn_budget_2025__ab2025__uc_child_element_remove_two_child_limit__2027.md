# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23527:76270d3c75a7a426 | -2,958.4 | -2,510.4 | 448.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23533:536f90f4ea5cecc8 | — | — | — | — | — |
| measure_year | total | -2,958.4 | -2,510.4 | 448.1 | numerical | move_above_threshold |
| head | universal_credit | -2,958.4 | -2,510.4 | 448.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23527:76270d3c75a7a426 (row 23527) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -2,101.0 | -2,958.4 | -2,510.4 |
| base | obr_pmd_nov2025:23533:536f90f4ea5cecc8 (row 23533) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -489.0 | — | — |
| head | obr_pmd_nov2025:23527:76270d3c75a7a426 (row 23527) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -2,101.0 | -2,958.4 | -2,510.4 |
| head | obr_pmd_nov2025:23533:536f90f4ea5cecc8 (row 23533) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -489.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027.json` (sha256 `549672f778268216fd773a05837e686431b71e86743635c0eb195f662eb3e2a2`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027.json` (sha256 `bb2360e23f815567196d5d58cb6ea740cd14df268a40c52f6aadd9c6270bbf4e`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
