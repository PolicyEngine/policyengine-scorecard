# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10545:18a361a4f818b0b8 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10551:67fe35e4947b995a | -12,070.1 | -11,919.3 | 150.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10557:93c084b7621cd9ac | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10563:81781f08d44304b1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21464:190052623cdf04c0 | 104.7 | 274.9 | 170.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21470:a374a68995990feb | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21476:68e76146f1165518 | — | — | — | — | — |
| measure_year | total | -11,965.4 | -11,644.5 | 320.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,073.5 | -11,923.0 | 150.5 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.4 | 3.7 | 0.3 | — | — |
| head | universal_credit | 104.7 | 274.9 | 170.2 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10545:18a361a4f818b0b8 (row 10545) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 684.4 | 0.0 | 0.0 |
| obr_pmd_nov2025:10551:67fe35e4947b995a (row 10551) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -9,343.0 | -12,070.1 | -11,919.3 |
| obr_pmd_nov2025:10557:93c084b7621cd9ac (row 10557) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -410.0 | — | — |
| obr_pmd_nov2025:10563:81781f08d44304b1 (row 10563) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21464:190052623cdf04c0 (row 21464) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 171.4 | 104.7 | 274.9 |
| obr_pmd_nov2025:21470:a374a68995990feb (row 21470) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 5.7 | — | — |
| obr_pmd_nov2025:21476:68e76146f1165518 (row 21476) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 57.1 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026.json` (sha256 `65d728060d9d6b2379957944d897a7e28aad115596e7d2ea95cfd821225b1049`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026.json` (sha256 `91fb1c66577b718a1f8c6c3e0adfc6c20d5c906bb6248a3a012d04586565f645`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
