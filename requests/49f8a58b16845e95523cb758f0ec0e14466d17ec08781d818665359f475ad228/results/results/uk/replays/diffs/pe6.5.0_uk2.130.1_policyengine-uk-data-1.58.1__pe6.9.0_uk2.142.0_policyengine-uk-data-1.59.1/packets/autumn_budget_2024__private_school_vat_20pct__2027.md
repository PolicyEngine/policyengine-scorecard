# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11619:8726edda9aa7b020 | 2,044.4 | 1,960.2 | -84.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11625:b0574efd1cd0378e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22784:b7a7cb6abf5168fd | — | — | — | — | — |
| measure_year | total | 2,044.4 | 1,960.2 | -84.2 | numerical | move_above_threshold |
| head | private_school_vat | 2,044.4 | 1,960.2 | -84.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11619:8726edda9aa7b020 (row 11619) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT | 1,608.9 | 2,044.4 | 1,960.2 |
| base | obr_pmd_nov2025:11625:b0574efd1cd0378e (row 11625) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | 452.0 | — | — |
| base | obr_pmd_nov2025:22784:b7a7cb6abf5168fd (row 22784) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | -452.0 | — | — |
| head | obr_pmd_nov2025:11619:8726edda9aa7b020 (row 11619) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT | 1,608.9 | 2,044.4 | 1,960.2 |
| head | obr_pmd_nov2025:11625:b0574efd1cd0378e (row 11625) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | 452.0 | — | — |
| head | obr_pmd_nov2025:22784:b7a7cb6abf5168fd (row 22784) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | -452.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027.json` (sha256 `820930eea4ddfd3850bb65f6fcc036fb09cc12702a0c387173b40f2cc59ded56`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027.json` (sha256 `310e5da350a13061f785922298ff83ea4b59c47d2fe0205da715ebca8e1d16a3`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
