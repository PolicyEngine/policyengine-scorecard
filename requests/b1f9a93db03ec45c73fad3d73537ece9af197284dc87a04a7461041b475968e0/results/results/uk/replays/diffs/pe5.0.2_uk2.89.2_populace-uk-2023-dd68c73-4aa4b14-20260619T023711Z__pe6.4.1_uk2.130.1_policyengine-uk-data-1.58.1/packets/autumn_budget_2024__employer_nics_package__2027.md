# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11667:35345df3785dfdea | -8,784.0 | -7,564.0 | 1,219.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11673:94b8906a8929f113 | 25,206.4 | 24,832.1 | -374.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22826:318fb1def1dc970d | — | — | — | — | — |
| measure_year | total | 16,422.5 | 17,268.0 | 845.6 | numerical | move_above_threshold |
| head | income_tax | -8,784.0 | -7,564.0 | 1,219.9 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,264.8 | -1,433.9 | -169.1 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,470.3 | 26,265.5 | -204.8 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.9 | 0.5 | -0.4 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11667:35345df3785dfdea (row 11667) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -139.4 | -8,784.0 | -7,564.0 |
| base | obr_pmd_nov2025:11673:94b8906a8929f113 (row 11673) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 24,166.6 | 25,206.4 | 24,832.1 |
| base | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 (row 11679) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 157.9 | — | — |
| base | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb (row 22820) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -12.8 | — | — |
| base | obr_pmd_nov2025:22826:318fb1def1dc970d (row 22826) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.7 | — | — |
| head | obr_pmd_nov2025:11667:35345df3785dfdea (row 11667) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -139.4 | -8,784.0 | -7,564.0 |
| head | obr_pmd_nov2025:11673:94b8906a8929f113 (row 11673) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 24,166.6 | 25,206.4 | 24,832.1 |
| head | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 (row 11679) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 157.9 | — | — |
| head | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb (row 22820) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -12.8 | — | — |
| head | obr_pmd_nov2025:22826:318fb1def1dc970d (row 22826) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.7 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027.json` (sha256 `c9e81b8ec1badf77d9016586ecfe90e5a34f9f772446248f28b0541c86bb4e4e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027.json` (sha256 `d0d26d8578af7589a70e6d0a145cf0f2dd62b8c251e810995aed0d4936d5062a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
