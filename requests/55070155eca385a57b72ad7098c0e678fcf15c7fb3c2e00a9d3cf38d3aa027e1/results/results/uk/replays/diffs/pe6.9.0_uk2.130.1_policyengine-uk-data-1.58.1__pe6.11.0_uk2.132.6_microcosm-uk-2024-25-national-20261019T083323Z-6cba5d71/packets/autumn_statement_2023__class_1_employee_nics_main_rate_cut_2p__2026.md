# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10545:18a361a4f818b0b8 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10551:67fe35e4947b995a | -11,791.7 | -11,770.0 | 21.7 | — | — |
| source_row | obr_pmd_nov2025:10557:93c084b7621cd9ac | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10563:81781f08d44304b1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21464:190052623cdf04c0 | 282.0 | 218.5 | -63.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21470:a374a68995990feb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21476:68e76146f1165518 | — | — | — | — | — |
| measure_year | total | -11,509.7 | -11,551.5 | -41.9 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,795.8 | -11,779.3 | 16.4 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 4.1 | 9.3 | 5.3 | numerical | move_above_threshold |
| head | universal_credit | 282.0 | 218.5 | -63.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10545:18a361a4f818b0b8 (row 10545) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 684.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10551:67fe35e4947b995a (row 10551) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,343.0 | -11,791.7 | -11,770.0 |
| base | obr_pmd_nov2025:10557:93c084b7621cd9ac (row 10557) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -410.0 | — | — |
| base | obr_pmd_nov2025:10563:81781f08d44304b1 (row 10563) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21464:190052623cdf04c0 (row 21464) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.4 | 282.0 | 218.5 |
| base | obr_pmd_nov2025:21470:a374a68995990feb (row 21470) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 5.7 | — | — |
| base | obr_pmd_nov2025:21476:68e76146f1165518 (row 21476) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 57.1 | — | — |
| head | obr_pmd_nov2025:10545:18a361a4f818b0b8 (row 10545) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 684.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10551:67fe35e4947b995a (row 10551) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,343.0 | -11,791.7 | -11,770.0 |
| head | obr_pmd_nov2025:10557:93c084b7621cd9ac (row 10557) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -410.0 | — | — |
| head | obr_pmd_nov2025:10563:81781f08d44304b1 (row 10563) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21464:190052623cdf04c0 (row 21464) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.4 | 282.0 | 218.5 |
| head | obr_pmd_nov2025:21470:a374a68995990feb (row 21470) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 5.7 | — | — |
| head | obr_pmd_nov2025:21476:68e76146f1165518 (row 21476) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 57.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026.json` (sha256 `be899bf31182c8db1798fdf4bd9fe67a03bc6b2b9a8bec6302ca2cc999bdfbf5`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026.json` (sha256 `f30e572d7c94b89d929ee1109697619fcecbd95da56903a3bffb00be79fbbb80`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
