# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10570:382153d580cbbacf | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10576:033898ebb4865f78 | -607.0 | -347.6 | 259.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10582:7799d90753f7ec23 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10588:d3ebd197a534d4d4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21483:8913a74a278eaeb2 | 8.1 | 22.8 | 14.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21489:e467d4010f8ef77b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21495:ee2885d02bcd90f9 | — | — | — | — | — |
| measure_year | total | -598.9 | -324.8 | 274.1 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -607.0 | -347.6 | 259.4 | numerical | move_above_threshold |
| head | universal_credit | 8.1 | 22.8 | 14.7 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10570:382153d580cbbacf (row 10570) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 161.1 | 0.0 | 0.0 |
| obr_pmd_nov2025:10576:033898ebb4865f78 (row 10576) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -342.5 | -607.0 | -347.6 |
| obr_pmd_nov2025:10582:7799d90753f7ec23 (row 10582) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -172.9 | — | — |
| obr_pmd_nov2025:10588:d3ebd197a534d4d4 (row 10588) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21483:8913a74a278eaeb2 (row 21483) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 8.1 | 22.8 |
| obr_pmd_nov2025:21489:e467d4010f8ef77b (row 21489) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 1.7 | — | — |
| obr_pmd_nov2025:21495:ee2885d02bcd90f9 (row 21495) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 15.5 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027.json` (sha256 `1a4597a82e81eecff0e706144f8692cd966a0f45db3ced397708799c09e458ba`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027.json` (sha256 `7f3b2c92e4bee9388de33a32f5e7fc9d541e2e414f162cef10d0baabeec7da7f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
