# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11668:a076a7d6b3992e7c | -8,988.4 | -7,898.2 | 1,090.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11674:6dd4d473c559cbea | 25,618.3 | 25,217.9 | -400.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11680:1df0b2733f687ca0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22821:be2053a7986ecc49 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22827:9881af9ed6467d43 | — | — | — | — | — |
| measure_year | total | 16,629.9 | 17,319.6 | 689.8 | numerical | move_above_threshold |
| head | income_tax | -8,988.4 | -7,898.2 | 1,090.2 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,282.0 | -1,446.3 | -164.3 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,899.4 | 26,662.9 | -236.5 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.9 | 1.3 | 0.3 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11668:a076a7d6b3992e7c (row 11668) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -125.0 | -8,988.4 | -7,898.2 |
| base | obr_pmd_nov2025:11674:6dd4d473c559cbea (row 11674) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 24,873.6 | 25,618.3 | 25,217.9 |
| base | obr_pmd_nov2025:11680:1df0b2733f687ca0 (row 11680) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 197.4 | — | — |
| base | obr_pmd_nov2025:22821:be2053a7986ecc49 (row 22821) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -13.3 | — | — |
| base | obr_pmd_nov2025:22827:9881af9ed6467d43 (row 22827) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.9 | — | — |
| head | obr_pmd_nov2025:11668:a076a7d6b3992e7c (row 11668) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -125.0 | -8,988.4 | -7,898.2 |
| head | obr_pmd_nov2025:11674:6dd4d473c559cbea (row 11674) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 24,873.6 | 25,618.3 | 25,217.9 |
| head | obr_pmd_nov2025:11680:1df0b2733f687ca0 (row 11680) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 197.4 | — | — |
| head | obr_pmd_nov2025:22821:be2053a7986ecc49 (row 22821) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -13.3 | — | — |
| head | obr_pmd_nov2025:22827:9881af9ed6467d43 (row 22827) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.9 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028.json` (sha256 `3b783d8bdfdab4352b815cb8cf01882f5eb4e0495befae9d29bfbd94366444bc`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028.json` (sha256 `da1b26e9964cf8fd7de100f8aed6ca92663d4e8794e46041a6169fe12a3d6146`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
