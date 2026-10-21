# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10595:d9bbeb74fa78d25e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10601:756ded1466aa84b3 | -491.2 | -504.8 | -13.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10607:8dbf84f23026cba0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10613:3cfca8cfa0228665 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21502:1ea7fa7e0cfb40da | 42.0 | 39.7 | -2.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21508:243bee3203cd1327 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21514:95c9fc186b0b36f4 | — | — | — | — | — |
| measure_year | total | -449.2 | -465.1 | -15.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -491.2 | -504.8 | -13.6 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 42.0 | 39.7 | -2.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10595:d9bbeb74fa78d25e (row 10595) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 261.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10601:756ded1466aa84b3 (row 10601) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -378.9 | -491.2 | -504.8 |
| base | obr_pmd_nov2025:10607:8dbf84f23026cba0 (row 10607) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -290.6 | — | — |
| base | obr_pmd_nov2025:10613:3cfca8cfa0228665 (row 10613) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21502:1ea7fa7e0cfb40da (row 21502) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 42.0 | 39.7 |
| base | obr_pmd_nov2025:21508:243bee3203cd1327 (row 21508) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.8 | — | — |
| base | obr_pmd_nov2025:21514:95c9fc186b0b36f4 (row 21514) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 25.8 | — | — |
| head | obr_pmd_nov2025:10595:d9bbeb74fa78d25e (row 10595) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 261.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10601:756ded1466aa84b3 (row 10601) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -378.9 | -491.2 | -504.8 |
| head | obr_pmd_nov2025:10607:8dbf84f23026cba0 (row 10607) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -290.6 | — | — |
| head | obr_pmd_nov2025:10613:3cfca8cfa0228665 (row 10613) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21502:1ea7fa7e0cfb40da (row 21502) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 42.0 | 39.7 |
| head | obr_pmd_nov2025:21508:243bee3203cd1327 (row 21508) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.8 | — | — |
| head | obr_pmd_nov2025:21514:95c9fc186b0b36f4 (row 21514) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 25.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028.json` (sha256 `6d7377e6f401174564a6cbbeb34dcea1bc4e361e4a7772387492564e553ff25c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028.json` (sha256 `62c5d462ad0ef305c1e998d17aa5d5020b685c6dd5c24a8309fb01b858acbdbc`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
