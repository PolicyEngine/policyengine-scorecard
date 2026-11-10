# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10973:fd336468dba2c601 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10979:3e84f55a7dc5bd63 | -810.9 | -821.6 | -10.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10985:22cea5b4798ba0ee | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22192:79bd1761809b7468 | 37.2 | 43.5 | 6.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22198:f6d029286c02e545 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22204:5467614330bcf0e5 | — | — | — | — | — |
| measure_year | total | -773.7 | -778.1 | -4.4 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -810.9 | -821.6 | -10.8 | numerical | move_above_threshold |
| head | universal_credit | 37.2 | 43.5 | 6.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10973:fd336468dba2c601 (row 10973) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 360.1 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10979:3e84f55a7dc5bd63 (row 10979) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -764.3 | -810.9 | -821.6 |
| base | obr_pmd_nov2025:10985:22cea5b4798ba0ee (row 10985) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -410.8 | — | — |
| base | obr_pmd_nov2025:22192:79bd1761809b7468 (row 22192) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 13.5 | 37.2 | 43.5 |
| base | obr_pmd_nov2025:22198:f6d029286c02e545 (row 22198) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 4.0 | — | — |
| base | obr_pmd_nov2025:22204:5467614330bcf0e5 (row 22204) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 36.1 | — | — |
| head | obr_pmd_nov2025:10973:fd336468dba2c601 (row 10973) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 360.1 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10979:3e84f55a7dc5bd63 (row 10979) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | -764.3 | -810.9 | -821.6 |
| head | obr_pmd_nov2025:10985:22cea5b4798ba0ee (row 10985) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -410.8 | — | — |
| head | obr_pmd_nov2025:22192:79bd1761809b7468 (row 22192) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | 13.5 | 37.2 | 43.5 |
| head | obr_pmd_nov2025:22198:f6d029286c02e545 (row 22198) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 4.0 | — | — |
| head | obr_pmd_nov2025:22204:5467614330bcf0e5 (row 22204) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 36.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028.json` (sha256 `a161ad9e0958a4f768ce01fe9213c6151dde0708329e9e12195e5b72c1bcc155`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028.json` (sha256 `904491b74a0d231076de13b407db0311cdd46eacdcd04f3237ee2c77ad0e33c9`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
