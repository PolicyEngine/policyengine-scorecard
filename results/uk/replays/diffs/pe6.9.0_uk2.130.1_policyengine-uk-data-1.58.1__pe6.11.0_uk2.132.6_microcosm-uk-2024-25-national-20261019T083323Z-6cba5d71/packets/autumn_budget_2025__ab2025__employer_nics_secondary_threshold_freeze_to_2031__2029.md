# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12256:5509231f1d1fc426 | -196.1 | -195.6 | 0.5 | — | — |
| source_row | obr_pmd_nov2025:12262:370b9fb9250ec360 | 717.7 | 704.1 | -13.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12268:45f83bc0d782b97e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23931:d6cf2bc3c72ca4fe | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23937:c6309c507e442578 | — | — | — | — | — |
| measure_year | total | 521.6 | 508.4 | -13.2 | numerical | move_above_threshold |
| head | income_tax | -196.1 | -195.6 | 0.5 | — | — |
| head | ni_class_1_employee | -45.3 | -42.8 | 2.6 | numerical | move_above_threshold |
| head | ni_class_1_employer | 763.0 | 746.7 | -16.2 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.1 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12256:5509231f1d1fc426 (row 12256) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -159.9 | -196.1 | -195.6 |
| base | obr_pmd_nov2025:12262:370b9fb9250ec360 (row 12262) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 842.9 | 717.7 | 704.1 |
| base | obr_pmd_nov2025:12268:45f83bc0d782b97e (row 12268) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -54.8 | — | — |
| base | obr_pmd_nov2025:23931:d6cf2bc3c72ca4fe (row 23931) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -1.7 | — | — |
| base | obr_pmd_nov2025:23937:c6309c507e442578 (row 23937) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -10.9 | — | — |
| head | obr_pmd_nov2025:12256:5509231f1d1fc426 (row 12256) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -159.9 | -196.1 | -195.6 |
| head | obr_pmd_nov2025:12262:370b9fb9250ec360 (row 12262) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 842.9 | 717.7 | 704.1 |
| head | obr_pmd_nov2025:12268:45f83bc0d782b97e (row 12268) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -54.8 | — | — |
| head | obr_pmd_nov2025:23931:d6cf2bc3c72ca4fe (row 23931) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -1.7 | — | — |
| head | obr_pmd_nov2025:23937:c6309c507e442578 (row 23937) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -10.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2029.json` (sha256 `e19e0ba54ee534ffe7e2e1035a777bd6fd9f440cacc109df09d849b649b774d0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2029.json` (sha256 `778fedfccb6b064aa683567f995fe8a01b98a56d3285d629170d2385fe6a11aa`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
