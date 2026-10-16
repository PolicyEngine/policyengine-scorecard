# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11619:8726edda9aa7b020 | 1,323.0 | 2,044.4 | 721.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11625:b0574efd1cd0378e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22784:b7a7cb6abf5168fd | — | — | — | — | — |
| measure_year | total | 1,323.0 | 2,044.4 | 721.4 | numerical | move_above_threshold |
| head | private_school_vat | 1,323.0 | 2,044.4 | 721.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11619:8726edda9aa7b020 (row 11619) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT | 1,608.9 | 1,323.0 | 2,044.4 |
| base | obr_pmd_nov2025:11625:b0574efd1cd0378e (row 11625) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | 452.0 | — | — |
| base | obr_pmd_nov2025:22784:b7a7cb6abf5168fd (row 22784) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | -452.0 | — | — |
| head | obr_pmd_nov2025:11619:8726edda9aa7b020 (row 11619) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT | 1,608.9 | 1,323.0 | 2,044.4 |
| head | obr_pmd_nov2025:11625:b0574efd1cd0378e (row 11625) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | 452.0 | — | — |
| head | obr_pmd_nov2025:22784:b7a7cb6abf5168fd (row 22784) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | VAT refunds | -452.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027.json` (sha256 `83f7f9058c3dd031c1fb421390e51f5746dd117e4a21875bd73d209c253d7af6`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027.json` (sha256 `ebb869817b7ee1268b4a53b71ed114210849270d1f1e6426d509c07bf9cebc2f`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__private_school_vat_20pct --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
