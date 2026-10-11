# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11620:5446e6157f4ef4ec | 1,354.9 | 2,176.6 | 821.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11626:0135955a60199873 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22785:2ad7bb129298e82a | — | — | — | — | — |
| measure_year | total | 1,354.9 | 2,176.6 | 821.8 | numerical | move_above_threshold |
| head | private_school_vat | 1,354.9 | 2,176.6 | 821.8 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11620:5446e6157f4ef4ec (row 11620) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT | 1,664.3 | 1,354.9 | 2,176.6 |
| obr_pmd_nov2025:11626:0135955a60199873 (row 11626) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | 467.0 | — | — |
| obr_pmd_nov2025:22785:2ad7bb129298e82a (row 22785) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | -467.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028.json` (sha256 `d65c650dd4abf908089442db4175e67667a6299853017d3861c8979ae5e58501`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028.json` (sha256 `93ba23b4da1ae971d9e8216964e941ebeef0a265071fadc5d2e55c4ff6793256`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
