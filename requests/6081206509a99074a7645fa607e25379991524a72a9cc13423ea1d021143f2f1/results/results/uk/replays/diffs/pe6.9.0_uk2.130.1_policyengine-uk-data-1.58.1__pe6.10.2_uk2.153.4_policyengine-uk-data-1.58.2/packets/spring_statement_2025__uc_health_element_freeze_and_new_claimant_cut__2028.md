# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical, construction
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23319:c6ce8500db20415e | 1,053.0 | 860.0 | -193.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23325:2a220260e99cd7fb | — | — | — | — | — |
| measure_year | total | 1,053.0 | 860.0 | -193.1 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | 1,053.0 | 860.0 | -193.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23319:c6ce8500db20415e (row 23319) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 2,328.4 | 1,053.0 | 860.0 |
| base | obr_pmd_nov2025:23325:2a220260e99cd7fb (row 23325) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -33.9 | — | — |
| head | obr_pmd_nov2025:23319:c6ce8500db20415e (row 23319) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 2,328.4 | 1,053.0 | 860.0 |
| head | obr_pmd_nov2025:23325:2a220260e99cd7fb (row 23325) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -33.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028.json` (sha256 `18cfad656705c8ea7b6fc99e740f84373639e8fe7ea20117754edfbe22d86935`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028.json` (sha256 `18cc3c52367f054c09cf40575812762772c79fa0576d20147cb7534a42f0d11a`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
