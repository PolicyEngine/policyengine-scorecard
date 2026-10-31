# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10594:eac703aa1cd0c605 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10600:d0828a5bfb537ca4 | -502.7 | -493.4 | 9.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10606:464a49f34a9b5964 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10612:6f1e9a3bd0d656c3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21501:53e1c92d4a4f4e96 | 33.7 | 34.8 | 1.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21507:2c2538b49423c207 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21513:7aa3f5c32491b748 | — | — | — | — | — |
| measure_year | total | -469.0 | -458.6 | 10.4 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -502.7 | -493.4 | 9.3 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 33.7 | 34.8 | 1.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10594:eac703aa1cd0c605 (row 10594) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 206.5 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10600:d0828a5bfb537ca4 (row 10600) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -368.7 | -502.7 | -493.4 |
| base | obr_pmd_nov2025:10606:464a49f34a9b5964 (row 10606) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -242.1 | — | — |
| base | obr_pmd_nov2025:10612:6f1e9a3bd0d656c3 (row 10612) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21501:53e1c92d4a4f4e96 (row 21501) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 33.7 | 34.8 |
| base | obr_pmd_nov2025:21507:2c2538b49423c207 (row 21507) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 2.2 | — | — |
| base | obr_pmd_nov2025:21513:7aa3f5c32491b748 (row 21513) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 20.1 | — | — |
| head | obr_pmd_nov2025:10594:eac703aa1cd0c605 (row 10594) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 206.5 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10600:d0828a5bfb537ca4 (row 10600) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -368.7 | -502.7 | -493.4 |
| head | obr_pmd_nov2025:10606:464a49f34a9b5964 (row 10606) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -242.1 | — | — |
| head | obr_pmd_nov2025:10612:6f1e9a3bd0d656c3 (row 10612) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21501:53e1c92d4a4f4e96 (row 21501) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 33.7 | 34.8 |
| head | obr_pmd_nov2025:21507:2c2538b49423c207 (row 21507) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 2.2 | — | — |
| head | obr_pmd_nov2025:21513:7aa3f5c32491b748 (row 21513) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 20.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027.json` (sha256 `f29469df05c5221b1e7d0b0d46c4aeb9209fe620423a035adb860ab3032d1dd4`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027.json` (sha256 `6f1617951b942629174b37c432caa98128b2c602f4ec80b5919b4a33504ea1aa`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
