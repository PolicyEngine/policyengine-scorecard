# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -7,513.2 | -7,573.4 | -60.2 | — | — |
| source_row | obr_pmd_nov2025:11672:0b55202125025854 | 24,257.8 | 23,866.9 | -390.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22825:edacdcc46eb06fe4 | — | — | — | — | — |
| measure_year | total | 16,744.6 | 16,293.4 | -451.2 | numerical | move_above_threshold |
| head | income_tax | -7,513.2 | -7,573.4 | -60.2 | — | — |
| head | ni_class_1_employee | -1,346.6 | -1,343.9 | 2.7 | — | — |
| head | ni_class_1_employer | 25,603.4 | 25,210.2 | -393.2 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 1.0 | 0.5 | -0.5 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -7,513.2 | -7,573.4 |
| base | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,257.8 | 23,866.9 |
| base | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| base | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| base | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |
| head | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -7,513.2 | -7,573.4 |
| head | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,257.8 | 23,866.9 |
| head | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| head | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| head | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `ad46179b7c1a3b6150b179e71f83aa0b5d0e386a16856699c05737fb83c586d6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `a1a4fd877f04a727107808e057203373c21c600a838a57b7b59eddd1569676c0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
