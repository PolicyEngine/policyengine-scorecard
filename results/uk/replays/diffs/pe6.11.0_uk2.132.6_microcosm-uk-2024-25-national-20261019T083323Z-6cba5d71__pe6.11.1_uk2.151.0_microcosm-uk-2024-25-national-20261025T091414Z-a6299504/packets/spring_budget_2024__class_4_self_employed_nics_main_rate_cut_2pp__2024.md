# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10969:8dde405208f86bbd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10975:497e18b9ba827fa3 | -680.4 | -678.5 | 1.9 | — | — |
| source_row | obr_pmd_nov2025:10981:ee23395fc58c2e94 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22188:9f98363a90ba075c | 25.3 | 26.8 | 1.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22194:376f5e7bc1c25928 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22200:454271d3e97ec8eb | — | — | — | — | — |
| measure_year | total | -655.1 | -651.7 | 3.4 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -680.4 | -678.5 | 1.9 | — | — |
| head | universal_credit | 25.3 | 26.8 | 1.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10969:8dde405208f86bbd (row 10969) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10975:497e18b9ba827fa3 (row 10975) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -666.5 | -680.4 | -678.5 |
| base | obr_pmd_nov2025:10981:ee23395fc58c2e94 (row 10981) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -51.8 | — | — |
| base | obr_pmd_nov2025:22188:9f98363a90ba075c (row 22188) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 8.3 | 25.3 | 26.8 |
| base | obr_pmd_nov2025:22194:376f5e7bc1c25928 (row 22194) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22200:454271d3e97ec8eb (row 22200) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10969:8dde405208f86bbd (row 10969) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10975:497e18b9ba827fa3 (row 10975) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -666.5 | -680.4 | -678.5 |
| head | obr_pmd_nov2025:10981:ee23395fc58c2e94 (row 10981) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -51.8 | — | — |
| head | obr_pmd_nov2025:22188:9f98363a90ba075c (row 22188) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 8.3 | 25.3 | 26.8 |
| head | obr_pmd_nov2025:22194:376f5e7bc1c25928 (row 22194) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22200:454271d3e97ec8eb (row 22200) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024.json` (sha256 `fad25631d0885856e65fac5bd7fa048b0ec8cf3c5e6e2c282f83db2faa3ae99d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024.json` (sha256 `5520ecd8627e84693f883f4a33d82c452b950c20a0abe4186aa7f6a8b066276e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
