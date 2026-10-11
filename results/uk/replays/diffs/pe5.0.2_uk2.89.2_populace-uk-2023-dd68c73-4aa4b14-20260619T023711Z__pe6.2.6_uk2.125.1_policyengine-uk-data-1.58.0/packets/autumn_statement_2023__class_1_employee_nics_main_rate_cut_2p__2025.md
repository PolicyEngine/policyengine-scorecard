# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10544:79169e2dc0d81851 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10550:68081ae97974ee1e | -11,685.8 | -11,458.8 | 227.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10556:7fa8864402f56971 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10562:c587a7ea3d698161 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21463:fd9bc11d19465ecb | 94.2 | 268.4 | 174.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21469:e585cb5a7bf7268c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21475:d7a921363b549d4a | — | — | — | — | — |
| measure_year | total | -11,591.5 | -11,190.4 | 401.1 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,689.4 | -11,461.4 | 228.0 | numerical | move_above_threshold |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.7 | 2.7 | -1.0 | numerical | move_above_threshold |
| head | universal_credit | 94.2 | 268.4 | 174.1 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10544:79169e2dc0d81851 (row 10544) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 606.8 | 0.0 | 0.0 |
| obr_pmd_nov2025:10550:68081ae97974ee1e (row 10550) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,182.3 | -11,685.8 | -11,458.8 |
| obr_pmd_nov2025:10556:7fa8864402f56971 (row 10556) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -274.9 | — | — |
| obr_pmd_nov2025:10562:c587a7ea3d698161 (row 10562) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21463:fd9bc11d19465ecb (row 21463) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 152.7 | 94.2 | 268.4 |
| obr_pmd_nov2025:21469:e585cb5a7bf7268c (row 21469) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |
| obr_pmd_nov2025:21475:d7a921363b549d4a (row 21475) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 44.8 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025.json` (sha256 `1b7002908a8df14628b82d035c4eed72c16c06aba530b5e3ad841da25b01826e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025.json` (sha256 `62d215f59525ef06708086f637faf8ba48892078398db6118e9603851c74ec3b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
