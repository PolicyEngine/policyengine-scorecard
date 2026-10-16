# Investigation packet: spring_budget_2024 / spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10950:cfbd201bdcc71ff6 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10956:fe78e076cc7bb65b | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10962:1552bf784a1d7a0a | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22169:cfddc3a6fdeecca3 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:22175:c61213e1325dab69 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22181:84f54c5d1c2eee0c | — | — | — | — | — |
| measure_year | total | 0.0 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10950:cfbd201bdcc71ff6 (row 10950) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10956:fe78e076cc7bb65b (row 10956) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10962:1552bf784a1d7a0a (row 10962) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| base | obr_pmd_nov2025:22169:cfddc3a6fdeecca3 (row 22169) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:22175:c61213e1325dab69 (row 22175) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22181:84f54c5d1c2eee0c (row 22181) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10950:cfbd201bdcc71ff6 (row 10950) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10956:fe78e076cc7bb65b (row 10956) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10962:1552bf784a1d7a0a (row 10962) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:22169:cfddc3a6fdeecca3 (row 22169) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:22175:c61213e1325dab69 (row 22175) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22181:84f54c5d1c2eee0c (row 22181) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2023.json` (sha256 `48e728eff7dc0d687b3ec260bde21419305c4b34092eb3b25d4535d2efb63686`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2023
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
