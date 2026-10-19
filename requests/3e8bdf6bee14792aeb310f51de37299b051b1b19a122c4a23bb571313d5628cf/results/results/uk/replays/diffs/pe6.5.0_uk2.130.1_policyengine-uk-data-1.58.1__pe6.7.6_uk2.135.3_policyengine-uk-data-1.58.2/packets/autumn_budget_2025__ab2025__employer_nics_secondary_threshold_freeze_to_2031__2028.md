# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.135.3_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12255:0fd29e509efbba1c | -92.0 | -90.4 | 1.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12261:317b60a83974bf6d | 338.8 | 339.4 | 0.6 | — | — |
| source_row | obr_pmd_nov2025:12267:3fa6651a965d1925 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23936:7895cd012b6c00fc | — | — | — | — | — |
| measure_year | total | 246.8 | 249.0 | 2.1 | — | — |
| head | income_tax | -92.0 | -90.4 | 1.6 | numerical | move_above_threshold |
| head | ni_class_1_employee | -21.4 | -21.5 | -0.1 | — | — |
| head | ni_class_1_employer | 360.2 | 360.8 | 0.6 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | -0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12255:0fd29e509efbba1c (row 12255) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -75.4 | -92.0 | -90.4 |
| base | obr_pmd_nov2025:12261:317b60a83974bf6d (row 12261) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 398.3 | 338.8 | 339.4 |
| base | obr_pmd_nov2025:12267:3fa6651a965d1925 (row 12267) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -28.0 | — | — |
| base | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 (row 23930) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.8 | — | — |
| base | obr_pmd_nov2025:23936:7895cd012b6c00fc (row 23936) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -5.2 | — | — |
| head | obr_pmd_nov2025:12255:0fd29e509efbba1c (row 12255) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -75.4 | -92.0 | -90.4 |
| head | obr_pmd_nov2025:12261:317b60a83974bf6d (row 12261) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 398.3 | 338.8 | 339.4 |
| head | obr_pmd_nov2025:12267:3fa6651a965d1925 (row 12267) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -28.0 | — | — |
| head | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 (row 23930) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.8 | — | — |
| head | obr_pmd_nov2025:23936:7895cd012b6c00fc (row 23936) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -5.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028.json` (sha256 `131bb44120ca18f85773d609f9afddb397164f9311effd3877d92b37a0c17087`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.135.3_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028.json` (sha256 `6a30df62c38c593d2dfd5187e98cfc914d412028e3660ebc79dbc40f2458670b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.7.6_uk2.135.3_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.135.3_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
