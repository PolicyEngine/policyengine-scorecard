# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12257:95f2605d4a114c10 | -306.9 | -308.5 | -1.6 | — | — |
| source_row | obr_pmd_nov2025:12263:b231bc602cc23fb2 | 1,108.4 | 1,087.3 | -21.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23932:941cef215b41c2c1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23938:58dc61511eb5ce88 | — | — | — | — | — |
| measure_year | total | 801.5 | 778.8 | -22.7 | numerical | move_above_threshold |
| head | income_tax | -306.9 | -308.5 | -1.6 | — | — |
| head | ni_class_1_employee | -69.4 | -65.8 | 3.6 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,177.7 | 1,153.0 | -24.7 | numerical | move_above_threshold |
| head | ni_class_4 | 0.1 | 0.1 | 0.1 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | -306.9 | -308.5 |
| base | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | 1,108.4 | 1,087.3 |
| base | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| base | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| base | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |
| head | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | -306.9 | -308.5 |
| head | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | 1,108.4 | 1,087.3 |
| head | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| head | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| head | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `01ee8b562c5bc99f73919d87a603a4deed0b287614756bcc1acb9a433168a749`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `027f70469cc96651d727b3d59dc1b0156b91fa8e354a1c1aaf85b47f79b2b970`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
