# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10546:fa5fffec2b5956c5 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10552:16a41c96f88267ae | -12,356.2 | -12,255.2 | 101.0 | — | — |
| source_row | obr_pmd_nov2025:10558:b4986d812dc5a6a2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10564:2063a39157d32288 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21465:6ea19652f3e3ea6b | 109.3 | 282.4 | 173.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21471:b097d213678c2035 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21477:948ae569eb8d4a91 | — | — | — | — | — |
| measure_year | total | -12,246.8 | -11,972.8 | 274.1 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,359.5 | -12,260.6 | 98.9 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 3.4 | 5.4 | 2.1 | numerical | move_above_threshold |
| head | universal_credit | 109.3 | 282.4 | 173.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:10546:fa5fffec2b5956c5 (row 10546) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 784.7 | 0.0 | 0.0 |
| obr_pmd_nov2025:10552:16a41c96f88267ae (row 10552) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,564.2 | -12,356.2 | -12,255.2 |
| obr_pmd_nov2025:10558:b4986d812dc5a6a2 (row 10558) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -522.4 | — | — |
| obr_pmd_nov2025:10564:2063a39157d32288 (row 10564) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| obr_pmd_nov2025:21465:6ea19652f3e3ea6b (row 21465) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.1 | 109.3 | 282.4 |
| obr_pmd_nov2025:21471:b097d213678c2035 (row 21471) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 6.9 | — | — |
| obr_pmd_nov2025:21477:948ae569eb8d4a91 (row 21477) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 68.6 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027.json` (sha256 `43cccd2c18558b0e1435a358079c4f1be63db7295b8037a270e1a967731ff7dd`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027.json` (sha256 `e0da57532336675cdfb4df05ecdcf9f223f15f714bc0672a76e3635d8409b3db`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
