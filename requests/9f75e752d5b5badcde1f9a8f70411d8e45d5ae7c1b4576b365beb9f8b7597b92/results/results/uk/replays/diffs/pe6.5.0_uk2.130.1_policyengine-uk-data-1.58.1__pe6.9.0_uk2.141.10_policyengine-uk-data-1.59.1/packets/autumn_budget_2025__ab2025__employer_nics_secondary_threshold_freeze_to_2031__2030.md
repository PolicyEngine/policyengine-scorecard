# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12257:95f2605d4a114c10 | -306.9 | -315.7 | -8.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12263:b231bc602cc23fb2 | 1,108.4 | 1,136.8 | 28.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23932:941cef215b41c2c1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23938:58dc61511eb5ce88 | — | — | — | — | — |
| measure_year | total | 801.5 | 821.2 | 19.7 | numerical | move_above_threshold |
| head | income_tax | -306.9 | -315.7 | -8.7 | numerical | move_above_threshold |
| head | ni_class_1_employee | -69.4 | -70.9 | -1.6 | numerical | move_above_threshold |
| head | ni_class_1_employer | 1,177.7 | 1,207.7 | 29.9 | numerical | move_above_threshold |
| head | ni_class_4 | 0.1 | 0.1 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | -306.9 | -315.7 |
| base | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | 1,108.4 | 1,136.8 |
| base | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| base | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| base | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |
| head | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | -306.9 | -315.7 |
| head | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | 1,108.4 | 1,136.8 |
| head | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| head | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| head | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `babc11b6362cc432478abc658cda971494bdccf10e12d8114f30212343f2da08`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `b602fa0ba30dcef562f123ba51d5ba28b66e5901382279d91b5ee73095f5aefb`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
