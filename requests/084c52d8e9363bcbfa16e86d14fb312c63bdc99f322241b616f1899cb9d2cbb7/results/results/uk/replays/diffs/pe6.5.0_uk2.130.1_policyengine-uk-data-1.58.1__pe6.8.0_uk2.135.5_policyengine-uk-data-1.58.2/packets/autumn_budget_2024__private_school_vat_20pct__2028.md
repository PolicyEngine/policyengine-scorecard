# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11620:5446e6157f4ef4ec | 2,138.1 | 2,032.7 | -105.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11626:0135955a60199873 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22785:2ad7bb129298e82a | — | — | — | — | — |
| measure_year | total | 2,138.1 | 2,032.7 | -105.4 | numerical | move_above_threshold |
| head | private_school_vat | 2,138.1 | 2,032.7 | -105.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11620:5446e6157f4ef4ec (row 11620) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT | 1,664.3 | 2,138.1 | 2,032.7 |
| base | obr_pmd_nov2025:11626:0135955a60199873 (row 11626) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | 467.0 | — | — |
| base | obr_pmd_nov2025:22785:2ad7bb129298e82a (row 22785) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | -467.0 | — | — |
| head | obr_pmd_nov2025:11620:5446e6157f4ef4ec (row 11620) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT | 1,664.3 | 2,138.1 | 2,032.7 |
| head | obr_pmd_nov2025:11626:0135955a60199873 (row 11626) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | 467.0 | — | — |
| head | obr_pmd_nov2025:22785:2ad7bb129298e82a (row 22785) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | VAT refunds | -467.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028.json` (sha256 `dd928f7732ce7aae4593cba3eeeebf379e7d2c79742039ee7fbcd5c3da02ec4b`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028.json` (sha256 `c7b40b5ace4160c7c457053054a06c441b70d61598cf32960d34e03726aaf682`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
