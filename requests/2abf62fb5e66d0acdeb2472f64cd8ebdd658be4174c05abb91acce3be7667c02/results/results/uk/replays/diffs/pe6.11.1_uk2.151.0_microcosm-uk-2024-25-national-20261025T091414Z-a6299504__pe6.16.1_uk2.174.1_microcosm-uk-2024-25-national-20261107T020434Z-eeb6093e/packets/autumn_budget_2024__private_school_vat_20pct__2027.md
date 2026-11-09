# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11619:8726edda9aa7b020 | 1,487.5 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11625:b0574efd1cd0378e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22784:b7a7cb6abf5168fd | — | — | — | — | — |
| measure_year | total | 1,487.5 | 0.0 | -1,487.5 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | private_school_vat | 1,487.5 | 0.0 | -1,487.5 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11619:8726edda9aa7b020 (row 11619) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT | 1,608.9 | 1,487.5 | — |
| base | obr_pmd_nov2025:11625:b0574efd1cd0378e (row 11625) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | 452.0 | — | — |
| base | obr_pmd_nov2025:22784:b7a7cb6abf5168fd (row 22784) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | -452.0 | — | — |
| head | obr_pmd_nov2025:11619:8726edda9aa7b020 (row 11619) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT | 1,608.9 | 1,487.5 | — |
| head | obr_pmd_nov2025:11625:b0574efd1cd0378e (row 11625) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | 452.0 | — | — |
| head | obr_pmd_nov2025:22784:b7a7cb6abf5168fd (row 22784) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | -452.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027.json` (sha256 `c37ea7e042d17b59a5bafb2a7913e33a01c7d19509fecae32330f2395e8fdfcf`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027.json` (sha256 `de7763c7a738346d1c15bd6f0da9c118607d8305286e3adb954438525d4fd51b`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
