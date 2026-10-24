# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10969:8dde405208f86bbd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10975:497e18b9ba827fa3 | -649.6 | -645.8 | 3.8 | — | — |
| source_row | obr_pmd_nov2025:10981:ee23395fc58c2e94 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22188:9f98363a90ba075c | 37.4 | 35.7 | -1.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22194:376f5e7bc1c25928 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22200:454271d3e97ec8eb | — | — | — | — | — |
| measure_year | total | -612.2 | -610.0 | 2.2 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -649.6 | -645.8 | 3.8 | — | — |
| head | universal_credit | 37.4 | 35.7 | -1.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10969:8dde405208f86bbd (row 10969) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10975:497e18b9ba827fa3 (row 10975) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -666.5 | -649.6 | -645.8 |
| base | obr_pmd_nov2025:10981:ee23395fc58c2e94 (row 10981) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -51.8 | — | — |
| base | obr_pmd_nov2025:22188:9f98363a90ba075c (row 22188) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 8.3 | 37.4 | 35.7 |
| base | obr_pmd_nov2025:22194:376f5e7bc1c25928 (row 22194) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22200:454271d3e97ec8eb (row 22200) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10969:8dde405208f86bbd (row 10969) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Income tax | 0.0 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10975:497e18b9ba827fa3 (row 10975) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | NICs | -666.5 | -649.6 | -645.8 |
| head | obr_pmd_nov2025:10981:ee23395fc58c2e94 (row 10981) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Corporation tax (onshore) | -51.8 | — | — |
| head | obr_pmd_nov2025:22188:9f98363a90ba075c (row 22188) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | 8.3 | 37.4 | 35.7 |
| head | obr_pmd_nov2025:22194:376f5e7bc1c25928 (row 22194) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22200:454271d3e97ec8eb (row 22200) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024.json` (sha256 `fcf6f1905f1fecbf539c6d0e35d88859a32679920fb08246614c12e396d7adda`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024.json` (sha256 `35f0c1886e062ba71061ae53ebbdae29959e1dc0bef457d57c6b51d40f4e06e8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
