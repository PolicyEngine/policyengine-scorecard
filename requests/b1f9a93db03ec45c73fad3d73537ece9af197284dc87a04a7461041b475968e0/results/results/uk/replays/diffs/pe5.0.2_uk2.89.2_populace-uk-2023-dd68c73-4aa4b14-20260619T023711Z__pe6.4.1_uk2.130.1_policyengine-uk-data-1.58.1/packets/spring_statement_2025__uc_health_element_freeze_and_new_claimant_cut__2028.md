# Investigation packet: spring_statement_2025 / spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:23319:c6ce8500db20415e | 436.3 | 1,053.0 | 616.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23325:2a220260e99cd7fb | — | — | — | — | — |
| measure_year | total | 436.3 | 1,053.0 | 616.7 | numerical | move_above_threshold |
| head | universal_credit | 436.3 | 1,053.0 | 616.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:23319:c6ce8500db20415e (row 23319) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 2,328.4 | 436.3 | 1,053.0 |
| base | obr_pmd_nov2025:23325:2a220260e99cd7fb (row 23325) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -33.9 | — | — |
| head | obr_pmd_nov2025:23319:c6ce8500db20415e (row 23319) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 2,328.4 | 436.3 | 1,053.0 |
| head | obr_pmd_nov2025:23325:2a220260e99cd7fb (row 23325) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -33.9 | — | — |

## Executed worlds

* base: `results/uk/events/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028.json` (sha256 `8c9a16f8cca31e1db7053077f2b58c35463f53038e95096ab4a439f44c446086`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028.json` (sha256 `d98649c2a60fe36a3bc2a4836ef61fdb27fdc58e232fcac660c43be8488f9a09`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.rebalancing.new_claimant_health_element": {"2026-01-01.2026-12-31": 437.66, "2027-01-01.2027-12-31": 447.73, "2028-01-01.2028-12-31": 456.68, "2029-01-01.2029-12-31": 465.81}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_statement_2025_measures.json --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
