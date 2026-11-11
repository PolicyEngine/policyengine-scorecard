# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10569:9c1e6218a8238dfd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10575:e617707f9625fbba | -360.1 | -370.0 | -9.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10581:97f735b5b05863e9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10587:5f3c7d488533b903 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21482:753c71d52bde5307 | 16.5 | 17.8 | 1.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21488:9444f449b920b74b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21494:c20e55b607e6fc79 | — | — | — | — | — |
| measure_year | total | -343.5 | -352.2 | -8.7 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -360.1 | -370.0 | -9.9 | numerical | move_above_threshold |
| head | universal_credit | 16.5 | 17.8 | 1.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10569:9c1e6218a8238dfd (row 10569) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 114.3 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10575:e617707f9625fbba (row 10575) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -330.1 | -360.1 | -370.0 |
| base | obr_pmd_nov2025:10581:97f735b5b05863e9 (row 10581) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -132.2 | — | — |
| base | obr_pmd_nov2025:10587:5f3c7d488533b903 (row 10587) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21482:753c71d52bde5307 (row 21482) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 16.5 | 17.8 |
| base | obr_pmd_nov2025:21488:9444f449b920b74b (row 21488) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.2 | — | — |
| base | obr_pmd_nov2025:21494:c20e55b607e6fc79 (row 21494) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 10.6 | — | — |
| head | obr_pmd_nov2025:10569:9c1e6218a8238dfd (row 10569) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 114.3 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10575:e617707f9625fbba (row 10575) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -330.1 | -360.1 | -370.0 |
| head | obr_pmd_nov2025:10581:97f735b5b05863e9 (row 10581) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -132.2 | — | — |
| head | obr_pmd_nov2025:10587:5f3c7d488533b903 (row 10587) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21482:753c71d52bde5307 (row 21482) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 16.5 | 17.8 |
| head | obr_pmd_nov2025:21488:9444f449b920b74b (row 21488) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.2 | — | — |
| head | obr_pmd_nov2025:21494:c20e55b607e6fc79 (row 21494) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 10.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026.json` (sha256 `1db37e6f55ac5f9cbb672ce841c2f8f561b53d44156450316f6b789e0d862900`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026.json` (sha256 `d3aeab7e58c99c6503194775b458c0265aec2738e62accf285d49adb16e7c460`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
