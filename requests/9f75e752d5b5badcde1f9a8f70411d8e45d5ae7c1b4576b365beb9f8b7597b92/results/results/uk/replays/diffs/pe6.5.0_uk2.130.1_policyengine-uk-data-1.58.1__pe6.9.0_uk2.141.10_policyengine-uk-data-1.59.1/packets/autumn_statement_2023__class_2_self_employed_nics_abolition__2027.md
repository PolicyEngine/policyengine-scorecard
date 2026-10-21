# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_2_self_employed_nics_abolition / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10594:eac703aa1cd0c605 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10600:d0828a5bfb537ca4 | -474.1 | -487.1 | -13.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10606:464a49f34a9b5964 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10612:6f1e9a3bd0d656c3 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21501:53e1c92d4a4f4e96 | 41.8 | 39.9 | -1.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21507:2c2538b49423c207 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21513:7aa3f5c32491b748 | — | — | — | — | — |
| measure_year | total | -432.3 | -447.2 | -14.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | -474.1 | -487.1 | -13.0 | numerical | move_above_threshold |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | 41.8 | 39.9 | -1.9 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10594:eac703aa1cd0c605 (row 10594) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 206.5 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10600:d0828a5bfb537ca4 (row 10600) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -368.7 | -474.1 | -487.1 |
| base | obr_pmd_nov2025:10606:464a49f34a9b5964 (row 10606) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -242.1 | — | — |
| base | obr_pmd_nov2025:10612:6f1e9a3bd0d656c3 (row 10612) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21501:53e1c92d4a4f4e96 (row 21501) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 41.8 | 39.9 |
| base | obr_pmd_nov2025:21507:2c2538b49423c207 (row 21507) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 2.2 | — | — |
| base | obr_pmd_nov2025:21513:7aa3f5c32491b748 (row 21513) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 20.1 | — | — |
| head | obr_pmd_nov2025:10594:eac703aa1cd0c605 (row 10594) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 206.5 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10600:d0828a5bfb537ca4 (row 10600) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -368.7 | -474.1 | -487.1 |
| head | obr_pmd_nov2025:10606:464a49f34a9b5964 (row 10606) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -242.1 | — | — |
| head | obr_pmd_nov2025:10612:6f1e9a3bd0d656c3 (row 10612) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21501:53e1c92d4a4f4e96 (row 21501) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 41.8 | 39.9 |
| head | obr_pmd_nov2025:21507:2c2538b49423c207 (row 21507) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 2.2 | — | — |
| head | obr_pmd_nov2025:21513:7aa3f5c32491b748 (row 21513) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 20.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027.json` (sha256 `888ab1d6486aacbc8817f0e5b4093f018d4403a91542b2e69bdafd2dea0742b1`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027.json` (sha256 `8cd6be22350218b9f680c6deec09753579b7de651684c27e10a40cf70c3032da`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_2.flat_rate": {"2024-01-01.2035-12-31": 3.7}, "gov.hmrc.national_insurance.class_2.small_profits_threshold": {"2024-01-01.2035-12-31": 12570}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.10_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2027
```

## Sources the registry cites

* base: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html
* head: https://www.gov.uk/government/publications/autumn-statement-2023/autumn-statement-2023-html

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
