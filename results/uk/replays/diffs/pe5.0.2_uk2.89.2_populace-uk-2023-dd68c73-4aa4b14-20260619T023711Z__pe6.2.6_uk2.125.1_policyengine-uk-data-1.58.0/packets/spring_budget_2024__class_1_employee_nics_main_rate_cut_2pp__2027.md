# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10954:9f544c20c7f55f9e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10960:fa02958b7f130d94 | -12,356.2 | -12,255.2 | 101.0 | — | — |
| source_row | obr_pmd_nov2025:10966:456be6c0d69212e2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 | 109.3 | 282.4 | 173.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22179:06fd4ca2443593c5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22185:b33d18992cb585a3 | — | — | — | — | — |
| measure_year | total | -12,246.8 | -11,972.8 | 274.1 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,359.5 | -12,260.6 | 98.9 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.4 | 5.4 | 2.1 | numerical | move_above_threshold |
| head | universal_credit | 109.3 | 282.4 | 173.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -12,356.2 | -12,255.2 |
| obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 109.3 | 282.4 |
| obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `7acb2c151eae5c0d7127a833cb6926bb651a988f280715cd79942af8e5202e41`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `b7ed3b6da2553c1dfa8e2500d0bd493e85f49f548e4f09d8e891583d7d76eb49`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
