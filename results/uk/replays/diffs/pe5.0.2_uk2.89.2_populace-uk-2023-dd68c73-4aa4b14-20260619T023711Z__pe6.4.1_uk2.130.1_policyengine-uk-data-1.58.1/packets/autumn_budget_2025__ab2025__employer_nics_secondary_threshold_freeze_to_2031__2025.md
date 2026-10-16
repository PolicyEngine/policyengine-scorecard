# Investigation packet: autumn_budget_2025 / ab2025__employer_nics_secondary_threshold_freeze_to_2031 / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12252:01dfc28b448fefc1 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12258:bd30009d1602f503 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12264:01126fa86255d2bc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23927:fd1d4891f4b64585 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23933:dbb15db7e903a265 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12252:01dfc28b448fefc1 (row 12252) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12258:bd30009d1602f503 (row 12258) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12264:01126fa86255d2bc (row 12264) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:23927:fd1d4891f4b64585 (row 23927) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23933:dbb15db7e903a265 (row 23933) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2025.json` (sha256 `80cb85f4605403d0950d8fb314704ade05096a1e12d0a1788febba16a7d46aa3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2028-01-01.2028-12-31": 97.9199086029823, "2029-01-01.2029-12-31": 99.8780897071249, "2030-01-01.2030-12-31": 101.875685775149}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
