# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11669:1cedd72c387ad84b | -8,218.2 | -8,377.4 | -159.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11675:286359ea5a53fc94 | 25,764.2 | 25,248.5 | -515.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11681:83ebf7f916ba0b8d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22822:be5f3270a974f57f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22828:f93a41b9d86839e9 | — | — | — | — | — |
| measure_year | total | 17,546.0 | 16,871.1 | -674.9 | numerical | move_above_threshold |
| head | income_tax | -8,218.2 | -8,377.4 | -159.2 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,357.6 | -1,349.3 | 8.3 | — | — |
| head | ni_class_1_employer | 27,120.7 | 26,597.0 | -523.6 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.2 | 0.8 | -0.4 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11669:1cedd72c387ad84b (row 11669) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -129.8 | -8,218.2 | -8,377.4 |
| base | obr_pmd_nov2025:11675:286359ea5a53fc94 (row 11675) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 25,624.6 | 25,764.2 | 25,248.5 |
| base | obr_pmd_nov2025:11681:83ebf7f916ba0b8d (row 11681) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 231.7 | — | — |
| base | obr_pmd_nov2025:22822:be5f3270a974f57f (row 22822) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -14.7 | — | — |
| base | obr_pmd_nov2025:22828:f93a41b9d86839e9 (row 22828) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -2.1 | — | — |
| head | obr_pmd_nov2025:11669:1cedd72c387ad84b (row 11669) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -129.8 | -8,218.2 | -8,377.4 |
| head | obr_pmd_nov2025:11675:286359ea5a53fc94 (row 11675) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 25,624.6 | 25,764.2 | 25,248.5 |
| head | obr_pmd_nov2025:11681:83ebf7f916ba0b8d (row 11681) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | 231.7 | — | — |
| head | obr_pmd_nov2025:22822:be5f3270a974f57f (row 22822) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -14.7 | — | — |
| head | obr_pmd_nov2025:22828:f93a41b9d86839e9 (row 22828) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -2.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029.json` (sha256 `03f5a4cb532d6953e7d0d59d4cc51513c1b2c07e8d7bfff33d6261ad2eac02bc`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029.json` (sha256 `e9f826eed3236f126211106e78adaa2a96dc2481f8e3ba1f8c02ef070020ad7a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
