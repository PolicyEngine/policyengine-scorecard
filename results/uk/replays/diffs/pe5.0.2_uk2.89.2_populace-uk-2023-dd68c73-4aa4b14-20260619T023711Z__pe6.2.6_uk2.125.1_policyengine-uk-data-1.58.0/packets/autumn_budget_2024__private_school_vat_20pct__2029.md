# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11621:8bf103a18fecf781 | 1,388.0 | 2,166.5 | 778.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11627:37d39a5448ffd160 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f | — | — | — | — | — |
| measure_year | total | 1,388.0 | 2,166.5 | 778.5 | numerical | move_above_threshold |
| head | private_school_vat | 1,388.0 | 2,166.5 | 778.5 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11621:8bf103a18fecf781 (row 11621) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT | 1,726.5 | 1,388.0 | 2,166.5 |
| obr_pmd_nov2025:11627:37d39a5448ffd160 (row 11627) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | 484.0 | — | — |
| obr_pmd_nov2025:22786:b2bc03d5bfd19f7f (row 22786) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | -484.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029.json` (sha256 `9b65d6ba9924f83a3fd6f37f834a2dd916d8664ada6a817a9cd09f5e1f6627ed`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029.json` (sha256 `87518b57b1311ecaf75350cf3396f9dc64e5ae3fe0a842a0874daae675f51271`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__private_school_vat_20pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__private_school_vat_20pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
