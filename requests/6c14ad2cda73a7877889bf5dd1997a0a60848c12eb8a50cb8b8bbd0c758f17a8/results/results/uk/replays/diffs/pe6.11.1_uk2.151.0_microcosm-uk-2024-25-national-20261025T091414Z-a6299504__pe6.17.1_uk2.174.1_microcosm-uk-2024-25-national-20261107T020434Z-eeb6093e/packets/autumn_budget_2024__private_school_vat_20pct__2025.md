# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11617:414a87b10621e433 | 1,414.9 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11623:b03eabd172377164 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22782:f6cf42e5375f2826 | — | — | — | — | — |
| measure_year | total | 1,414.9 | 0.0 | -1,414.9 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | private_school_vat | 1,414.9 | 0.0 | -1,414.9 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11617:414a87b10621e433 (row 11617) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT | 1,505.7 | 1,414.9 | — |
| base | obr_pmd_nov2025:11623:b03eabd172377164 (row 11623) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | 425.0 | — | — |
| base | obr_pmd_nov2025:22782:f6cf42e5375f2826 (row 22782) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | -425.0 | — | — |
| head | obr_pmd_nov2025:11617:414a87b10621e433 (row 11617) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT | 1,505.7 | 1,414.9 | — |
| head | obr_pmd_nov2025:11623:b03eabd172377164 (row 11623) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | 425.0 | — | — |
| head | obr_pmd_nov2025:22782:f6cf42e5375f2826 (row 22782) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | -425.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025.json` (sha256 `c211e420ae23909c5e87784fb3e511b8d6f6bbb0a97877e9e59bbbf76c5d5e71`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025.json` (sha256 `3b289bb374b8e08009334f88c640b3e0c23ef2944d7c9517689fb2a82d828627`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
