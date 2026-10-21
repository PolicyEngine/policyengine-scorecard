# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,966.5 | 1,915.8 | -50.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11624:58692c00fbcbe1a9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22783:70b4189e19c7238f | — | — | — | — | — |
| measure_year | total | 1,966.5 | 1,915.8 | -50.8 | numerical | move_above_threshold |
| head | private_school_vat | 1,966.5 | 1,915.8 | -50.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,966.5 | 1,915.8 |
| base | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| base | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |
| head | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,966.5 | 1,915.8 |
| head | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| head | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `28d4522728c519e8306993b6e95130951de6549658252c73e44c2836eb493a37`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `d372d2af5a34c527e7505fd749b8b1165e2782f5fdad42ee228e0dcd8224e2a8`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.9_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
