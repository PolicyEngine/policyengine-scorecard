# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11667:35345df3785dfdea | -7,746.1 | -7,829.5 | -83.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11673:94b8906a8929f113 | 24,682.9 | 24,306.4 | -376.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22826:318fb1def1dc970d | — | — | — | — | — |
| measure_year | total | 16,936.9 | 16,476.8 | -460.0 | numerical | move_above_threshold |
| head | income_tax | -7,746.1 | -7,829.5 | -83.5 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,350.5 | -1,345.7 | 4.8 | — | — |
| head | ni_class_1_employer | 26,032.4 | 25,651.4 | -381.0 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.0 | 0.7 | -0.3 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11667:35345df3785dfdea (row 11667) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -139.4 | -7,746.1 | -7,829.5 |
| base | obr_pmd_nov2025:11673:94b8906a8929f113 (row 11673) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 24,166.6 | 24,682.9 | 24,306.4 |
| base | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 (row 11679) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 157.9 | — | — |
| base | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb (row 22820) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -12.8 | — | — |
| base | obr_pmd_nov2025:22826:318fb1def1dc970d (row 22826) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.7 | — | — |
| head | obr_pmd_nov2025:11667:35345df3785dfdea (row 11667) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -139.4 | -7,746.1 | -7,829.5 |
| head | obr_pmd_nov2025:11673:94b8906a8929f113 (row 11673) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 24,166.6 | 24,682.9 | 24,306.4 |
| head | obr_pmd_nov2025:11679:80b7d4c0d69f1c59 (row 11679) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 157.9 | — | — |
| head | obr_pmd_nov2025:22820:f6b54a5fbcdee6cb (row 22820) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -12.8 | — | — |
| head | obr_pmd_nov2025:22826:318fb1def1dc970d (row 22826) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027.json` (sha256 `c206b9b2c2af7e3474b59cef0814a487faa9384f93d55fe43ec888073298fe1a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027.json` (sha256 `3cd66f36d6fcd0614228231ef1d59785915ca32f2772a9850a72954da110f2f4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
