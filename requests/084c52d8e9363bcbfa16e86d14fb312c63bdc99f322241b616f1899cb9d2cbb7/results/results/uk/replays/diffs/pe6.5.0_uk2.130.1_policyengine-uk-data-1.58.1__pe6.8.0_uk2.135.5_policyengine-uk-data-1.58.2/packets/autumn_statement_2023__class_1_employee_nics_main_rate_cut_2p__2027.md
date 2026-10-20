# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10546:fa5fffec2b5956c5 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10552:16a41c96f88267ae | -12,126.5 | -12,165.1 | -38.6 | — | — |
| source_row | obr_pmd_nov2025:10558:b4986d812dc5a6a2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10564:2063a39157d32288 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21465:6ea19652f3e3ea6b | 292.4 | 297.2 | 4.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21471:b097d213678c2035 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21477:948ae569eb8d4a91 | — | — | — | — | — |
| measure_year | total | -11,834.1 | -11,867.8 | -33.8 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | -12,132.3 | -12,170.9 | -38.5 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 5.8 | 5.8 | -0.0 | — | — |
| head | universal_credit | 292.4 | 297.2 | 4.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10546:fa5fffec2b5956c5 (row 10546) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 784.7 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10552:16a41c96f88267ae (row 10552) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,564.2 | -12,126.5 | -12,165.1 |
| base | obr_pmd_nov2025:10558:b4986d812dc5a6a2 (row 10558) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -522.4 | — | — |
| base | obr_pmd_nov2025:10564:2063a39157d32288 (row 10564) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21465:6ea19652f3e3ea6b (row 21465) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.1 | 292.4 | 297.2 |
| base | obr_pmd_nov2025:21471:b097d213678c2035 (row 21471) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 6.9 | — | — |
| base | obr_pmd_nov2025:21477:948ae569eb8d4a91 (row 21477) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 68.6 | — | — |
| head | obr_pmd_nov2025:10546:fa5fffec2b5956c5 (row 10546) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 784.7 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10552:16a41c96f88267ae (row 10552) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -9,564.2 | -12,126.5 | -12,165.1 |
| head | obr_pmd_nov2025:10558:b4986d812dc5a6a2 (row 10558) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -522.4 | — | — |
| head | obr_pmd_nov2025:10564:2063a39157d32288 (row 10564) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21465:6ea19652f3e3ea6b (row 21465) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 170.1 | 292.4 | 297.2 |
| head | obr_pmd_nov2025:21471:b097d213678c2035 (row 21471) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 6.9 | — | — |
| head | obr_pmd_nov2025:21477:948ae569eb8d4a91 (row 21477) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 68.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027.json` (sha256 `37e7a4ea1e0fa1dc526c1ffd5d79ecb7ee73308849008a27fce6a6d47cbd7bc9`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027.json` (sha256 `12ccbf831ee3f0d41659a1afb7eb69b7f27ab90702ed19b43169419eaa4eebe7`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.135.5_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
