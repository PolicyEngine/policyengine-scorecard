# Investigation packet: autumn_budget_2024 / autumn_budget_2024__private_school_vat_20pct / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11617:414a87b10621e433 | 1,258.4 | 1,972.7 | 714.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11623:b03eabd172377164 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22782:f6cf42e5375f2826 | — | — | — | — | — |
| measure_year | total | 1,258.4 | 1,972.7 | 714.3 | numerical | move_above_threshold |
| head | private_school_vat | 1,258.4 | 1,972.7 | 714.3 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11617:414a87b10621e433 (row 11617) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT | 1,505.7 | 1,258.4 | 1,972.7 |
| obr_pmd_nov2025:11623:b03eabd172377164 (row 11623) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | 425.0 | — | — |
| obr_pmd_nov2025:22782:f6cf42e5375f2826 (row 22782) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | VAT refunds | -425.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025.json` (sha256 `b72464503faffde8fe6ce0fb81f8678bfb0f0a1b7f2f7529703e40b37a6ba5f4`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025.json` (sha256 `14134d4392ed35fe7ce9207e74e10205f2510ba7f9f52c4f0e7da7bfa4a0d2fa`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.contrib.labour.private_school_vat": {"2025-01-01.2035-12-31": 0.2}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__private_school_vat_20pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__private_school_vat_20pct --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
