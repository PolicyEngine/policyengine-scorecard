# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11668:a076a7d6b3992e7c | -8,146.6 | -7,981.5 | 165.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11674:6dd4d473c559cbea | 25,525.5 | 25,080.3 | -445.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11680:1df0b2733f687ca0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22821:be2053a7986ecc49 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22827:9881af9ed6467d43 | — | — | — | — | — |
| measure_year | total | 17,378.9 | 17,098.8 | -280.2 | numerical | move_above_threshold |
| head | income_tax | -8,146.6 | -7,981.5 | 165.0 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,392.0 | -1,357.0 | 35.1 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,915.0 | 26,436.3 | -478.7 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 2.6 | 1.0 | -1.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11668:a076a7d6b3992e7c (row 11668) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -125.0 | -8,146.6 | -7,981.5 |
| base | obr_pmd_nov2025:11674:6dd4d473c559cbea (row 11674) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 24,873.6 | 25,525.5 | 25,080.3 |
| base | obr_pmd_nov2025:11680:1df0b2733f687ca0 (row 11680) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 197.4 | — | — |
| base | obr_pmd_nov2025:22821:be2053a7986ecc49 (row 22821) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -13.3 | — | — |
| base | obr_pmd_nov2025:22827:9881af9ed6467d43 (row 22827) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.9 | — | — |
| head | obr_pmd_nov2025:11668:a076a7d6b3992e7c (row 11668) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -125.0 | -8,146.6 | -7,981.5 |
| head | obr_pmd_nov2025:11674:6dd4d473c559cbea (row 11674) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 24,873.6 | 25,525.5 | 25,080.3 |
| head | obr_pmd_nov2025:11680:1df0b2733f687ca0 (row 11680) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 197.4 | — | — |
| head | obr_pmd_nov2025:22821:be2053a7986ecc49 (row 22821) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -13.3 | — | — |
| head | obr_pmd_nov2025:22827:9881af9ed6467d43 (row 22827) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028.json` (sha256 `47db7d0d6bd0e778a76eaf7e87ee43748aec72515b65e22cd8dcc8575b1da48d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028.json` (sha256 `8431cdb7167b7a91ba803e9f7bc6ef8db8f81ad467702b1fcc3f1fdb04524ba3`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
