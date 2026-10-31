# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23526:7a52217d035becaf | -2,317.0 | -2,242.1 | 74.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23532:a4b6c3164622eec3 | — | — | — | — | — |
| measure_year | total | -2,317.0 | -2,242.1 | 74.9 | numerical | move_above_threshold |
| head | universal_credit | -2,317.0 | -2,242.1 | 74.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23526:7a52217d035becaf (row 23526) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,886.7 | -2,317.0 | -2,242.1 |
| base | obr_pmd_nov2025:23532:a4b6c3164622eec3 (row 23532) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -480.0 | — | — |
| head | obr_pmd_nov2025:23526:7a52217d035becaf (row 23526) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,886.7 | -2,317.0 | -2,242.1 |
| head | obr_pmd_nov2025:23532:a4b6c3164622eec3 (row 23532) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -480.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026.json` (sha256 `d900a0065302c9f6ecf10fceb82e208019338dd8e65a77e32a370af8fd06498f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026.json` (sha256 `8cb2a47810867e9cb67923601f76b1757c4148c14b044dc0a9ceeab272e7ff3f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
