# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12255:0fd29e509efbba1c | — | -92.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12261:317b60a83974bf6d | — | 338.8 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12267:3fa6651a965d1925 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23936:7895cd012b6c00fc | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 246.8 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12255:0fd29e509efbba1c (row 12255) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -75.4 | — | -92.0 |
| head | obr_pmd_nov2025:12261:317b60a83974bf6d (row 12261) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 398.3 | — | 338.8 |
| head | obr_pmd_nov2025:12267:3fa6651a965d1925 (row 12267) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -28.0 | — | — |
| head | obr_pmd_nov2025:23930:c7e38b0a5a00d8e8 (row 23930) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -0.8 | — | — |
| head | obr_pmd_nov2025:23936:7895cd012b6c00fc (row 23936) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -5.2 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028.json` (sha256 `48f1a3ddc2fd8677869f4eab0eba28788ec0b865e1dbf0129a6a38147e6f7cdb`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
