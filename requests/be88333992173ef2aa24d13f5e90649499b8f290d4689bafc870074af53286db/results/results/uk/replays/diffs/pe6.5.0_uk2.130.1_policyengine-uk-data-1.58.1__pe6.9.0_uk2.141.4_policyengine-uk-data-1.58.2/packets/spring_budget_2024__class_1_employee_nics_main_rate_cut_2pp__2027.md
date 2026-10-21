# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10954:9f544c20c7f55f9e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10960:fa02958b7f130d94 | -12,126.5 | -12,165.1 | -38.6 | — | — |
| source_row | obr_pmd_nov2025:10966:456be6c0d69212e2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 | 292.4 | 297.1 | 4.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22179:06fd4ca2443593c5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22185:b33d18992cb585a3 | — | — | — | — | — |
| measure_year | total | -11,834.1 | -11,868.0 | -33.9 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,132.3 | -12,170.9 | -38.5 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 5.8 | 5.8 | -0.0 | — | — |
| head | universal_credit | 292.4 | 297.1 | 4.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -12,126.5 | -12,165.1 |
| base | obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| base | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 292.4 | 297.1 |
| base | obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| base | obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |
| head | obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -12,126.5 | -12,165.1 |
| head | obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| head | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 292.4 | 297.1 |
| head | obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| head | obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `170ae022774de2180df274148611944a6c968914ea7e079eb5db93c103da538c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `6d98f64bfcd77c3c7748aa47ffc6694c699c8130a445fb888df0a04430c2111e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.4_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
