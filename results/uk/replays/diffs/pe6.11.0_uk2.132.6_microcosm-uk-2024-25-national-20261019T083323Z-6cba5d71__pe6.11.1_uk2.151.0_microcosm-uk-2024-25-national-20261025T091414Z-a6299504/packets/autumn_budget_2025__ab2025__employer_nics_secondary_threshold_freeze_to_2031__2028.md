# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12255:0fd29e509efbba1c | -90.7 | -88.6 | 2.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12261:317b60a83974bf6d | 332.2 | 326.7 | -5.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12267:3fa6651a965d1925 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23936:7895cd012b6c00fc | — | — | — | — | — |
| measure_year | total | 241.4 | 238.0 | -3.4 | numerical | move_above_threshold |
| head | income_tax | -90.7 | -88.6 | 2.1 | numerical | move_above_threshold |
| head | ni_class_1_employee | -20.4 | -19.8 | 0.6 | — | — |
| head | ni_class_1_employer | 352.5 | 346.5 | -6.0 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | -0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12255:0fd29e509efbba1c (row 12255) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -75.4 | -90.7 | -88.6 |
| base | obr_pmd_nov2025:12261:317b60a83974bf6d (row 12261) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 398.3 | 332.2 | 326.7 |
| base | obr_pmd_nov2025:12267:3fa6651a965d1925 (row 12267) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -28.0 | — | — |
| base | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 (row 23930) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.8 | — | — |
| base | obr_pmd_nov2025:23936:7895cd012b6c00fc (row 23936) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -5.2 | — | — |
| head | obr_pmd_nov2025:12255:0fd29e509efbba1c (row 12255) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -75.4 | -90.7 | -88.6 |
| head | obr_pmd_nov2025:12261:317b60a83974bf6d (row 12261) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 398.3 | 332.2 | 326.7 |
| head | obr_pmd_nov2025:12267:3fa6651a965d1925 (row 12267) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -28.0 | — | — |
| head | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 (row 23930) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.8 | — | — |
| head | obr_pmd_nov2025:23936:7895cd012b6c00fc (row 23936) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -5.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028.json` (sha256 `cb2d7f023b6a3a9d82b51e8de8cd3eafe7b65e46478168a85646c248471ca4b0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028.json` (sha256 `643b4231a8f71e4fc8bc7b921c2fc6785b47e0e4fb82e92a1790b29daeb179b4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
