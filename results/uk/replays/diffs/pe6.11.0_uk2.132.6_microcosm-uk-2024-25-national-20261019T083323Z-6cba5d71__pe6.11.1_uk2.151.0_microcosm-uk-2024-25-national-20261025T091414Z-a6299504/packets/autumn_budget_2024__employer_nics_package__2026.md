# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -7,697.1 | -7,513.2 | 183.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11672:0b55202125025854 | 24,695.7 | 24,257.8 | -437.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22825:edacdcc46eb06fe4 | — | — | — | — | — |
| measure_year | total | 16,998.6 | 16,744.6 | -254.0 | numerical | move_above_threshold |
| head | income_tax | -7,697.1 | -7,513.2 | 183.9 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,380.3 | -1,346.6 | 33.7 | numerical | move_above_threshold |
| head | ni_class_1_employer | 26,074.7 | 25,603.4 | -471.3 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.2 | 1.0 | -0.2 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -7,697.1 | -7,513.2 |
| base | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,695.7 | 24,257.8 |
| base | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| base | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| base | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |
| head | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -7,697.1 | -7,513.2 |
| head | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,695.7 | 24,257.8 |
| head | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| head | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| head | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `a42f08f1b66c5962be51add4c0601bdea0b0ed26111075be3d0061c9c216aeb5`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `ad46179b7c1a3b6150b179e71f83aa0b5d0e386a16856699c05737fb83c586d6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
