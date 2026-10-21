# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10569:9c1e6218a8238dfd | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:10575:e617707f9625fbba | -348.3 | -360.3 | -11.9 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:10581:97f735b5b05863e9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10587:5f3c7d488533b903 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21482:753c71d52bde5307 | 22.0 | 21.3 | -0.7 | — | — |
| source_row | obr_pmd_nov2025:21488:9444f449b920b74b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21494:c20e55b607e6fc79 | — | — | — | — | — |
| measure_year | total | -326.3 | -338.9 | -12.6 | numerical | move_above_threshold |
| head | income_tax | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_2 | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | -348.3 | -360.3 | -11.9 | numerical | move_above_threshold |
| head | universal_credit | 22.0 | 21.3 | -0.7 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10569:9c1e6218a8238dfd (row 10569) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 114.3 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:10575:e617707f9625fbba (row 10575) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -330.1 | -348.3 | -360.3 |
| base | obr_pmd_nov2025:10581:97f735b5b05863e9 (row 10581) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -132.2 | — | — |
| base | obr_pmd_nov2025:10587:5f3c7d488533b903 (row 10587) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21482:753c71d52bde5307 (row 21482) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 22.0 | 21.3 |
| base | obr_pmd_nov2025:21488:9444f449b920b74b (row 21488) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.2 | — | — |
| base | obr_pmd_nov2025:21494:c20e55b607e6fc79 (row 21494) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 10.6 | — | — |
| head | obr_pmd_nov2025:10569:9c1e6218a8238dfd (row 10569) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 114.3 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:10575:e617707f9625fbba (row 10575) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | -330.1 | -348.3 | -360.3 |
| head | obr_pmd_nov2025:10581:97f735b5b05863e9 (row 10581) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -132.2 | — | — |
| head | obr_pmd_nov2025:10587:5f3c7d488533b903 (row 10587) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21482:753c71d52bde5307 (row 21482) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | 6.1 | 22.0 | 21.3 |
| head | obr_pmd_nov2025:21488:9444f449b920b74b (row 21488) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 1.2 | — | — |
| head | obr_pmd_nov2025:21494:c20e55b607e6fc79 (row 21494) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 10.6 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026.json` (sha256 `9df7ba1126c77a793d50267e4aa05cf5fffd615f048027b6f0d0686312ef08ce`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026.json` (sha256 `96817a53a9ba7482579ed824331783f1ad579209596c6f44bd8651c3854914ec`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.12_policyengine-uk-data-1.59.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
