# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10954:9f544c20c7f55f9e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10960:fa02958b7f130d94 | -11,906.4 | -12,273.7 | -367.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10966:456be6c0d69212e2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 | 214.6 | 226.4 | 11.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22179:06fd4ca2443593c5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22185:b33d18992cb585a3 | — | — | — | — | — |
| measure_year | total | -11,691.8 | -12,047.4 | -355.6 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,912.2 | -12,277.4 | -365.2 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 5.8 | 3.7 | -2.1 | numerical | move_above_threshold |
| head | universal_credit | 214.6 | 226.4 | 11.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -11,906.4 | -12,273.7 |
| base | obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| base | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 214.6 | 226.4 |
| base | obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| base | obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |
| head | obr_pmd_nov2025:10954:9f544c20c7f55f9e (row 10954) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 403.9 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10960:fa02958b7f130d94 (row 10960) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,817.9 | -11,906.4 | -12,273.7 |
| head | obr_pmd_nov2025:10966:456be6c0d69212e2 (row 10966) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -507.3 | — | — |
| head | obr_pmd_nov2025:22173:3beb0f8e7601b1e2 (row 22173) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.0 | 214.6 | 226.4 |
| head | obr_pmd_nov2025:22179:06fd4ca2443593c5 (row 22179) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 4.9 | — | — |
| head | obr_pmd_nov2025:22185:b33d18992cb585a3 (row 22185) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 40.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `f161bb431181d172f89f0163c1b48f59880d6a6342700445b8738fb523f37f46`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027.json` (sha256 `0a62c3e517e996fcfc424807c92f1cd7710370561381112af28efe97be3429f4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
