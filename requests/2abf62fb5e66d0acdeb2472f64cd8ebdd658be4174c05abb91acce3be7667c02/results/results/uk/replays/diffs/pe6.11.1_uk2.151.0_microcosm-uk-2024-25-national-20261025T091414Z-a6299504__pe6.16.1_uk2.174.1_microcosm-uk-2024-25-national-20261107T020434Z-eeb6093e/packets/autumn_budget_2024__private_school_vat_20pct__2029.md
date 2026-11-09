# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11621:8bf103a18fecf781 | 1,560.6 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11627:37d39a5448ffd160 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f | — | — | — | — | — |
| measure_year | total | 1,560.6 | 0.0 | -1,560.6 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | private_school_vat | 1,560.6 | 0.0 | -1,560.6 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11621:8bf103a18fecf781 (row 11621) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT | 1,726.5 | 1,560.6 | — |
| base | obr_pmd_nov2025:11627:37d39a5448ffd160 (row 11627) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | 484.0 | — | — |
| base | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f (row 22786) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | -484.0 | — | — |
| head | obr_pmd_nov2025:11621:8bf103a18fecf781 (row 11621) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT | 1,726.5 | 1,560.6 | — |
| head | obr_pmd_nov2025:11627:37d39a5448ffd160 (row 11627) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | 484.0 | — | — |
| head | obr_pmd_nov2025:22786:b2bc03d5bfd19f7f (row 22786) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | VAT refunds | -484.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029.json` (sha256 `f1fe69dd2a92e95e8a1d8823be4b484f25a9d0670d1fe142ffd59c08fce969ee`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029.json` (sha256 `708c73b253b6a7776ab5d12aa8f8a49e6aabf92a112a332afdcf16f0a6888e9a`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
