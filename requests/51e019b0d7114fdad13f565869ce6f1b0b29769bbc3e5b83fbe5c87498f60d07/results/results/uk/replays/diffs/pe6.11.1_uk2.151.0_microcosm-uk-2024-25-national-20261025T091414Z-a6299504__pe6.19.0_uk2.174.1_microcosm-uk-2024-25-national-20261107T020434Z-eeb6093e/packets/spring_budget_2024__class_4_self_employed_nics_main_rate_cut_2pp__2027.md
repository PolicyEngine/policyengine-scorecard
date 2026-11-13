# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10972:7571c928a69b0431 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10978:58862ededbda2b44 | -765.9 | -779.4 | -13.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10984:f4db3cecac0c3af9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22191:6f3ee686a895fd60 | 36.2 | 40.3 | 4.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:22197:1c94607e6780e917 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22203:bdc8349aedf6e875 | — | — | — | — | — |
| measure_year | total | -729.7 | -739.0 | -9.3 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -765.9 | -779.4 | -13.4 | numerical | move_above_threshold |
| head | universal_credit | 36.2 | 40.3 | 4.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10972:7571c928a69b0431 (row 10972) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 280.5 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10978:58862ededbda2b44 (row 10978) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -724.0 | -765.9 | -779.4 |
| base | obr_pmd_nov2025:10984:f4db3cecac0c3af9 (row 10984) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -340.4 | — | — |
| base | obr_pmd_nov2025:22191:6f3ee686a895fd60 (row 22191) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 12.4 | 36.2 | 40.3 |
| base | obr_pmd_nov2025:22197:1c94607e6780e917 (row 22197) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 3.1 | — | — |
| base | obr_pmd_nov2025:22203:bdc8349aedf6e875 (row 22203) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 27.8 | — | — |
| head | obr_pmd_nov2025:10972:7571c928a69b0431 (row 10972) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 280.5 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10978:58862ededbda2b44 (row 10978) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -724.0 | -765.9 | -779.4 |
| head | obr_pmd_nov2025:10984:f4db3cecac0c3af9 (row 10984) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -340.4 | — | — |
| head | obr_pmd_nov2025:22191:6f3ee686a895fd60 (row 22191) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 12.4 | 36.2 | 40.3 |
| head | obr_pmd_nov2025:22197:1c94607e6780e917 (row 22197) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 3.1 | — | — |
| head | obr_pmd_nov2025:22203:bdc8349aedf6e875 (row 22203) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 27.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027.json` (sha256 `cb7f70d96b5ff73ea22b4c682bd024d16e636e89e6ce848b66d5925eefa4de6e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: `results/uk/replays/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027.json` (sha256 `c000963d0a1f849a13b03ba6412768b95c35b40245a15cecc547cf44c30e6a22`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.19.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
