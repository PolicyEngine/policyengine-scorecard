# Recent OBR fiscal-event replays

The inventories use the pinned populace-uk-2023 bundle definition with policyengine-uk 2.89.2. A seeded registry does not establish a completed numerical replay. Available comparisons use one source head and fiscal year per row.

Numerical comparison outputs available: 0. Registry inventories available: 5.

| Event | Replay state | Measures | Source rows | Computed rows | Computed FYs |
|---|---|---:|---:|---:|---|
| [autumn_budget_2024](autumn_budget_2024/COMPARISON.md) | Registry seeded; numerical replay incomplete | 74 | 1134 | 0 | — |
| [autumn_statement_2023](autumn_statement_2023/COMPARISON.md) | Registry seeded; numerical replay incomplete | 77 | 1116 | 0 | — |
| [spring_budget_2023](spring_budget_2023/COMPARISON.md) | Registry seeded; numerical replay incomplete | 89 | 1020 | 0 | — |
| [spring_budget_2024](spring_budget_2024/COMPARISON.md) | Registry seeded; numerical replay incomplete | 49 | 816 | 0 | — |
| [spring_statement_2025](spring_statement_2025/COMPARISON.md) | Registry seeded; numerical replay incomplete | 32 | 498 | 0 | — |

## Source inventory accounting

These amounts sum all source heads and costing years, including zero cells. They are inventory totals, not one-year event costings or numerical agreement statistics.

| Event / class | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |
|---|---:|---:|---:|---:|
| autumn_budget_2024 / expressible | 0 | 0 | 0.000 | 0.000 |
| autumn_budget_2024 / partial | 5 | 60 | 148.279 | 152.288 |
| autumn_budget_2024 / not_expressible | 43 | 438 | 42.163 | 71.094 |
| autumn_budget_2024 / out_of_household_scope | 26 | 636 | -380.606 | 477.285 |
| autumn_statement_2023 / expressible | 0 | 0 | 0.000 | 0.000 |
| autumn_statement_2023 / partial | 2 | 48 | -46.340 | 55.824 |
| autumn_statement_2023 / not_expressible | 37 | 354 | 7.094 | 31.444 |
| autumn_statement_2023 / out_of_household_scope | 38 | 714 | -67.493 | 99.223 |
| spring_budget_2023 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_budget_2023 / partial | 1 | 12 | -1.642 | 1.642 |
| spring_budget_2023 / not_expressible | 40 | 330 | -22.574 | 41.012 |
| spring_budget_2023 / out_of_household_scope | 48 | 678 | -63.834 | 83.759 |
| spring_budget_2024 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_budget_2024 / partial | 3 | 48 | -51.930 | 58.201 |
| spring_budget_2024 / not_expressible | 26 | 276 | 9.152 | 28.291 |
| spring_budget_2024 / out_of_household_scope | 20 | 492 | -1.255 | 25.416 |
| spring_statement_2025 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_statement_2025 / partial | 2 | 18 | 2.365 | 13.031 |
| spring_statement_2025 / not_expressible | 17 | 156 | 13.906 | 22.174 |
| spring_statement_2025 / out_of_household_scope | 13 | 324 | -10.696 | 39.774 |

## Agreement profile

Unavailable: no completed numerical comparison rows have been published. Registry coverage does not supply a PE/OBR agreement profile.

## Named axes and explained share

population_vintage tags every row: the fiscal event's OBR forecast differs from the certified 2023 population and its later calibration targets. behavioural_adjustment, baseline_vintage, cy_proxies_fy and head_scope describe the other construction differences. construction_scope identifies partial measures. The pipeline does not adjust the population vintage.

Pinned employer-NIC incidence assigns the wage adjustment fully to employees while holding employer cost fixed. OBR's direct per-head costings exclude separately reported macroeconomic indirect effects. This construction/head_scope difference is named, but its contribution to the raw gaps remains unsized.

National gaps and explained share are unavailable until numerical comparisons exist.

## Largest unexplained divergences

The queue below is ranked by absolute residual_plus_unsized, after any evidence-backed sized terms. It names variables and a minimal run selection for investigation. A raw gap with unsized vintage or behavioural terms does not establish a PolicyEngine model issue. Multiple years of one measure share a potential mechanism, so the queue selects one row per measure.

| Event / measure | FY / head | Residual £bn | Variables | Evidence / diagnosis | Minimal replay |
|---|---|---:|---|---|---|
| No computed divergences | — | — | — | — | — |

Evidence-backed PolicyEngine issue candidates recorded: 6. No upstream issues were filed by this replay lane.

## Measured model investigation candidates

These are engine observations reproduced separately from the national costing. Their national contribution remains unsized. The list contains only observed candidates; it is not padded to ten.

| Candidate | Class | Variables | Evidence | Minimal reproducer |
|---|---|---|---|---|
| carers_allowance_earnings_test_absent | pe_gap | carers_allowance | variables/gov/dwp/carers_allowance.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case carers_allowance_earnings_test_absent` |
| cgt_main_rate_commencement | pe_gap | capital_gains_tax | parameters/gov/hmrc/cgt/basic_rate.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case cgt_main_rate_commencement` |
| sdlt_additional_home_hike_absent | pe_gap | sdlt_on_residential_property_transactions, stamp_duty_land_tax | parameters/gov/hmrc/stamp_duty/residential/purchase/additional/rate.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case sdlt_additional_home_hike_absent` |
| private_school_vat_current_law_lever_zero | pe_gap | private_school_vat | parameters/gov/contrib/labour/private_school_vat.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case private_school_vat_current_law_lever_zero` |
| dividend_band_threshold_lag | pe_gap | dividend_income_tax, income_tax | parameters/gov/hmrc/income_tax/rates/dividends.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case dividend_band_threshold_lag` |
| class4_threshold_indexation_from_2027 | pe_gap | ni_class_4 | parameters/gov/hmrc/national_insurance/class_4/thresholds/lower_profits_limit.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case class4_threshold_indexation_from_2027` |
| uc_lcwra_protection_stops_at_2030 | investigation | uc_LCWRA_element | scenarios/uc_reform.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case uc_lcwra_protection_stops_at_2030` |
