# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12228:d38b159485d898ff | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12234:c1382507c39ee980 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12240:c7bffab29c5d6353 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12246:887dab1e9725d45f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23909:f351a5ac1519fcec | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23915:48461770cb90e722 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23921:a7d689d3b547d3a5 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12228:d38b159485d898ff (row 12228) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12234:c1382507c39ee980 (row 12234) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12240:c7bffab29c5d6353 (row 12240) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12246:887dab1e9725d45f (row 12246) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:23909:f351a5ac1519fcec (row 23909) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23915:48461770cb90e722 (row 23915) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:23921:a7d689d3b547d3a5 (row 23921) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2025.json` (sha256 `0846b7d52bccd0f2167d1df74e56fec869455e1dcc8c1f4ac06a26f69ac61930`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
