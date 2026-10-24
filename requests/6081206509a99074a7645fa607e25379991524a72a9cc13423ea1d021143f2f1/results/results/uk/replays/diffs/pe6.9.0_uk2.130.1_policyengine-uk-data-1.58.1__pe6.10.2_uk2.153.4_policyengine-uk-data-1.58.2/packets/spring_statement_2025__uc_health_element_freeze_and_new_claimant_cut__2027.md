# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical, construction
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23318:dcc529f309fec572 | 893.6 | 712.8 | -180.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23324:9399b2f27fbfd06e | — | — | — | — | — |
| measure_year | total | 893.6 | 712.8 | -180.8 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | 893.6 | 712.8 | -180.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23318:dcc529f309fec572 (row 23318) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,555.7 | 893.6 | 712.8 |
| base | obr_pmd_nov2025:23324:9399b2f27fbfd06e (row 23324) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -22.3 | — | — |
| head | obr_pmd_nov2025:23318:dcc529f309fec572 (row 23318) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,555.7 | 893.6 | 712.8 |
| head | obr_pmd_nov2025:23324:9399b2f27fbfd06e (row 23324) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -22.3 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027.json` (sha256 `23c1669e3b8e98547c7c4610069be4d0cdc9ba7dbb5a0f567766f1967b914b5d`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027.json` (sha256 `1b3f3cf4652a9f89146af12c4f1db89d92c3c0a8ee27e95cfcb9197fb0f49d88`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
