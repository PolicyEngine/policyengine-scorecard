# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.5.0_uk2.134.5_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11668:a076a7d6b3992e7c | -7,898.2 | -7,807.0 | 91.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11674:6dd4d473c559cbea | 25,217.9 | 25,258.4 | 40.5 | — | — |
| source_row | obr_pmd_nov2025:11680:1df0b2733f687ca0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22821:be2053a7986ecc49 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22827:9881af9ed6467d43 | — | — | — | — | — |
| measure_year | total | 17,319.6 | 17,451.4 | 131.8 | — | — |
| head | income_tax | -7,898.2 | -7,807.0 | 91.3 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,446.3 | -1,451.0 | -4.7 | — | — |
| head | ni_class_1_employer | 26,662.9 | 26,708.3 | 45.4 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.3 | 1.0 | -0.2 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11668:a076a7d6b3992e7c (row 11668) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -125.0 | -7,898.2 | -7,807.0 |
| base | obr_pmd_nov2025:11674:6dd4d473c559cbea (row 11674) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 24,873.6 | 25,217.9 | 25,258.4 |
| base | obr_pmd_nov2025:11680:1df0b2733f687ca0 (row 11680) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 197.4 | — | — |
| base | obr_pmd_nov2025:22821:be2053a7986ecc49 (row 22821) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -13.3 | — | — |
| base | obr_pmd_nov2025:22827:9881af9ed6467d43 (row 22827) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.9 | — | — |
| head | obr_pmd_nov2025:11668:a076a7d6b3992e7c (row 11668) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -125.0 | -7,898.2 | -7,807.0 |
| head | obr_pmd_nov2025:11674:6dd4d473c559cbea (row 11674) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 24,873.6 | 25,217.9 | 25,258.4 |
| head | obr_pmd_nov2025:11680:1df0b2733f687ca0 (row 11680) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | 197.4 | — | — |
| head | obr_pmd_nov2025:22821:be2053a7986ecc49 (row 22821) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -13.3 | — | — |
| head | obr_pmd_nov2025:22827:9881af9ed6467d43 (row 22827) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028.json` (sha256 `f0192295e3732d1fa23539b962ea38cc29aea6e0993612a93e13420320d0b28d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.5.0_uk2.134.5_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028.json` (sha256 `ba3e643ffb27d0ac4944f65d9324560e346bfc04edcc32222457831795fad486`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.134.5_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.134.5_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
