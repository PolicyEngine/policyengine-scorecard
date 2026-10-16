# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12253:a700821a34d41059 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12259:ce036213afa1446d | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12265:97c092709106c98c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23928:07dd6734916f0277 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23934:f457b3519ddeeba0 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12253:a700821a34d41059 (row 12253) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12259:ce036213afa1446d (row 12259) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12265:97c092709106c98c (row 12265) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:23928:07dd6734916f0277 (row 23928) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23934:f457b3519ddeeba0 (row 23934) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2026.json` (sha256 `cd86d8dd6df1c8accd57af17dc24fe33630d8a3e1b5ff863ab7ae30de9af4678`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
