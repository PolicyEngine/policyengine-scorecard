# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12257:95f2605d4a114c10 | -299.7 | -295.1 | 4.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12263:b231bc602cc23fb2 | 1,069.5 | 1,017.0 | -52.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23932:941cef215b41c2c1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23938:58dc61511eb5ce88 | — | — | — | — | — |
| measure_year | total | 769.8 | 721.9 | -47.9 | numerical | move_above_threshold |
| head | income_tax | -299.7 | -295.1 | 4.6 | numerical | move_above_threshold |
| head | ni_class_1_employee | -63.8 | -62.0 | 1.8 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,133.2 | 1,079.0 | -54.3 | numerical | move_above_threshold |
| head | ni_class_4 | 0.1 | 0.0 | -0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | -299.7 | -295.1 |
| base | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | 1,069.5 | 1,017.0 |
| base | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| base | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| base | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |
| head | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | -299.7 | -295.1 |
| head | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | 1,069.5 | 1,017.0 |
| head | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| head | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| head | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `29534f970563521ad760d5129f5c502884bb28b223bff40f2172909498873395`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `201edf5dfbd018417f084dbc7c702382014dfccd89d3f4929c9f061e7716e4ad`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
