# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23526:7a52217d035becaf | -2,242.1 | -2,329.1 | -87.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23532:a4b6c3164622eec3 | — | — | — | — | — |
| measure_year | total | -2,242.1 | -2,329.1 | -87.0 | numerical | move_above_threshold |
| head | universal_credit | -2,242.1 | -2,329.1 | -87.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23526:7a52217d035becaf (row 23526) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,886.7 | -2,242.1 | -2,329.1 |
| base | obr_pmd_nov2025:23532:a4b6c3164622eec3 (row 23532) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -480.0 | — | — |
| head | obr_pmd_nov2025:23526:7a52217d035becaf (row 23526) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,886.7 | -2,242.1 | -2,329.1 |
| head | obr_pmd_nov2025:23532:a4b6c3164622eec3 (row 23532) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -480.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026.json` (sha256 `06efd524c119a3ff0ba993d52be56872b5b2f9891cbc3800724c001e4ff480bc`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026.json` (sha256 `b6150f7bcac0ffa0154d513dae0962a494e4295b56464b7b1c29341955a64349`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
