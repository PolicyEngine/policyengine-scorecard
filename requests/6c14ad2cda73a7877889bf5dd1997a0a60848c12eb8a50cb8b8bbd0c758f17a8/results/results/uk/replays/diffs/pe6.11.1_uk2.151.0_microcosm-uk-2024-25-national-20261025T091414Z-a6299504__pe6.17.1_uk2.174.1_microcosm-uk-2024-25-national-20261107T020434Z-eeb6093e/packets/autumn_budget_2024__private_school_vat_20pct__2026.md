# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11618:ad4256274cc146d3 | 1,452.9 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11624:58692c00fbcbe1a9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22783:70b4189e19c7238f | — | — | — | — | — |
| measure_year | total | 1,452.9 | 0.0 | -1,452.9 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | private_school_vat | 1,452.9 | 0.0 | -1,452.9 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,452.9 | — |
| base | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| base | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |
| head | obr_pmd_nov2025:11618:ad4256274cc146d3 (row 11618) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT | 1,557.7 | 1,452.9 | — |
| head | obr_pmd_nov2025:11624:58692c00fbcbe1a9 (row 11624) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | 439.0 | — | — |
| head | obr_pmd_nov2025:22783:70b4189e19c7238f (row 22783) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | VAT refunds | -439.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `a2fc071f31c4b1fb5848b60d83eadb0ce0b60e456f509d7bd54fe738bd451869`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json` (sha256 `66052f1a7b425804d1016ab459268db2a8bee097c2744f92695f792b685831c1`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
