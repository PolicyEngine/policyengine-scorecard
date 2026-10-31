# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10543:a1f1338aee24ceda | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10549:7322b894d39fa3ec | -10,656.0 | -10,469.2 | 186.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10555:6e52d779b70c2afe | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10561:0142012d49059613 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21462:c775903b43caf723 | 181.4 | 163.0 | -18.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21468:3a8f7c4777a80257 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21474:9cbc966cf0e74bd1 | — | — | — | — | — |
| measure_year | total | -10,474.5 | -10,306.2 | 168.3 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -10,662.6 | -10,474.8 | 187.8 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 6.6 | 5.6 | -1.0 | numerical | move_above_threshold |
| head | universal_credit | 181.4 | 163.0 | -18.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10543:a1f1338aee24ceda (row 10543) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 369.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10549:7322b894d39fa3ec (row 10549) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,128.9 | -10,656.0 | -10,469.2 |
| base | obr_pmd_nov2025:10555:6e52d779b70c2afe (row 10555) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -102.4 | — | — |
| base | obr_pmd_nov2025:10561:0142012d49059613 (row 10561) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21462:c775903b43caf723 (row 21462) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.3 | 181.4 | 163.0 |
| base | obr_pmd_nov2025:21468:3a8f7c4777a80257 (row 21468) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 2.0 | — | — |
| base | obr_pmd_nov2025:21474:9cbc966cf0e74bd1 (row 21474) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 26.5 | — | — |
| head | obr_pmd_nov2025:10543:a1f1338aee24ceda (row 10543) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 369.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10549:7322b894d39fa3ec (row 10549) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -9,128.9 | -10,656.0 | -10,469.2 |
| head | obr_pmd_nov2025:10555:6e52d779b70c2afe (row 10555) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -102.4 | — | — |
| head | obr_pmd_nov2025:10561:0142012d49059613 (row 10561) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21462:c775903b43caf723 (row 21462) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 116.3 | 181.4 | 163.0 |
| head | obr_pmd_nov2025:21468:3a8f7c4777a80257 (row 21468) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 2.0 | — | — |
| head | obr_pmd_nov2025:21474:9cbc966cf0e74bd1 (row 21474) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 26.5 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024.json` (sha256 `4e33524df390f327e89e4047138ba7604929859cd0942380b55cceb49d857aa7`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024.json` (sha256 `9148c707120b8aabee2779952c0c9e1348865d282c2a177f6e4ba6a2f812222a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
