# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12367:5e598a525ced2676 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12373:b35120d1508528b3 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12379:d28baa0990b9606c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12385:6b9810c9f16cf4ae | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23988:9b2cf5b18d7783e5 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23994:a1ecc5a04cd0ab9e | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12367:5e598a525ced2676 (row 12367) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | -31.8 | — | — |
| head | obr_pmd_nov2025:12373:b35120d1508528b3 (row 12373) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | High-value council tax surcharge | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12379:d28baa0990b9606c (row 12379) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | -3.6 | — | — |
| head | obr_pmd_nov2025:12385:6b9810c9f16cf4ae (row 12385) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | -79.9 | — | — |
| head | obr_pmd_nov2025:23988:9b2cf5b18d7783e5 (row 23988) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -1.6 | — | — |
| head | obr_pmd_nov2025:23994:a1ecc5a04cd0ab9e (row 23994) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -3.7 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2026.json` (sha256 `9d62695f58da4c3fd40c0b9e78f3bd2bb46926c654636e5f54cc1f306e11acba`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
