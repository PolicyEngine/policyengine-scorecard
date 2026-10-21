# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11667:35345df3785dfdea | -7,564.0 | -7,871.2 | -307.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11673:94b8906a8929f113 | 24,832.1 | 25,743.0 | 911.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22826:318fb1def1dc970d | — | — | — | — | — |
| measure_year | total | 17,268.0 | 17,871.9 | 603.8 | numerical | move_above_threshold |
| head | income_tax | -7,564.0 | -7,871.2 | -307.1 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,433.9 | -1,480.3 | -46.4 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,265.5 | 27,222.6 | 957.1 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.5 | 0.8 | 0.3 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11667:35345df3785dfdea (row 11667) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -139.4 | -7,564.0 | -7,871.2 |
| base | obr_pmd_nov2025:11673:94b8906a8929f113 (row 11673) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 24,166.6 | 24,832.1 | 25,743.0 |
| base | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 (row 11679) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 157.9 | — | — |
| base | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb (row 22820) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -12.8 | — | — |
| base | obr_pmd_nov2025:22826:318fb1def1dc970d (row 22826) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.7 | — | — |
| head | obr_pmd_nov2025:11667:35345df3785dfdea (row 11667) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -139.4 | -7,564.0 | -7,871.2 |
| head | obr_pmd_nov2025:11673:94b8906a8929f113 (row 11673) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 24,166.6 | 24,832.1 | 25,743.0 |
| head | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 (row 11679) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 157.9 | — | — |
| head | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb (row 22820) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -12.8 | — | — |
| head | obr_pmd_nov2025:22826:318fb1def1dc970d (row 22826) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027.json` (sha256 `aa609a3f3be1082280a56c0d062087c02c6e30b533abeaa9f3d7a493dd84077f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027.json` (sha256 `fa86d4a5dea1c3b8a8cbe32614a1883d60fd799012ced10aeaa45f6b5c1c7a85`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
