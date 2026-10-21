# Policy experiments: exp-pe6.10.0_uk2.143.0_on_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71

**Policy experiments on the modern population: not replays or costings of any past event.**

17 events, 71 experiment-years (model_swap). Per-event detail is in each event's FINDINGS.md.

## Anomalies

| Code | Diagnosed | Count |
|---|---|---:|
| `inert` | diagnosed | 2 |
| `magnitude_outside_10x` | diagnosed | 2 |
| `magnitude_outside_3x` | diagnosed | 4 |
| `sign_mismatch` | diagnosed | 2 |

## Mirrors

| Pair | FY | Variables | Effects (£bn) | Exact negatives |
|---|---|---|---|---|

## Modern base against the OBR's newest forecast

| Head | FY | PE base (£bn) | OBR newest (£bn) | Ratio |
|---|---|---:|---:|---:|
| IT | 2024-25 | 298.8 | 305.9 (March 2026) | 0.977 |
| IT | 2025-26 | 324.4 | 331.4 (March 2026) | 0.979 |
| IT | 2026-27 | 345.1 | 359.6 (March 2026) | 0.960 |
| NICS | 2024-25 | 172.4 | 171.4 (March 2026) | 1.006 |
| NICS | 2025-26 | 214.0 | 204.0 (March 2026) | 1.049 |
| NICS | 2026-27 | 223.2 | 211.6 (March 2026) | 1.055 |

## Against the certified pair on the same data

Same data, so each row is a model change between the engines: a fix or a bug.

| Event | Experiment | FY | Certified pair (£bn) | This model (£bn) | Change (£bn) | Diagnosis |
|---|---|---|---:|---:|---:|---|
| autumn_2010 | `as2010_high_income_child_benefit_charge` | 2024-25 | +2.282 | +2.148 | -0.134 | undiagnosed |
| autumn_2010 | `as2010_high_income_child_benefit_charge` | 2025-26 | +2.524 | +2.379 | -0.145 | undiagnosed |
| autumn_2015 | `as2015_sdlt_additional_dwellings_surcharge` | 2025-26 | +0.937 | +0.000 | -0.937 | data_issue: policyengine-uk 2.134.1 (52030637b) with microcosm#1308's property_purchases stage |
| autumn_2015 | `as2015_sdlt_additional_dwellings_surcharge` | 2026-27 | +0.968 | +0.000 | -0.968 | data_issue: policyengine-uk 2.134.1 (52030637b) with microcosm#1308's property_purchases stage |
| autumn_budget_2017 | `ab2017_sdlt_first_time_buyers_relief` | 2024-25 | -0.730 | -0.565 | +0.165 | undiagnosed |
| budget_2010_2 | `b2010_vat_standard_rate_20` | 2024-25 | +28.670 | +23.229 | -5.441 | undiagnosed |
| budget_2010_2 | `b2010_vat_standard_rate_20` | 2025-26 | +29.858 | +24.192 | -5.666 | undiagnosed |
| budget_2015 | `b2015_personal_savings_allowance` | 2024-25 | -0.458 | -0.768 | -0.310 | undiagnosed |
| budget_2015 | `b2015_personal_savings_allowance` | 2025-26 | -0.512 | -0.843 | -0.331 | undiagnosed |
