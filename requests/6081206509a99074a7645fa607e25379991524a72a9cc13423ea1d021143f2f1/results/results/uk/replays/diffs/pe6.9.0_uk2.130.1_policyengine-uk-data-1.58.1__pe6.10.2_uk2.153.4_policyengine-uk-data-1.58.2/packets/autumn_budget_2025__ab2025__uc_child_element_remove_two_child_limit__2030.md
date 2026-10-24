# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23530:d1bc796d9f235c4f | -3,488.2 | -3,599.0 | -110.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23536:b082924fa31ed31d | — | — | — | — | — |
| measure_year | total | -3,488.2 | -3,599.0 | -110.8 | numerical | move_above_threshold |
| head | universal_credit | -3,488.2 | -3,599.0 | -110.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23530:d1bc796d9f235c4f (row 23530) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -2,684.9 | -3,488.2 | -3,599.0 |
| base | obr_pmd_nov2025:23536:b082924fa31ed31d (row 23536) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare outside cap | -550.0 | — | — |
| head | obr_pmd_nov2025:23530:d1bc796d9f235c4f (row 23530) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -2,684.9 | -3,488.2 | -3,599.0 |
| head | obr_pmd_nov2025:23536:b082924fa31ed31d (row 23536) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare outside cap | -550.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030.json` (sha256 `5d604f96a5f4930929f03042a7678112516baddb5744a5304bbdfb00d583a4b3`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030.json` (sha256 `5bb55009812e6cff220a796d5ac0cf822671578e9c028d9756f4666faad9751e`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
