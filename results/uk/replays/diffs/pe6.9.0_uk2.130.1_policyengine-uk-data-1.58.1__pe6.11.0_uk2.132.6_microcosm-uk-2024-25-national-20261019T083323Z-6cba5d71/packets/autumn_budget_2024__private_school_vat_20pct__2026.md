# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,966.5 | 1,451.2 | -515.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11624:58692c00fbcbe1a9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22783:70b4189e19c7238f | — | — | — | — | — |
| measure_year | total | 1,966.5 | 1,451.2 | -515.3 | numerical | move_above_threshold |
| head | private_school_vat | 1,966.5 | 1,451.2 | -515.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,966.5 | 1,451.2 |
| base | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| base | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |
| head | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,966.5 | 1,451.2 |
| head | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| head | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `8db5d03b1d1a15ffe5ec271e0c4c8f862a6a506d5df09b0dff92d2dbcfd260c2`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `105656489203cd365653da274d30a2d064debdfbd3d4c0eac179fcf5b34ff5a2`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
