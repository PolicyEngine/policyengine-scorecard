# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23528:35553a766a3ad3d3 | -2,869.7 | -2,918.6 | -48.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23534:b80fd366f320caa3 | — | — | — | — | — |
| measure_year | total | -2,869.7 | -2,918.6 | -48.9 | numerical | move_above_threshold |
| head | universal_credit | -2,869.7 | -2,918.6 | -48.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23528:35553a766a3ad3d3 (row 23528) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -2,325.3 | -2,869.7 | -2,918.6 |
| base | obr_pmd_nov2025:23534:b80fd366f320caa3 (row 23534) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -490.0 | — | — |
| head | obr_pmd_nov2025:23528:35553a766a3ad3d3 (row 23528) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -2,325.3 | -2,869.7 | -2,918.6 |
| head | obr_pmd_nov2025:23534:b80fd366f320caa3 (row 23534) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -490.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028.json` (sha256 `05698027e4c901071fb0ee57e9ed5769b5e13964024beebb90df4d7bb83c549c`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028.json` (sha256 `7da9a068031ca079debb940d1917771eb95132da951c6e469cb774af60c3cf15`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
