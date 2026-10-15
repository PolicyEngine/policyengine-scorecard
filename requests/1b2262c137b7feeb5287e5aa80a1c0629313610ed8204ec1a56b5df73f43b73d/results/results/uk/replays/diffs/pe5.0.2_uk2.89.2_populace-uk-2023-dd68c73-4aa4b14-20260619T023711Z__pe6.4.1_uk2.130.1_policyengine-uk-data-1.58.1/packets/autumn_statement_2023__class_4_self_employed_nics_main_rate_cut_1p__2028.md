# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10571:1975fbed36dbf276 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10577:55cd081c955ca847 | -631.3 | -390.7 | 240.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10583:57bf357507c74a9e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10589:6abb82ca2883b6cc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21484:a26658ab9b55efac | 8.3 | 24.7 | 16.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21490:d49920340fa63e2f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21496:ed49cb1a1b266067 | — | — | — | — | — |
| measure_year | total | -623.0 | -366.0 | 257.0 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -631.3 | -390.7 | 240.5 | numerical | move_above_threshold |
| head | universal_credit | 8.3 | 24.7 | 16.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10571:1975fbed36dbf276 (row 10571) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 202.8 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10577:55cd081c955ca847 (row 10577) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -363.1 | -631.3 | -390.7 |
| base | obr_pmd_nov2025:10583:57bf357507c74a9e (row 10583) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -209.4 | — | — |
| base | obr_pmd_nov2025:10589:6abb82ca2883b6cc (row 10589) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21484:a26658ab9b55efac (row 21484) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 8.3 | 24.7 |
| base | obr_pmd_nov2025:21490:d49920340fa63e2f (row 21490) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.1 | — | — |
| base | obr_pmd_nov2025:21496:ed49cb1a1b266067 (row 21496) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 19.8 | — | — |
| head | obr_pmd_nov2025:10571:1975fbed36dbf276 (row 10571) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 202.8 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10577:55cd081c955ca847 (row 10577) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -363.1 | -631.3 | -390.7 |
| head | obr_pmd_nov2025:10583:57bf357507c74a9e (row 10583) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -209.4 | — | — |
| head | obr_pmd_nov2025:10589:6abb82ca2883b6cc (row 10589) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21484:a26658ab9b55efac (row 21484) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 6.7 | 8.3 | 24.7 |
| head | obr_pmd_nov2025:21490:d49920340fa63e2f (row 21490) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 2.1 | — | — |
| head | obr_pmd_nov2025:21496:ed49cb1a1b266067 (row 21496) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 19.8 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028.json` (sha256 `77e88ce7264fe3cb33dc7380c2dfa1f1e783ad122e7b59e3037a493cdf9efec2`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028.json` (sha256 `c0cdfcfa39b4425c62549468f41a40849229fd8f814b7e387273d3cb6bdf6c42`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
