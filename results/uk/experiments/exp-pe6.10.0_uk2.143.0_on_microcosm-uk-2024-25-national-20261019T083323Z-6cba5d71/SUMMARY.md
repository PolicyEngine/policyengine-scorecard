# Policy experiments: exp-pe6.10.0_uk2.143.0_on_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71

**Policy experiments on the modern population: not replays or costings of any past event.**

7 events, 74 experiment-years (model_swap). Per-event detail is in each event's FINDINGS.md.

## Anomalies

| Code | Diagnosed | Count |
|---|---|---:|
| `construction_noop` | diagnosed | 7 |
| `inert` | diagnosed | 2 |
| `magnitude_outside_3x` | diagnosed | 2 |

## Mirrors

| Pair | FY | Variables | Effects (£bn) | Exact negatives |
|---|---|---|---|---|
| `autumn_budget_2021:ab2021_hscl_nics_plus_1_25pp` / `autumn_statement_2022:as2022_reverse_nics_1_25pp` | 2024-25 | `income_tax` | -3.199 / +3.199 | yes |
| `autumn_budget_2021:ab2021_hscl_nics_plus_1_25pp` / `autumn_statement_2022:as2022_reverse_nics_1_25pp` | 2024-25 | `ni_class_1_employee+ni_class_1_employer+ni_class_2+ni_class_4` | +19.666 / -19.666 | yes |
| `autumn_budget_2021:ab2021_hscl_nics_plus_1_25pp` / `autumn_statement_2022:as2022_reverse_nics_1_25pp` | 2025-26 | `income_tax` | -3.814 / +3.814 | yes |
| `autumn_budget_2021:ab2021_hscl_nics_plus_1_25pp` / `autumn_statement_2022:as2022_reverse_nics_1_25pp` | 2025-26 | `ni_class_1_employee+ni_class_1_employer+ni_class_2+ni_class_4` | +22.256 / -22.256 | yes |
| `autumn_budget_2021:ab2021_hscl_nics_plus_1_25pp` / `autumn_statement_2022:as2022_reverse_nics_1_25pp` | 2026-27 | `income_tax` | -4.050 / +4.050 | yes |
| `autumn_budget_2021:ab2021_hscl_nics_plus_1_25pp` / `autumn_statement_2022:as2022_reverse_nics_1_25pp` | 2026-27 | `ni_class_1_employee+ni_class_1_employer+ni_class_2+ni_class_4` | +23.327 / -23.327 | yes |
| `autumn_statement_2022:as2022_maintain_basic_rate_20` / `spring_statement_2022:ss2022_basic_rate_19` | 2024-25 | `income_tax` | +6.343 / -6.343 | yes |
| `autumn_statement_2022:as2022_maintain_basic_rate_20` / `spring_statement_2022:ss2022_basic_rate_19` | 2025-26 | `income_tax` | +6.739 / -6.739 | yes |
| `autumn_statement_2022:as2022_maintain_basic_rate_20` / `spring_statement_2022:ss2022_basic_rate_19` | 2026-27 | `income_tax` | +7.032 / -7.032 | yes |

## Modern base against the OBR's newest forecast

| Head | FY | PE base (£bn) | OBR newest (£bn) | Ratio |
|---|---|---:|---:|---:|
| CGT | 2024-25 | 23.1 | 13.7 (March 2026) | 1.691 |
| CGT | 2025-26 | 27.3 | 21.8 (March 2026) | 1.252 |
| CGT | 2026-27 | 29.0 | 20.8 (March 2026) | 1.396 |
| CGT | 2027-28 | 30.1 | 25.5 (March 2026) | 1.183 |
| IT | 2024-25 | 298.8 | 305.9 (March 2026) | 0.977 |
| IT | 2025-26 | 324.4 | 331.4 (March 2026) | 0.979 |
| IT | 2026-27 | 345.1 | 359.6 (March 2026) | 0.960 |
| IT | 2027-28 | 361.9 | 384.6 (March 2026) | 0.941 |
| NICS | 2024-25 | 172.4 | 171.4 (March 2026) | 1.006 |
| NICS | 2025-26 | 214.0 | 204.0 (March 2026) | 1.049 |
| NICS | 2026-27 | 223.2 | 211.6 (March 2026) | 1.055 |
| NICS | 2027-28 | 230.3 | 218.9 (March 2026) | 1.052 |

## Against the certified pair on the same data

Same data, so each row is a model change between the engines: a fix or a bug.

| Event | Experiment | FY | Certified pair (£bn) | This model (£bn) | Change (£bn) | Diagnosis |
|---|---|---|---:|---:|---:|---|
| autumn_2015 | `as2015_sdlt_additional_dwellings_surcharge` | 2025-26 | +0.937 | +0.000 | -0.937 | data_issue: policyengine-uk 2.134.1 (52030637b) with microcosm#1308's property_purchases stage |
| autumn_2015 | `as2015_sdlt_additional_dwellings_surcharge` | 2026-27 | +0.968 | +0.000 | -0.968 | data_issue: policyengine-uk 2.134.1 (52030637b) with microcosm#1308's property_purchases stage |
| autumn_statement_2022 | `as2022_additional_rate_threshold_125140` | 2024-25 | +0.853 | +0.959 | +0.106 | model_bug: policyengine-uk 2.139.4 (83de1ef1d, 'Correct historical dividend income tax band thresholds') |
| autumn_statement_2022 | `as2022_additional_rate_threshold_125140` | 2025-26 | +0.950 | +1.071 | +0.121 | model_bug: policyengine-uk 2.139.4 (83de1ef1d, 'Correct historical dividend income tax band thresholds') |
| autumn_statement_2022 | `as2022_sdlt_nil_rate_bands_2024` | 2024-25 | +0.000 | -1.234 | -1.234 | model_bug: policyengine-uk 2.141.8 (4044d6ccf, 'Fix recent residential SDLT purchase schedules and inclusive first-buyer caps') |
