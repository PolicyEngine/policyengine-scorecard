# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10567:9abce81401b2c5e2 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10573:22a57b73322dcf42 | -324.5 | -340.2 | -15.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10579:4207dfbb96bff4bd | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10585:3790ea3f7e719e01 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21480:4e24d4d5f036370a | 18.7 | 12.6 | -6.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21486:6fefba1046222770 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21492:2331bd8e954b19b9 | — | — | — | — | — |
| measure_year | total | -305.8 | -327.5 | -21.7 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -324.5 | -340.2 | -15.7 | numerical | move_above_threshold |
| head | universal_credit | 18.7 | 12.6 | -6.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10567:9abce81401b2c5e2 (row 10567) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10573:22a57b73322dcf42 (row 10573) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -325.3 | -324.5 | -340.2 |
| base | obr_pmd_nov2025:10579:4207dfbb96bff4bd (row 10579) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -25.9 | — | — |
| base | obr_pmd_nov2025:10585:3790ea3f7e719e01 (row 10585) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21480:4e24d4d5f036370a (row 21480) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 18.7 | 12.6 |
| base | obr_pmd_nov2025:21486:6fefba1046222770 (row 21486) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:21492:2331bd8e954b19b9 (row 21492) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10567:9abce81401b2c5e2 (row 10567) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10573:22a57b73322dcf42 (row 10573) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -325.3 | -324.5 | -340.2 |
| head | obr_pmd_nov2025:10579:4207dfbb96bff4bd (row 10579) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -25.9 | — | — |
| head | obr_pmd_nov2025:10585:3790ea3f7e719e01 (row 10585) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21480:4e24d4d5f036370a (row 21480) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 18.7 | 12.6 |
| head | obr_pmd_nov2025:21486:6fefba1046222770 (row 21486) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:21492:2331bd8e954b19b9 (row 21492) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024.json` (sha256 `d10e39275443d650c114d04ba16375da911e4af223eb407ddf5fdc1efb61a436`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024.json` (sha256 `12edffbc62da489a48338819765f1d3d030999053e0b23bb0c231c057786fa68`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
