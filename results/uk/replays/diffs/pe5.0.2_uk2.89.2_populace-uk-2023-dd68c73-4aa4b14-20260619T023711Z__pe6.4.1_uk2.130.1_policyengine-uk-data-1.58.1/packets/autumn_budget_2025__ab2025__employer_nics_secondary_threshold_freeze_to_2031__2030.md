# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12257:95f2605d4a114c10 | — | -306.9 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12263:b231bc602cc23fb2 | — | 1,108.4 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23932:941cef215b41c2c1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23938:58dc61511eb5ce88 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 801.5 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12257:95f2605d4a114c10 (row 12257) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | -237.9 | — | -306.9 |
| head | obr_pmd_nov2025:12263:b231bc602cc23fb2 (row 12263) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 1,253.4 | — | 1,108.4 |
| head | obr_pmd_nov2025:12269:ac8484e9d2d62ab4 (row 12269) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -69.6 | — | — |
| head | obr_pmd_nov2025:23932:941cef215b41c2c1 (row 23932) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | -2.5 | — | — |
| head | obr_pmd_nov2025:23938:58dc61511eb5ce88 (row 23938) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | -16.2 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030.json` (sha256 `ab9f1e2388a68bbbaba9f34a18927587a8282627df0d91f8bf46905e0515157e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
