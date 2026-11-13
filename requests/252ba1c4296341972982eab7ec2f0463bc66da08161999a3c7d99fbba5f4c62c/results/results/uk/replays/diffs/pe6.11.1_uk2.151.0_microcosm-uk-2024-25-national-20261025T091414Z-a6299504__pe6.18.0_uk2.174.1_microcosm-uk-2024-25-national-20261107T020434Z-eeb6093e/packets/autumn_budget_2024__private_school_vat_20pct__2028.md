# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical, structural, inertness
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11620:5446e6157f4ef4ec | 1,523.3 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11626:0135955a60199873 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22785:2ad7bb129298e82a | — | — | — | — | — |
| measure_year | total | 1,523.3 | 0.0 | -1,523.3 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | private_school_vat | 1,523.3 | 0.0 | -1,523.3 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11620:5446e6157f4ef4ec (row 11620) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT | 1,664.3 | 1,523.3 | — |
| base | obr_pmd_nov2025:11626:0135955a60199873 (row 11626) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | 467.0 | — | — |
| base | obr_pmd_nov2025:22785:2ad7bb129298e82a (row 22785) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | -467.0 | — | — |
| head | obr_pmd_nov2025:11620:5446e6157f4ef4ec (row 11620) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT | 1,664.3 | 1,523.3 | — |
| head | obr_pmd_nov2025:11626:0135955a60199873 (row 11626) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | 467.0 | — | — |
| head | obr_pmd_nov2025:22785:2ad7bb129298e82a (row 22785) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | -467.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028.json` (sha256 `eee4d1f549bf6a0d673a052ff5926a5ac6e2e46ae3133da60242a08d0e3e3a28`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028.json` (sha256 `eb8fc40c3e84129a7941cb32674ff88cf209ca559793a55a3212d9e3c7505eb4`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
