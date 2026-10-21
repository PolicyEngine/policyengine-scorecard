# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.5_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23526:7a52217d035becaf | -2,694.6 | -2,765.4 | -70.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23532:a4b6c3164622eec3 | — | — | — | — | — |
| measure_year | total | -2,694.6 | -2,765.4 | -70.8 | numerical | move_above_threshold |
| head | universal_credit | -2,694.6 | -2,765.4 | -70.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23526:7a52217d035becaf (row 23526) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,886.7 | -2,694.6 | -2,765.4 |
| base | obr_pmd_nov2025:23532:a4b6c3164622eec3 (row 23532) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -480.0 | — | — |
| head | obr_pmd_nov2025:23526:7a52217d035becaf (row 23526) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -1,886.7 | -2,694.6 | -2,765.4 |
| head | obr_pmd_nov2025:23532:a4b6c3164622eec3 (row 23532) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare outside cap | -480.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026.json` (sha256 `0fc939904ae76f5e4571fe49eee94209b53f7968778c7c2b61b831638271f6dd`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.5_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026.json` (sha256 `32b4e463b82af0500f7cd831957dc750523eb258e16363863c47831a88d36741`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.5_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.5_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
