# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10567:9abce81401b2c5e2 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10573:22a57b73322dcf42 | -557.2 | -304.8 | 252.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10579:4207dfbb96bff4bd | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10585:3790ea3f7e719e01 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21480:4e24d4d5f036370a | 6.5 | 18.1 | 11.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21486:6fefba1046222770 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21492:2331bd8e954b19b9 | — | — | — | — | — |
| measure_year | total | -550.7 | -286.8 | 263.9 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -557.2 | -304.8 | 252.3 | numerical | move_above_threshold |
| head | universal_credit | 6.5 | 18.1 | 11.6 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10567:9abce81401b2c5e2 (row 10567) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| obr_pmd_nov2025:10573:22a57b73322dcf42 (row 10573) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -325.3 | -557.2 | -304.8 |
| obr_pmd_nov2025:10579:4207dfbb96bff4bd (row 10579) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -25.9 | — | — |
| obr_pmd_nov2025:10585:3790ea3f7e719e01 (row 10585) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21480:4e24d4d5f036370a (row 21480) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 4.1 | 6.5 | 18.1 |
| obr_pmd_nov2025:21486:6fefba1046222770 (row 21486) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| obr_pmd_nov2025:21492:2331bd8e954b19b9 (row 21492) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024.json` (sha256 `e6cdaa0063a9f35fb49d064cc2c11c5df99a5260900d8a727e6dd17aa452df82`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024.json` (sha256 `9cd244681c3a28b1e8c0b6a58f0830cc4da487d1553e81c13556e6a28f667f53`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
