# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10570:382153d580cbbacf | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10576:033898ebb4865f78 | -384.2 | -382.0 | 2.2 | — | — |
| source_row | obr_pmd_nov2025:10582:7799d90753f7ec23 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10588:d3ebd197a534d4d4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21483:8913a74a278eaeb2 | 16.6 | 17.9 | 1.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21489:e467d4010f8ef77b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21495:ee2885d02bcd90f9 | — | — | — | — | — |
| measure_year | total | -367.6 | -364.1 | 3.5 | — | — |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -384.2 | -382.0 | 2.2 | — | — |
| head | universal_credit | 16.6 | 17.9 | 1.3 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10570:382153d580cbbacf (row 10570) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 161.1 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10576:033898ebb4865f78 (row 10576) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -342.5 | -384.2 | -382.0 |
| base | obr_pmd_nov2025:10582:7799d90753f7ec23 (row 10582) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -172.9 | — | — |
| base | obr_pmd_nov2025:10588:d3ebd197a534d4d4 (row 10588) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21483:8913a74a278eaeb2 (row 21483) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 16.6 | 17.9 |
| base | obr_pmd_nov2025:21489:e467d4010f8ef77b (row 21489) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 1.7 | — | — |
| base | obr_pmd_nov2025:21495:ee2885d02bcd90f9 (row 21495) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 15.5 | — | — |
| head | obr_pmd_nov2025:10570:382153d580cbbacf (row 10570) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 161.1 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10576:033898ebb4865f78 (row 10576) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -342.5 | -384.2 | -382.0 |
| head | obr_pmd_nov2025:10582:7799d90753f7ec23 (row 10582) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -172.9 | — | — |
| head | obr_pmd_nov2025:10588:d3ebd197a534d4d4 (row 10588) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21483:8913a74a278eaeb2 (row 21483) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 6.2 | 16.6 | 17.9 |
| head | obr_pmd_nov2025:21489:e467d4010f8ef77b (row 21489) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 1.7 | — | — |
| head | obr_pmd_nov2025:21495:ee2885d02bcd90f9 (row 21495) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 15.5 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027.json` (sha256 `352803a8d80fd44f3218b036e3b424ec26787afc42e2a9efd9fdc6fe944ac4f8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027.json` (sha256 `acbed8e921ebea2ac491d701572d6cfb09b47235f0ae93289ddf182ed934140f`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
