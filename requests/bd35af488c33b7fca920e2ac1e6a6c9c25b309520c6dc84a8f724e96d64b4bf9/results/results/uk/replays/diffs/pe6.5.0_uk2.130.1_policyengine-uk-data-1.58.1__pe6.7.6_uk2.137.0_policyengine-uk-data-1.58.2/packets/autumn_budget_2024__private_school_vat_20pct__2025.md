# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11617:414a87b10621e433 | 1,940.3 | 1,844.3 | -96.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11623:b03eabd172377164 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22782:f6cf42e5375f2826 | — | — | — | — | — |
| measure_year | total | 1,940.3 | 1,844.3 | -96.0 | numerical | move_above_threshold |
| head | private_school_vat | 1,940.3 | 1,844.3 | -96.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11617:414a87b10621e433 (row 11617) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT | 1,505.7 | 1,940.3 | 1,844.3 |
| base | obr_pmd_nov2025:11623:b03eabd172377164 (row 11623) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | 425.0 | — | — |
| base | obr_pmd_nov2025:22782:f6cf42e5375f2826 (row 22782) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | -425.0 | — | — |
| head | obr_pmd_nov2025:11617:414a87b10621e433 (row 11617) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT | 1,505.7 | 1,940.3 | 1,844.3 |
| head | obr_pmd_nov2025:11623:b03eabd172377164 (row 11623) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | 425.0 | — | — |
| head | obr_pmd_nov2025:22782:f6cf42e5375f2826 (row 22782) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | -425.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025.json` (sha256 `3c3807777332e31927198b3189d9b14a77aa0ebcd3aec01c59dd13889fc0abd0`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025.json` (sha256 `7d118b0c96240ec57af2c1fd4c40d35827b22b9dbff2c862ecba28ab0a570497`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
