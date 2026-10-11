# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10973:fd336468dba2c601 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10979:3e84f55a7dc5bd63 | -1,263.9 | -737.5 | 526.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10985:22cea5b4798ba0ee | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22192:79bd1761809b7468 | 16.7 | 48.7 | 31.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22198:f6d029286c02e545 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22204:5467614330bcf0e5 | — | — | — | — | — |
| measure_year | total | -1,247.2 | -688.8 | 558.4 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -1,263.9 | -737.5 | 526.4 | numerical | move_above_threshold |
| head | universal_credit | 16.7 | 48.7 | 31.9 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10973:fd336468dba2c601 (row 10973) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 360.1 | 0.0 | 0.0 |
| obr_pmd_nov2025:10979:3e84f55a7dc5bd63 (row 10979) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -764.3 | -1,263.9 | -737.5 |
| obr_pmd_nov2025:10985:22cea5b4798ba0ee (row 10985) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -410.8 | — | — |
| obr_pmd_nov2025:22192:79bd1761809b7468 (row 22192) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 13.5 | 16.7 | 48.7 |
| obr_pmd_nov2025:22198:f6d029286c02e545 (row 22198) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 4.0 | — | — |
| obr_pmd_nov2025:22204:5467614330bcf0e5 (row 22204) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 36.1 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028.json` (sha256 `f0f483a5c5153c97db991f069aaa65ed78ba3d96e4b779f54ba9dbefe81aace1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028.json` (sha256 `51a4e0c9334f0c2945a26a74ea2f73a748436aec9840ac14e3381db0dbf7c134`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
