# Policy experiments: autumn_statement_2022

**Policy experiment on the modern population: not a replay or a costing of Autumn Statement 2022.**

Population `exp-pe6.10.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`. OBR costings are the registry's source rows; scaling uses the November 2022 forecast (docs/uk_replay/POLICY_EXPERIMENTS.md). £bn, positive = gain to the Exchequer.

| Experiment | FY | PE | OBR mapped | OBR × scale | Scaled ratio | Anomalies |
|---|---|---:|---:|---:|---:|---|
| `as2022_additional_rate_threshold_125140` | 2024-25 | +0.853 | +0.789 | +0.851 | 1.00 | modern_law_differs (investigate; model_bug) |
| `as2022_additional_rate_threshold_125140` | 2025-26 | +0.950 | +0.765 | +0.863 | 1.10 | modern_law_differs (investigate; model_bug) |
| `as2022_additional_rate_threshold_125140` | 2026-27 | +1.122 | +0.792 | +0.906 | 1.24 |  |
| `as2022_additional_rate_threshold_125140` | 2027-28 | +1.185 | +0.843 | +0.958 | 1.24 |  |
| `as2022_benefit_cap_cpi_uprating` | 2024-25 | -0.273 | -0.243 | -0.260 | 1.05 |  |
| `as2022_benefit_cap_cpi_uprating` | 2025-26 | -0.347 | -0.254 | -0.287 | 1.21 |  |
| `as2022_benefit_cap_cpi_uprating` | 2026-27 | -0.485 | -0.254 | -0.299 | 1.62 |  |
| `as2022_benefit_cap_cpi_uprating` | 2027-28 | -0.528 | -0.264 | -0.313 | 1.68 |  |
| `as2022_cgt_annual_exempt_amount_3000` | 2024-25 | +0.834 | +0.279 | +0.370 | 2.25 |  |
| `as2022_cgt_annual_exempt_amount_3000` | 2025-26 | +0.935 | +0.423 | +0.642 | 1.46 |  |
| `as2022_cgt_annual_exempt_amount_3000` | 2026-27 | +0.966 | +0.435 | +0.672 | 1.44 |  |
| `as2022_cgt_annual_exempt_amount_3000` | 2027-28 | +0.979 | +0.440 | +0.643 | 1.52 |  |
| `as2022_dividend_allowance_500` | 2024-25 | +0.514 | +0.522 | +0.563 | 0.91 |  |
| `as2022_dividend_allowance_500` | 2025-26 | +0.535 | +0.912 | +1.028 | 0.52 |  |
| `as2022_dividend_allowance_500` | 2026-27 | +0.626 | +0.992 | +1.134 | 0.55 |  |
| `as2022_dividend_allowance_500` | 2027-28 | +0.641 | +1.094 | +1.243 | 0.52 |  |
| `as2022_employer_secondary_threshold_freeze` | 2024-25 | +3.668 | +5.313 | +5.351 | 0.69 |  |
| `as2022_employer_secondary_threshold_freeze` | 2025-26 | +0.000 | +5.323 | +6.488 | 0.00 | construction_noop (note; expected) |
| `as2022_employer_secondary_threshold_freeze` | 2026-27 | +0.000 | +5.373 | +6.604 | 0.00 | construction_noop (note; expected) |
| `as2022_employer_secondary_threshold_freeze` | 2027-28 | +0.000 | +5.744 | +7.029 | 0.00 | construction_noop (note; expected) |
| `as2022_maintain_basic_rate_20` | 2024-25 | +6.245 | +5.516 | +5.948 | 1.05 |  |
| `as2022_maintain_basic_rate_20` | 2025-26 | +6.632 | +6.223 | +7.015 | 0.95 |  |
| `as2022_maintain_basic_rate_20` | 2026-27 | +6.914 | +6.115 | +6.991 | 0.99 |  |
| `as2022_maintain_basic_rate_20` | 2027-28 | +7.122 | +6.242 | +7.097 | 1.00 |  |
| `as2022_reverse_nics_1_25pp` | 2024-25 | -16.252 | -16.209 | -16.231 | 1.00 |  |
| `as2022_reverse_nics_1_25pp` | 2025-26 | -18.157 | -16.373 | -20.096 | 0.90 |  |
| `as2022_reverse_nics_1_25pp` | 2026-27 | -18.952 | -16.746 | -20.726 | 0.91 |  |
| `as2022_reverse_nics_1_25pp` | 2027-28 | -19.624 | -17.208 | -21.218 | 0.92 |  |
| `as2022_sdlt_end_growth_plan_relief` | 2024-25 | +0.000 | +0.199 | +0.245 | 0.00 | construction_noop (note; expected) |
| `as2022_sdlt_end_growth_plan_relief` | 2025-26 | +1.367 | +0.873 | +1.005 | 1.36 |  |
| `as2022_sdlt_end_growth_plan_relief` | 2026-27 | +1.407 | +1.442 | +1.592 | 0.88 |  |
| `as2022_sdlt_end_growth_plan_relief` | 2027-28 | +1.476 | +1.631 | +1.772 | 0.83 |  |
| `as2022_sdlt_nil_rate_bands_2024` | 2024-25 | +0.000 | -1.048 | -1.288 | -0.00 | construction_noop (note; model_bug) |
| `as2022_sdlt_nil_rate_bands_2024` | 2025-26 | +0.000 | -1.198 | -1.380 | -0.00 | construction_noop (note; expected) |
| `as2022_sdlt_nil_rate_bands_2024` | 2026-27 | +0.000 | -1.442 | -1.592 | -0.00 | construction_noop (note; expected) |
| `as2022_sdlt_nil_rate_bands_2024` | 2027-28 | +0.000 | -1.631 | -1.772 | -0.00 | construction_noop (note; expected) |
