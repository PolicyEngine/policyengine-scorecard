# Investigation packet: autumn_budget_2024 / autumn_budget_2024__employer_nics_package / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11666:e4413c7487d85ddf | -7,376.9 | -7,675.5 | -298.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11672:0b55202125025854 | 24,413.3 | 25,306.6 | 893.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22825:edacdcc46eb06fe4 | — | — | — | — | — |
| measure_year | total | 17,036.4 | 17,631.1 | 594.7 | numerical | move_above_threshold |
| head | income_tax | -7,376.9 | -7,675.5 | -298.6 | numerical | move_above_threshold |
| head | ni_class_1_employee | -1,431.6 | -1,480.5 | -48.9 | numerical | move_above_threshold |
| head | ni_class_1_employer | 25,844.5 | 26,786.4 | 941.9 | numerical | move_above_threshold |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.5 | 0.7 | 0.3 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -7,376.9 | -7,675.5 |
| base | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,413.3 | 25,306.6 |
| base | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| base | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| base | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |
| head | obr_pmd_nov2025:11666:e4413c7487d85ddf (row 11666) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | -312.9 | -7,376.9 | -7,675.5 |
| head | obr_pmd_nov2025:11672:0b55202125025854 (row 11672) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 23,923.3 | 24,413.3 | 25,306.6 |
| head | obr_pmd_nov2025:11678:cf7e6fb3e86bb47c (row 11678) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | 104.3 | — | — |
| head | obr_pmd_nov2025:22819:dd2ccd436f0e20b2 (row 22819) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | -22.6 | — | — |
| head | obr_pmd_nov2025:22825:edacdcc46eb06fe4 (row 22825) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | -2.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `2c959c6a051678ed7b351170a847833964a184a0e9cb8b35a55cef03c19c688d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026.json` (sha256 `0d0df7afd027e34d92f711af5eba6e76eb29e1250359729bf28481b0247256a4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employer": {"2025-01-01.2035-12-31": 0.138}, "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {"2025-01-01.2035-12-31": 175}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__employer_nics_package --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
