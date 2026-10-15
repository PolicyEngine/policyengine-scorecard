# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical, structural, inertness
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23318:dcc529f309fec572 | 338.6 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:23324:9399b2f27fbfd06e | — | — | — | — | — |
| measure_year | total | 338.6 | 0.0 | -338.6 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | universal_credit | 338.6 | -0.0 | -338.6 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23318:dcc529f309fec572 (row 23318) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,555.7 | 338.6 | — |
| base | obr_pmd_nov2025:23324:9399b2f27fbfd06e (row 23324) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -22.3 | — | — |
| head | obr_pmd_nov2025:23318:dcc529f309fec572 (row 23318) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,555.7 | 338.6 | — |
| head | obr_pmd_nov2025:23324:9399b2f27fbfd06e (row 23324) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -22.3 | — | — |

## Executed worlds

* base: `results/uk/events/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027.json` (sha256 `e4498a6ffb5ce844af7ccb47c3e7d25d8b2458f098a3a97b7b9998391931155b`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027.json` (sha256 `f3d8f3108e1dfb84f1e7ff8814487bae82a2b0a3f071b0e6d3fd15539a01bb40`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
