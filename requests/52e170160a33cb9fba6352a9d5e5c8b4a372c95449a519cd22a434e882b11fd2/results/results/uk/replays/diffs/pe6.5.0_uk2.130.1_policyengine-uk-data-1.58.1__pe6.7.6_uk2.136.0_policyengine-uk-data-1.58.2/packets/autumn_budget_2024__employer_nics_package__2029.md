# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11669:1cedd72c387ad84b | -8,092.9 | -7,984.2 | 108.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11675:286359ea5a53fc94 | 25,792.5 | 25,840.1 | 47.6 | — | — |
| source_row | obr_pmd_nov2025:11681:83ebf7f916ba0b8d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22822:be5f3270a974f57f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22828:f93a41b9d86839e9 | — | — | — | — | — |
| measure_year | total | 17,699.6 | 17,855.8 | 156.3 | — | — |
| head | income_tax | -8,092.9 | -7,984.2 | 108.6 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,450.6 | -1,450.2 | 0.4 | — | — |
| head | ni_class_1_employer | 27,241.7 | 27,288.8 | 47.1 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.4 | 1.5 | 0.1 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11669:1cedd72c387ad84b (row 11669) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -129.8 | -8,092.9 | -7,984.2 |
| base | obr_pmd_nov2025:11675:286359ea5a53fc94 (row 11675) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 25,624.6 | 25,792.5 | 25,840.1 |
| base | obr_pmd_nov2025:11681:83ebf7f916ba0b8d (row 11681) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 231.7 | — | — |
| base | obr_pmd_nov2025:22822:be5f3270a974f57f (row 22822) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -14.7 | — | — |
| base | obr_pmd_nov2025:22828:f93a41b9d86839e9 (row 22828) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -2.1 | — | — |
| head | obr_pmd_nov2025:11669:1cedd72c387ad84b (row 11669) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -129.8 | -8,092.9 | -7,984.2 |
| head | obr_pmd_nov2025:11675:286359ea5a53fc94 (row 11675) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 25,624.6 | 25,792.5 | 25,840.1 |
| head | obr_pmd_nov2025:11681:83ebf7f916ba0b8d (row 11681) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 231.7 | — | — |
| head | obr_pmd_nov2025:22822:be5f3270a974f57f (row 22822) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -14.7 | — | — |
| head | obr_pmd_nov2025:22828:f93a41b9d86839e9 (row 22828) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -2.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029.json` (sha256 `7df2d5f7e7eeed2ed1a50bebb7c4e9562b4dbef83d8d8e3d64b85522a5a10912`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029.json` (sha256 `420e3a62adc542ab5098e86394c81248795934aeb67a260c93b02456f478b07c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.136.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
