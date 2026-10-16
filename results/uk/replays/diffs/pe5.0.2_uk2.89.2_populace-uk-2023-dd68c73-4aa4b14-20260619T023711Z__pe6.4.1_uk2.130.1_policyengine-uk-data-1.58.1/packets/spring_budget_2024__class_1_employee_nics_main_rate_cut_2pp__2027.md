# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10954:9f544c20c7f55f9e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10960:fa02958b7f130d94 | -12,356.2 | -12,126.5 | 229.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10966:456be6c0d69212e2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 | 109.3 | 292.4 | 183.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22179:06fd4ca2443593c5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22185:b33d18992cb585a3 | — | — | — | — | — |
| measure_year | total | -12,246.8 | -11,834.1 | 412.8 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,359.5 | -12,132.3 | 227.2 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.4 | 5.8 | 2.4 | numerical | move_above_threshold |
| head | universal_credit | 109.3 | 292.4 | 183.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -12,356.2 | -12,126.5 |
| base | obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| base | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 109.3 | 292.4 |
| base | obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| base | obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |
| head | obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -12,356.2 | -12,126.5 |
| head | obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| head | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 109.3 | 292.4 |
| head | obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| head | obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `7acb2c151eae5c0d7127a833cb6926bb651a988f280715cd79942af8e5202e41`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `c5ee77718c2f2d8c11b65a43bbccda4bd4d4ea2b539c9b3e2f9ddf264fec3a3b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
