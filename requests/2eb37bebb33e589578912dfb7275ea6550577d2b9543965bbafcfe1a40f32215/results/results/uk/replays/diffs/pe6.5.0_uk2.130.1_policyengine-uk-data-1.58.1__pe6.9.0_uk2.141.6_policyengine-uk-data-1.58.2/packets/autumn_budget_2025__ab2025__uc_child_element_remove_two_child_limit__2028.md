# Investigation packet: autumn_budget_2025 / ab2025__uc_child_element_remove_two_child_limit / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23528:35553a766a3ad3d3 | -3,154.8 | -3,203.9 | -49.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23534:b80fd366f320caa3 | — | — | — | — | — |
| measure_year | total | -3,154.8 | -3,203.9 | -49.1 | numerical | move_above_threshold |
| head | universal_credit | -3,154.8 | -3,203.9 | -49.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23528:35553a766a3ad3d3 (row 23528) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -2,325.3 | -3,154.8 | -3,203.9 |
| base | obr_pmd_nov2025:23534:b80fd366f320caa3 (row 23534) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -490.0 | — | — |
| head | obr_pmd_nov2025:23528:35553a766a3ad3d3 (row 23528) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -2,325.3 | -3,154.8 | -3,203.9 |
| head | obr_pmd_nov2025:23534:b80fd366f320caa3 (row 23534) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -490.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028.json` (sha256 `ea23b96a04e4b65d93138385d125fdf8de00b0a7b413118669f17d1dd03fb1ab`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028.json` (sha256 `042ca7a040d313db3ba05cdb3b4f6492186569d95ef956f87af9b4146935cf50`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.child.limit.child_count": {"2026-01-01.2030-12-31": 2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__uc_child_element_remove_two_child_limit --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.6_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
