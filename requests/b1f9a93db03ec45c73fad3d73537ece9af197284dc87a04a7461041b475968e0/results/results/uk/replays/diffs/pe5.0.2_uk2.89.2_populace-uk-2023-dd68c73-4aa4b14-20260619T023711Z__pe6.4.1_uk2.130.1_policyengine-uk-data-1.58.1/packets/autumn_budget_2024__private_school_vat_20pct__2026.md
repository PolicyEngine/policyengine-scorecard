# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,292.3 | 1,966.5 | 674.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11624:58692c00fbcbe1a9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22783:70b4189e19c7238f | — | — | — | — | — |
| measure_year | total | 1,292.3 | 1,966.5 | 674.3 | numerical | move_above_threshold |
| head | private_school_vat | 1,292.3 | 1,966.5 | 674.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,292.3 | 1,966.5 |
| base | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| base | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |
| head | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,292.3 | 1,966.5 |
| head | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| head | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `4aa3bc9f868865aa47e5d5f384930e74fde425e0dd443ab3e2ad4354b7943fc9`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `dfe7d96c0fd1c9ccfd30d7cfff11a4298bf817242f730603f4aa8a51d986d8b1`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
