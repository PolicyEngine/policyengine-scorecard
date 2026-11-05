# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10544:79169e2dc0d81851 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10550:68081ae97974ee1e | -11,330.0 | -11,327.6 | 2.4 | — | — |
| source_row | obr_pmd_nov2025:10556:7fa8864402f56971 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10562:c587a7ea3d698161 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21463:fd9bc11d19465ecb | 266.2 | 198.5 | -67.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21469:e585cb5a7bf7268c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21475:d7a921363b549d4a | — | — | — | — | — |
| measure_year | total | -11,063.8 | -11,129.1 | -65.3 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -11,332.9 | -11,335.4 | -2.6 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 2.9 | 7.9 | 4.9 | numerical | move_above_threshold |
| head | universal_credit | 266.2 | 198.5 | -67.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10544:79169e2dc0d81851 (row 10544) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 606.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10550:68081ae97974ee1e (row 10550) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,182.3 | -11,330.0 | -11,327.6 |
| base | obr_pmd_nov2025:10556:7fa8864402f56971 (row 10556) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -274.9 | — | — |
| base | obr_pmd_nov2025:10562:c587a7ea3d698161 (row 10562) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21463:fd9bc11d19465ecb (row 21463) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 152.7 | 266.2 | 198.5 |
| base | obr_pmd_nov2025:21469:e585cb5a7bf7268c (row 21469) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |
| base | obr_pmd_nov2025:21475:d7a921363b549d4a (row 21475) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 44.8 | — | — |
| head | obr_pmd_nov2025:10544:79169e2dc0d81851 (row 10544) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 606.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10550:68081ae97974ee1e (row 10550) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | NICs | -9,182.3 | -11,330.0 | -11,327.6 |
| head | obr_pmd_nov2025:10556:7fa8864402f56971 (row 10556) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Corporation tax (onshore) | -274.9 | — | — |
| head | obr_pmd_nov2025:10562:c587a7ea3d698161 (row 10562) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21463:fd9bc11d19465ecb (row 21463) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | 152.7 | 266.2 | 198.5 |
| head | obr_pmd_nov2025:21469:e585cb5a7bf7268c (row 21469) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |
| head | obr_pmd_nov2025:21475:d7a921363b549d4a (row 21475) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 44.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025.json` (sha256 `28001f896f734c45c4f077192a36fc97ee98d3b546e43962b696e2f316c2bb3a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025.json` (sha256 `c945aa032e299296485543daa96d9fe6d075e3ecb4163ac54545a44352adcea1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
