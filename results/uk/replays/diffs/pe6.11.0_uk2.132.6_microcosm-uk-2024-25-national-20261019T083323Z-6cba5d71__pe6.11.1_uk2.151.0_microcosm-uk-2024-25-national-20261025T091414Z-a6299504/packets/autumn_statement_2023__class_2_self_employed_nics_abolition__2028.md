# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10595:d9bbeb74fa78d25e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10601:756ded1466aa84b3 | -521.7 | -507.6 | 14.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10607:8dbf84f23026cba0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10613:3cfca8cfa0228665 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21502:1ea7fa7e0cfb40da | 34.6 | 35.0 | 0.4 | — | — |
| source_row | obr_pmd_nov2025:21508:243bee3203cd1327 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21514:95c9fc186b0b36f4 | — | — | — | — | — |
| measure_year | total | -487.1 | -472.6 | 14.5 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -521.7 | -507.6 | 14.1 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 34.6 | 35.0 | 0.4 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10595:d9bbeb74fa78d25e (row 10595) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 261.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10601:756ded1466aa84b3 (row 10601) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -378.9 | -521.7 | -507.6 |
| base | obr_pmd_nov2025:10607:8dbf84f23026cba0 (row 10607) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -290.6 | — | — |
| base | obr_pmd_nov2025:10613:3cfca8cfa0228665 (row 10613) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21502:1ea7fa7e0cfb40da (row 21502) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 34.6 | 35.0 |
| base | obr_pmd_nov2025:21508:243bee3203cd1327 (row 21508) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.8 | — | — |
| base | obr_pmd_nov2025:21514:95c9fc186b0b36f4 (row 21514) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 25.8 | — | — |
| head | obr_pmd_nov2025:10595:d9bbeb74fa78d25e (row 10595) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 261.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10601:756ded1466aa84b3 (row 10601) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -378.9 | -521.7 | -507.6 |
| head | obr_pmd_nov2025:10607:8dbf84f23026cba0 (row 10607) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -290.6 | — | — |
| head | obr_pmd_nov2025:10613:3cfca8cfa0228665 (row 10613) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21502:1ea7fa7e0cfb40da (row 21502) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 34.6 | 35.0 |
| head | obr_pmd_nov2025:21508:243bee3203cd1327 (row 21508) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.8 | — | — |
| head | obr_pmd_nov2025:21514:95c9fc186b0b36f4 (row 21514) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 25.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028.json` (sha256 `18a20dcad0a0cb5637e6997e59555c2a3f9d27735811a52217ba851917993cf4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028.json` (sha256 `61c4dc1e675e290a842da1a3d8f2e884cf3995deb385ab3478eeeaac98611a90`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
