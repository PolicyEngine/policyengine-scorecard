# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10543:a1f1338aee24ceda | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10549:7322b894d39fa3ec | -11,082.5 | -10,762.0 | 320.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10555:6e52d779b70c2afe | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10561:0142012d49059613 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21462:c775903b43caf723 | 86.2 | 243.2 | 157.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21468:3a8f7c4777a80257 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21474:9cbc966cf0e74bd1 | — | — | — | — | — |
| measure_year | total | -10,996.3 | -10,518.8 | 477.5 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,086.5 | -10,764.5 | 322.0 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.9 | 2.5 | -1.5 | numerical | move_above_threshold |
| head | universal_credit | 86.2 | 243.2 | 157.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10543:a1f1338aee24ceda (row 10543) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 369.0 | 0.0 | 0.0 |
| obr_pmd_nov2025:10549:7322b894d39fa3ec (row 10549) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,128.9 | -11,082.5 | -10,762.0 |
| obr_pmd_nov2025:10555:6e52d779b70c2afe (row 10555) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -102.4 | — | — |
| obr_pmd_nov2025:10561:0142012d49059613 (row 10561) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21462:c775903b43caf723 (row 21462) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.3 | 86.2 | 243.2 |
| obr_pmd_nov2025:21468:3a8f7c4777a80257 (row 21468) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 2.0 | — | — |
| obr_pmd_nov2025:21474:9cbc966cf0e74bd1 (row 21474) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 26.5 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024.json` (sha256 `b15ef6c90af1f05eeb520544c767230f66c6778d908d4412ddfb2d2b7872526f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024.json` (sha256 `f8fc9ad0f42f299bb61bb8865d7f167e2339b6c7deb8802275a917d47f0aa8ad`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
