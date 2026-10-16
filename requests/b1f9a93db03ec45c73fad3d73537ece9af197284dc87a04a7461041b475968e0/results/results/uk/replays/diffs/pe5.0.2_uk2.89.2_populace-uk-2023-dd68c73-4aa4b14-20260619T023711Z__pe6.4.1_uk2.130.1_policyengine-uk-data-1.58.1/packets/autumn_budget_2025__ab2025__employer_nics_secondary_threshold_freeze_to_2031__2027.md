# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12254:ef6f52eac5c45f4c | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12260:031335b5b668d66d | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12266:7a64c8990aba6f05 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23929:aafd70576a3c0984 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23935:51075e3dc2ea22d1 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12254:ef6f52eac5c45f4c (row 12254) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12260:031335b5b668d66d (row 12260) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12266:7a64c8990aba6f05 (row 12266) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -3.3 | — | — |
| head | obr_pmd_nov2025:23929:aafd70576a3c0984 (row 23929) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23935:51075e3dc2ea22d1 (row 23935) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2027.json` (sha256 `06e5e28723848dc6c659428994e75f4161f4ebe0b855e95e958bfcf1b0f57cb8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
