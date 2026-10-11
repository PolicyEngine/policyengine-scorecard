# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10972:7571c928a69b0431 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10978:58862ededbda2b44 | -1,215.5 | -695.7 | 519.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10984:f4db3cecac0c3af9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22191:6f3ee686a895fd60 | 16.2 | 46.3 | 30.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22197:1c94607e6780e917 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22203:bdc8349aedf6e875 | — | — | — | — | — |
| measure_year | total | -1,199.2 | -649.4 | 549.8 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -1,215.5 | -695.7 | 519.7 | numerical | move_above_threshold |
| head | universal_credit | 16.2 | 46.3 | 30.1 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10972:7571c928a69b0431 (row 10972) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 280.5 | 0.0 | 0.0 |
| obr_pmd_nov2025:10978:58862ededbda2b44 (row 10978) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -724.0 | -1,215.5 | -695.7 |
| obr_pmd_nov2025:10984:f4db3cecac0c3af9 (row 10984) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -340.4 | — | — |
| obr_pmd_nov2025:22191:6f3ee686a895fd60 (row 22191) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 12.4 | 16.2 | 46.3 |
| obr_pmd_nov2025:22197:1c94607e6780e917 (row 22197) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 3.1 | — | — |
| obr_pmd_nov2025:22203:bdc8349aedf6e875 (row 22203) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 27.8 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027.json` (sha256 `9411f83de5a260f1c00b5791bfd7d8734364a16f1e59b2a73a2a2358e4451e57`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027.json` (sha256 `579c30809dcd8eaf2c975684f328709cb65186e4216f73e8ee1f3e3c6ad2f82d`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
