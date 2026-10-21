# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10571:1975fbed36dbf276 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10577:55cd081c955ca847 | -390.7 | -403.3 | -12.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10583:57bf357507c74a9e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10589:6abb82ca2883b6cc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21484:a26658ab9b55efac | 24.7 | 23.6 | -1.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21490:d49920340fa63e2f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21496:ed49cb1a1b266067 | — | — | — | — | — |
| measure_year | total | -366.0 | -379.7 | -13.8 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -390.7 | -403.3 | -12.6 | numerical | move_above_threshold |
| head | universal_credit | 24.7 | 23.6 | -1.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10571:1975fbed36dbf276 (row 10571) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 202.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10577:55cd081c955ca847 (row 10577) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -363.1 | -390.7 | -403.3 |
| base | obr_pmd_nov2025:10583:57bf357507c74a9e (row 10583) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -209.4 | — | — |
| base | obr_pmd_nov2025:10589:6abb82ca2883b6cc (row 10589) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21484:a26658ab9b55efac (row 21484) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 24.7 | 23.6 |
| base | obr_pmd_nov2025:21490:d49920340fa63e2f (row 21490) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.1 | — | — |
| base | obr_pmd_nov2025:21496:ed49cb1a1b266067 (row 21496) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 19.8 | — | — |
| head | obr_pmd_nov2025:10571:1975fbed36dbf276 (row 10571) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 202.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10577:55cd081c955ca847 (row 10577) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -363.1 | -390.7 | -403.3 |
| head | obr_pmd_nov2025:10583:57bf357507c74a9e (row 10583) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -209.4 | — | — |
| head | obr_pmd_nov2025:10589:6abb82ca2883b6cc (row 10589) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21484:a26658ab9b55efac (row 21484) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 24.7 | 23.6 |
| head | obr_pmd_nov2025:21490:d49920340fa63e2f (row 21490) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.1 | — | — |
| head | obr_pmd_nov2025:21496:ed49cb1a1b266067 (row 21496) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 19.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028.json` (sha256 `0ee07d2d75bb21c6e58eb1b124dd718e2f39993cef737f0445135fb5899c13f7`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028.json` (sha256 `f1e3962965b92725fbe1b045714a07e61311e82e8f59974fd574b484c03393df`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
