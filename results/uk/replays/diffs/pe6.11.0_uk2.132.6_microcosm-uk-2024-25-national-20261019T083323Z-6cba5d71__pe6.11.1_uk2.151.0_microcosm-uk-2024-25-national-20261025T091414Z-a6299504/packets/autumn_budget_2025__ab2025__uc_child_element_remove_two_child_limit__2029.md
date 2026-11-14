# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23529:1e1a237caba88918 | -3,187.0 | -3,323.9 | -136.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23535:0e2f301b9e5ffadd | — | — | — | — | — |
| measure_year | total | -3,187.0 | -3,323.9 | -136.9 | numerical | move_above_threshold |
| head | universal_credit | -3,187.0 | -3,323.9 | -136.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23529:1e1a237caba88918 (row 23529) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -2,570.3 | -3,187.0 | -3,323.9 |
| base | obr_pmd_nov2025:23535:0e2f301b9e5ffadd (row 23535) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare outside cap | -525.0 | — | — |
| head | obr_pmd_nov2025:23529:1e1a237caba88918 (row 23529) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -2,570.3 | -3,187.0 | -3,323.9 |
| head | obr_pmd_nov2025:23535:0e2f301b9e5ffadd (row 23535) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare outside cap | -525.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029.json` (sha256 `7c61bd86662af24fb40f7dd39608a132e780b6bd6a908fbf2bad8aad67845896`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029.json` (sha256 `94120efa5e155c10313828ce9f922d6dc8e501547734eb45a1c81809c8cf05fb`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
