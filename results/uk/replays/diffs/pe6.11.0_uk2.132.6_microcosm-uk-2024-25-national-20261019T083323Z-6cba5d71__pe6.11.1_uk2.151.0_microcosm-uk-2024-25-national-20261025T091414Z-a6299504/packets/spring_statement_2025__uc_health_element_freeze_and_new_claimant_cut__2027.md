# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23318:dcc529f309fec572 | 931.4 | 872.1 | -59.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23324:9399b2f27fbfd06e | — | — | — | — | — |
| measure_year | total | 931.4 | 872.1 | -59.4 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | 931.4 | 872.1 | -59.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23318:dcc529f309fec572 (row 23318) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,555.7 | 931.4 | 872.1 |
| base | obr_pmd_nov2025:23324:9399b2f27fbfd06e (row 23324) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -22.3 | — | — |
| head | obr_pmd_nov2025:23318:dcc529f309fec572 (row 23318) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 1,555.7 | 931.4 | 872.1 |
| head | obr_pmd_nov2025:23324:9399b2f27fbfd06e (row 23324) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -22.3 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027.json` (sha256 `3f05122f233b5dcbd0b7c6ed33518e6b13d31405c6654f7e741c67fbeb4e6739`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027.json` (sha256 `463ae12533fe4dc7a25706e7802d2c9ef2c82f9aaed82f1ce0f811d6a6be80b3`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
