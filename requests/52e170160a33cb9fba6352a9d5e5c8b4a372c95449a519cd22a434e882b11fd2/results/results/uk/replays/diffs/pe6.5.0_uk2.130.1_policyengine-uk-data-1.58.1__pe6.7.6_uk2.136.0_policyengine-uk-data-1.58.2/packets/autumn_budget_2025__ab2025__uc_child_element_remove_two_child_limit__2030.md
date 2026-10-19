# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23530:d1bc796d9f235c4f | -3,488.2 | -3,562.3 | -74.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23536:b082924fa31ed31d | — | — | — | — | — |
| measure_year | total | -3,488.2 | -3,562.3 | -74.1 | numerical | move_above_threshold |
| head | universal_credit | -3,488.2 | -3,562.3 | -74.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23530:d1bc796d9f235c4f (row 23530) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -2,684.9 | -3,488.2 | -3,562.3 |
| base | obr_pmd_nov2025:23536:b082924fa31ed31d (row 23536) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare outside cap | -550.0 | — | — |
| head | obr_pmd_nov2025:23530:d1bc796d9f235c4f (row 23530) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -2,684.9 | -3,488.2 | -3,562.3 |
| head | obr_pmd_nov2025:23536:b082924fa31ed31d (row 23536) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare outside cap | -550.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030.json` (sha256 `52c3a072f9c637d1a65ecc1b8002b860e752e57cb5a3ac6781581a231ff2d503`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030.json` (sha256 `5c1b36217eadb4c972369bed0011761d575c7e8b591b9e83cbb9ae2bb6a22f49`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
