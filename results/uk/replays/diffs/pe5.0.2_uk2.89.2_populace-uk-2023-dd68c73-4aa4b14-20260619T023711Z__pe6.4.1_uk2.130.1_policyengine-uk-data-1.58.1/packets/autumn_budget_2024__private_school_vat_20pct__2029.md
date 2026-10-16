# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11621:8bf103a18fecf781 | 1,388.0 | 2,163.0 | 775.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11627:37d39a5448ffd160 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f | — | — | — | — | — |
| measure_year | total | 1,388.0 | 2,163.0 | 775.0 | numerical | move_above_threshold |
| head | private_school_vat | 1,388.0 | 2,163.0 | 775.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11621:8bf103a18fecf781 (row 11621) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT | 1,726.5 | 1,388.0 | 2,163.0 |
| base | obr_pmd_nov2025:11627:37d39a5448ffd160 (row 11627) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | 484.0 | — | — |
| base | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f (row 22786) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | -484.0 | — | — |
| head | obr_pmd_nov2025:11621:8bf103a18fecf781 (row 11621) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT | 1,726.5 | 1,388.0 | 2,163.0 |
| head | obr_pmd_nov2025:11627:37d39a5448ffd160 (row 11627) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | 484.0 | — | — |
| head | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f (row 22786) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | -484.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029.json` (sha256 `9b65d6ba9924f83a3fd6f37f834a2dd916d8664ada6a817a9cd09f5e1f6627ed`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029.json` (sha256 `be9fe1ca29a128088a86762f0473feef771d44e2c7fbabc7fcf58cc198539fa7`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
